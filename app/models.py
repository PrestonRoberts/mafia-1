from app import db, login
from flask_login import UserMixin


@login.user_loader
def load_player(id):
    return player.query.get(int(id))


class player(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    role = db.Column(db.String(64))
    isDead = db.Column(db.Boolean)
    actionToPlayer = db.Column(db.Integer)
    voteYes = db.Column(db.Integer)
    isHost = db.Column(db.Boolean)
    roomID = db.Column(db.Integer)
    voteCount = db.Column(db.Integer)
    selfHeal = db.Column(db.Boolean)

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'isDead': self.isDead,
            'voteCount': self.voteCount,
            'voteYes': self.voteYes,
            'actionToPlayer': self.actionToPlayer,
            'selfHeal': self.selfHeal
        }

    def __repr__(self):
        return '<User: {}>'.format(self.username)


class game_room(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playerCount = db.Column(db.Integer)
    isActive = db.Column(db.Boolean)
    code = db.Column(db.String(4))
    day = db.Column(db.Integer)
    phase = db.Column(db.String(64))
    votedPlayer = db.Column(db.Integer)
    timerStart = db.Column(db.DateTime)
    timerEnd = db.Column(db.DateTime)
    timer = db.Column(db.Boolean)
    yay = db.Column(db.Integer)
    nay = db.Column(db.Integer)
    isMafia = db.Column(db.Integer)
    attackTarget = db.Column(db.Integer)
    gaTarget = db.Column(db.Integer)

    def serialize(self):
        return {
            'day': self.day,
            'phase': self.phase,
            'timer': self.timer,
            'votedPlayer': self.votedPlayer,
            'yay': self.yay,
            'nay': self.nay,
            'isMafia': self.isMafia,
            'attackTarget': self.attackTarget,
            'gaTarget': self.gaTarget
        }

    def __repr__(self):
        return '<Room: {}>'.format(self.code)
