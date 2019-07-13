from flask import render_template, flash, redirect, url_for, jsonify, request
from app import app, db
from app.forms import RoomForm, JoinByCodeForm
from app.models import player, game_room
from flask_login import current_user, login_user
import string
import random
import math
import datetime


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/')
def index():
    return render_template('index.html', title='Home')


@app.route('/rules')
def rules():
    return render_template('rules.html', title='Rules')


@app.route('/create_room', methods=['GET', 'POST'])
def create_room():
    form = RoomForm()
    if form.validate_on_submit():
        allowable = string.ascii_uppercase
        if len(form.name.data) > 8:
            flash("Name must be shorter than 8 characters")
            return render_template('create_room.html', form=form, title='Create Room')
        for x in range(len(form.name.data)):
            if form.name.data[x].upper() not in allowable:
                flash("Name must only contain english characters")
                return render_template('create_room.html', form=form, title='Create Room')
        size = 4
        # Check to see if code exists
        while True:
            code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))
            rooms_with_code = game_room.query.filter_by(code=code).all()
            if not rooms_with_code:
                break
        cr = game_room(playerCount=1, isActive=False, code=code, day=0, phase="Intro", timer=False, votedPlayer=-1,
                       isMafia=-1)
        db.session.add(cr)
        db.session.commit()
        this_room = game_room.query.filter_by(code=code).first()

        new_player = player(username=form.name.data, roomID=this_room.id, isHost=True, isDead=False, actionToPlayer=-1,
                            voteCount=0, voteYes=-1, selfHeal=False)
        db.session.add(new_player)
        db.session.commit()

        curr = player.query.filter_by(roomID=this_room.id, username=form.name.data).first()
        curr.isHost = True
        db.session.commit()
        login_user(curr, True)
        return redirect(url_for("room_game", code=code))
    return render_template('create_room.html', title='Create Room', form=form)


@app.route('/join_room', methods=['GET', 'POST'])
def join_room():
    form = JoinByCodeForm()
    if form.validate_on_submit():
        input_code = form.code.data.upper()
        room = game_room.query.filter_by(code=input_code).first()
        if room is None:
            flash("Room does not exist")
            return render_template('join_room.html', form=form, title='Join Room')
        if room.isActive:
            flash("Game is in progress")
            return render_template('join_room.html', form=form, title='Join Room')
        copy = player.query.filter_by(roomID=room.id).all()
        if room.playerCount >= 12:
            flash("Room is full")
            return render_template('join_room.html', form=form, title='Join Room')
        if len(form.name.data) > 8:
            flash("Name must be shorter than 8 characters")
            return render_template('join_room.html', form=form, title='Join Room')
        for x in range(len(form.name.data)):
            allowable = string.ascii_uppercase
            if form.name.data[x].upper() not in allowable:
                flash("Name must only contain english characters")
                return render_template('join_room.html', form=form, title='Create Room')
        for player1 in copy:
            if player1.username.lower() == form.name.data.lower():
                flash("Name already in use")
                return render_template('join_room.html', form=form, title='Join Room')
        player2 = player(username=form.name.data, roomID=room.id, isHost=False, isDead=False, actionToPlayer=-1,
                         voteCount=0, voteYes=-1, selfHeal=False)
        db.session.add(player2)
        db.session.commit()
        curr = player.query.filter_by(roomID=room.id, username=form.name.data).first()
        room.playerCount += 1
        curr.isHost = False
        db.session.commit()
        login_user(curr, True)
        return redirect(url_for('room_game', code=room.code))
    return render_template('join_room.html', title="Join Room", form=form)


@app.route('/<code>', methods=['GET', 'POST'])
def room_game(code):
    player_list = []
    if current_user.is_authenticated:
        user = player.query.filter_by(id=current_user.id).first()
        game = game_room.query.filter_by(code=code).first()
        if user and game:
            if game.id != user.roomID:
                flash("Can Not Join Room by Link")
                return redirect(url_for("index"))
        else:
            return redirect(url_for("index"))
        if game:
            if game.playerCount >= 12:
                flash("Room is full")
                return redirect(url_for("index"))
            current_user.roomID = game.id
            db.session.commit()
            players_in_game = player.query.filter_by(roomID=game.id).all()
            for p in players_in_game:
                player_list.append(p)
            game.playerCount = len(player_list)
            db.session.commit()
            return render_template('game_room.html', player_list=player_list, title=code, room=game,
                                   current_user=current_user)
    flash("Can Not Join Room by Link")
    return redirect(url_for("index"))


@app.route('/_game_loop')
def game_loop():
    game = game_room.query.filter_by(id=current_user.roomID).first()
    all_players = player.query.filter_by(roomID=game.id).all()
    user = current_user
    town_question = 0
    if game:
        # Phase Change
        if game.timer:
            if (game.timerEnd - datetime.datetime.now()).total_seconds() <= 0:
                game.timer = False
                if game.phase == "Intro":
                    game.phase = "Night"
                    game.day += 1
                    game.attackTarget = -1
                    game.gaTarget = -1

                elif game.phase == "Night":
                    for p in all_players:
                        if p.role == "detective":
                            target = player.query.filter_by(id=p.actionToPlayer).first()
                            if target:
                                if target.role == "mafia":
                                    game.isMafia = 1
                                else:
                                    game.isMafia = 0
                        elif p.role == "guardian_angel":
                            target = player.query.filter_by(id=p.actionToPlayer).first()
                            if target:
                                game.gaTarget = target.id
                                if target == p:
                                    p.selfHeal = True
                        elif p.role == "mafia":
                            mafia_count = 0
                            target = player.query.filter_by(id=p.actionToPlayer).first()
                            for x in all_players:
                                if not x.isDead and x.role == "mafia":
                                    mafia_count += 1
                            majority = int(math.floor(mafia_count / 2)) + 1
                            for x in all_players:
                                if x.voteCount >= majority:
                                    target = player.query.filter_by(id=x.id).first()
                                    db.session.commit()
                                    break
                            p.voteCount = 0
                            p.actionToPlayer = -1
                            if target:
                                game.attackTarget = target.id
                    game.phase = "Talking"

                elif game.phase == "Talking":
                    for p in all_players:
                        p.actionToPlayer = -1
                        p.voteCount = 0
                    game.phase = "Voting"
                    game.isMafia = -1
                    game.attackTarget = -1
                    game.gaTarget = -1

                elif game.phase == "Voting":
                    random.randint(0, 1)
                    alive = 0
                    for p in all_players:
                        if not p.isDead:
                            alive += 1
                    majority = int(math.floor(alive / 2)) + 1
                    game.phase = "Night"
                    for p in all_players:
                        if p.voteCount >= majority:
                            game.votedPlayer = p.id
                            game.phase = "Defense"
                            db.session.commit()
                            break
                    for p in all_players:
                        p.voteCount = 0
                        p.actionToPlayer = -1
                    game.day += 1

                elif game.phase == "Defense":
                    game.phase = "Verdict"

                elif game.phase == "Verdict":
                    yay = 0
                    nay = 0
                    for p in all_players:
                        if p.voteYes == 0:
                            nay += 1
                        elif p.voteYes == 1:
                            yay += 1
                        p.voteYes = -1
                    game.yay = yay
                    game.nay = nay

                    if yay > nay:
                        new_dead = player.query.filter_by(id=game.votedPlayer).first()
                        new_dead.isDead = True
                    game.phase = "Decision"

                elif game.phase == "Decision":
                    random.randint(0, 1)
                    game.phase = "Night"
                    game.day += 1

        # Timer Set
        if game.phase == "Intro":
            if not game.timer:
                game.timerStart = datetime.datetime.now()
                game.timerEnd = datetime.datetime.now() + datetime.timedelta(seconds=10)
                game.timer = True

        elif game.phase == "Night":
            if not game.timer:
                game.timerStart = datetime.datetime.now()
                game.timerEnd = datetime.datetime.now() + datetime.timedelta(seconds=30)
                game.timer = True

        elif game.phase == "Talking":
            if not game.timer:
                game.timerStart = datetime.datetime.now()
                game.timerEnd = datetime.datetime.now() + datetime.timedelta(seconds=60)
                game.timer = True

        elif game.phase == "Voting":
            if not game.timer:
                game.timerStart = datetime.datetime.now()
                game.timerEnd = datetime.datetime.now() + datetime.timedelta(seconds=20)
                game.timer = True

        elif game.phase == "Defense":
            if not game.timer:
                game.timerStart = datetime.datetime.now()
                game.timerEnd = datetime.datetime.now() + datetime.timedelta(seconds=30)
                game.timer = True

        elif game.phase == "Verdict":
            if not game.timer:
                game.timerStart = datetime.datetime.now()
                game.timerEnd = datetime.datetime.now() + datetime.timedelta(seconds=15)
                game.timer = True

        elif game.phase == "Decision":
            if not game.timer:
                game.timerStart = datetime.datetime.now()
                game.timerEnd = datetime.datetime.now() + datetime.timedelta(seconds=5)
                game.timer = True

        # Variables to Send
        if game.timer:
            time = int(round((game.timerEnd - datetime.datetime.now()).total_seconds()))
        else:
            time = 10
        db.session.commit()
        return jsonify(game=game.serialize(), timer=time, players=[p.serialize() for p in all_players],
                       user=user.serialize(), town_question=town_question)


@app.route('/_death')
def death():
    game = game_room.query.filter_by(id=current_user.roomID).first()
    target = player.query.filter_by(id=game.attackTarget).first()
    if target:
        if not game.attackTarget == game.gaTarget:
            target.isDead = True
            db.session.commit()
    return jsonify(game=game.serialize())


@app.route('/_vote')
def vote():
    target = request.args.get('target', "")
    game = game_room.query.filter_by(id=current_user.roomID).first()
    player_target = player.query.filter_by(roomID=game.id, username=target).first()
    user = current_user.id
    current_player = player.query.filter_by(id=user).first()
    if game:
        if current_player.actionToPlayer != -1:
            old_target = player.query.filter_by(id=current_player.actionToPlayer).first()
            if game.phase == "Voting" or current_player.role == "mafia":
                old_target.voteCount -= 1
                db.session.commit()
            if current_player.actionToPlayer != player_target.id:
                current_player.actionToPlayer = player_target.id
                if game.phase == "Voting" or current_player.role == "mafia":
                    player_target.voteCount += 1
                    db.session.commit()
            else:
                current_player.actionToPlayer = -1
                db.session.commit()
        else:
            current_player.actionToPlayer = player_target.id
            if game.phase == "Voting" or current_player.role == "mafia":
                player_target.voteCount += 1
        db.session.commit()
    return 'ok'


@app.route('/_verdict')
def verdict():
    vote = request.args.get('vote', "")
    game = game_room.query.filter_by(id=current_user.roomID).first()
    user = current_user.id
    current_player = player.query.filter_by(id=user).first()
    if game:
        if vote == 'yes':
            current_player.voteYes = 1
        else:
            current_player.voteYes = 0
        db.session.commit()
    return 'ok'


@app.route('/_update')
def update():
    player_list = []
    game = game_room.query.filter_by(id=current_user.roomID).first()
    user = current_user.id
    if game:
        started = game.isActive
        players_in_game = player.query.filter_by(roomID=game.id).all()
        for p in players_in_game:
            player_list.append(p)
        game.playerCount = len(player_list)
        return jsonify(players=[p.serialize() for p in player_list], started=started, name=current_user.username,
                       user=user, role=current_user.role)


@app.route('/_start_game')
def start_game():
    game = game_room.query.filter_by(id=current_user.roomID).first()
    if game:
        player_count = game.playerCount
        mafia = 0
        guardian_angel = 0
        detective = 0
        if player_count < 4:
            return jsonify(started=game.isActive)

        game.isActive = True

        if player_count == 4:
            mafia = 1
            guardian_angel = 1
            detective = 1

        if player_count == 5:
            mafia = 1
            guardian_angel = 1
            detective = 1

        if player_count == 6:
            mafia = 2
            guardian_angel = 1
            detective = 1

        if player_count == 7:
            mafia = 2
            guardian_angel = 1
            detective = 1

        if player_count == 8:
            mafia = 2
            guardian_angel = 1
            detective = 1

        if player_count == 9:
            mafia = 2
            guardian_angel = 1
            detective = 1

        if player_count == 10:
            mafia = 2
            guardian_angel = 1
            detective = 1

        if player_count == 11:
            mafia = 3
            guardian_angel = 1
            detective = 1

        if player_count == 12:
            mafia = 3
            guardian_angel = 1
            detective = 1

        players_in_game = player.query.filter_by(roomID=game.id).all()

        player_list = []
        while len(player_list) < player_count:
            random_num = random.randint(0, player_count-1)
            if players_in_game[random_num] not in player_list:
                player_list.append(players_in_game[random_num])

        idx = 0
        while idx < player_count:
            if mafia > 0:
                player_list[idx].role = "mafia"
                mafia -= 1
                idx += 1
            elif guardian_angel > 0:
                player_list[idx].role = "guardian_angel"
                guardian_angel -= 1
                idx += 1
            elif detective > 0:
                player_list[idx].role = "detective"
                detective -= 1
                idx += 1
            else:
                player_list[idx].role = "town"
                idx += 1
        db.session.commit()
        return jsonify(started=True)
    return 'ok'


@app.route('/reset_db')
def reset_db():
    flash("Resetting database: deleting old data and repopulating with dummy data")
    # clear all data from all tables
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table {}'.format(table))
        db.session.execute(table.delete())
    db.session.commit()
    return render_template('index.html', title='Home')
