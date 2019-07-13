var isStarted = false;
var game1;

var town_questions = [
    "Who do you think is a member of the mafia?",
    "Who do you think is a member of the town?"];

function start_game(){
    $.getJSON($SCRIPT_ROOT + '/_start_game', {
    }, function (data) {
        if (data.started) {
            document.getElementById('start').style.display = 'none';
            document.getElementById("start").style.height = "0px";
            document.getElementById("enough").style.display = 'none';
        }else{
            document.getElementById("enough").style.display = 'block';
        }
    });
    return 0;
}

const start_button = document.getElementById("start");
if (start_button){
    start_button.addEventListener("click", start_game);
}

function vote(e){
    $.getJSON($SCRIPT_ROOT + '/_vote', {
        target: e
    }, function (data) {

    });
}

document.getElementById("yes").onclick = function verdict(){
    $.getJSON($SCRIPT_ROOT + '/_verdict', {
        vote: "yes"
    }, function (data) {

    });
    return 0;
};

document.getElementById("no").onclick = function verdict(){
    $.getJSON($SCRIPT_ROOT + '/_verdict', {
        vote: "no"
    }, function (data) {

    });
    return 0;
};

function endGame(winner, role, players){
    clearInterval(game1);
    document.getElementById("button-list").style.display = "none";

    if(winner === "mafia"){
        $('#day-info').html("Mafia Have Won");
    }
    else{
        $('#day-info').html("Town Have Won");
    }

    $('#winners').html("Winners: ");
    $('#losers').html("Losers: ");
    document.getElementById('losers').style.display = "block";

    let toAddWinners = "";
    let toAddLosers ="";

    for(let i=0; i<players.length; i++){
        let id = players[i].username;
        document.getElementById(id).style.display = "none";
        if(winner === "mafia") {
            if (players[i].role === "mafia") {
                if(players[i].isDead){
                    toAddWinners += '<div class="dead-player">' + players[i].username + '</div>';
                }
                else {
                    toAddWinners += '<div class="user">' + players[i].username + '</div>';
                }
            }
            else{
                if(players[i].isDead){
                    toAddLosers += '<div class="dead-player">' + players[i].username + '</div>';
                }
                else{
                    toAddLosers += '<div class="user">' + players[i].username + '</div>';
                }
            }
        }
        else{
            if (players[i].role === "mafia") {
                if(players[i].isDead){
                    toAddLosers += '<div class="dead-player">' + players[i].username + '</div>';
                }
                else {
                    toAddLosers += '<div class="user">' + players[i].username + '</div>';
                }
            }
            else{
                if(players[i].isDead){
                    toAddWinners += '<div class="dead-player">' + players[i].username + '</div>';
                }
                else {
                    toAddWinners += '<div class="user">' + players[i].username + '</div>';
                }
            }
        }
    }

    $('#player-list').html(toAddWinners);
    $('#player-list-2').html(toAddLosers);
    document.getElementById('player-list-2').style.display ="block";

    document.getElementById('previous-info').style.display = "none";
    document.getElementById('voting-info').style.display = "none";
    document.getElementById('phase-info').style.display = "none";
    document.getElementById('timer').style.display = "none";

    if(winner === "mafia") {
        if (role === "mafia") {
            $('#game-header').html("You Won");
        }
        else {
            $('#game-header').html("You Lost");
        }
    }
    else{
        if (role === "mafia") {
            $('#game-header').html("You Lost");
        }
        else {
            $('#game-header').html("You Won");
        }
    }
}

function game_loop(){

    $.getJSON($SCRIPT_ROOT + '/_game_loop', {
    }, function (data) {

        $('#game-info').html("");

        $('#timer').html(data.timer);
        document.getElementById('game-info').style.display = "none";
        document.getElementById('title').style.display = "none";

        let toAdd = '';

        if(data.game.phase !== "Talking"){
            if(data.user.isDead){
                $('#previous-info').html("You Are Dead");
            }else{
                $('#previous-info').html('');
            }
        }

        //Phases
        if(data.game.phase === "Talking"){

            $('#day-info').html("Day " + data.game.day);
            $('#phase-info').html("Talking");
            document.getElementById('phase-info').style.display = "block";

            for(let i=0; i<data.players.length; i++){
                let id = data.players[i].username;
                document.getElementById(id).style.visibility = "hidden";
                if(data.players[i].isDead){
                    toAdd += '<div class="dead-player">' + data.players[i].username + '</div>';
                }
                else{
                    toAdd += '<div class="user">' + data.players[i].username + '</div>';
                }
            }
            $('#player-list').html(toAdd);

            for(let i=0; i<data.players.length; i++) {
                let id = data.players[i].username;
                document.getElementById(id).style.visibility = "hidden";
            }

            $.getJSON($SCRIPT_ROOT + '/_death', {
            }, function (data) {
            });

            if(data.user.isDead){
                $('#previous-info').html("You Are Dead");
            }

            //Previous Text
            else if(data.user.role === "detective"){
                if(data.game.isMafia === -1){
                    $('#previous-info').html("you didn't perform your action");
                }
                else if(data.game.isMafia === 0){
                    for(let i=0; i<data.players.length; i++) {
                        if (data.players[i].id === data.user.actionToPlayer) {
                            $('#previous-info').html(data.players[i].username +
                                " is not a member of the mafia");
                        }
                    }
                }
                else if(data.game.isMafia === 1){
                    for(let i=0; i<data.players.length; i++) {
                        if (data.players[i].id === data.user.actionToPlayer) {
                            $('#previous-info').html(data.players[i].username +
                                " is a member of the mafia");
                        }
                    }
                }
            }
            else if(data.user.role === "mafia"){
                setTimeout(500);
                var isdead = false;
                for(let i=0; i<data.players.length; i++) {
                    if(data.players[i].id === data.game.attackTarget && data.players[i].isDead) {
                            isdead = true;
                    }
                }
                if(data.game.attackTarget === -1){
                    $('#previous-info').html("you didn't perform your action");
                }
                else if(isdead){
                    for(let i=0; i<data.players.length; i++) {
                        if(data.players[i].id === data.game.attackTarget) {
                            $('#previous-info').html("you killed " + data.players[i].username);
                        }
                    }
                }
                else if(!isdead){
                    for(let i=0; i<data.players.length; i++) {
                        if(data.players[i].id === data.game.attackTarget) {
                            $('#previous-info').html("you attacked " + data.players[i].username +
                                ", but they survived");
                        }
                    }
                }
            }
            else if(data.user.role === "guardian_angel"){
                if(data.game.gaTarget === -1){
                    $('#previous-info').html("you didn't perform your action");
                }
                else if(data.game.gaTarget === data.game.attackTarget){
                    for(let i=0; i<data.players.length; i++) {
                        if(data.players[i].id === data.game.attackTarget){
                            if(data.players[i].id === data.user.id){
                                $('#previous-info').html("You were attacked, and you " +
                                    "saved yourself");
                            }
                            else{
                                $('#previous-info').html(data.players[i].username + " was attacked, and you " +
                                    "saved them");
                            }
                        }
                    }
                }
                else{
                    for(let i=0; i<data.players.length; i++) {
                        if (data.players[i].id === data.user.actionToPlayer) {
                            if(data.players[i].id === data.user.id) {
                                $('#previous-info').html("Nothing happened to you");
                            }
                            else {
                                $('#previous-info').html("Nothing happened to " + data.players[i].username);
                            }
                        }
                    }
                }
            }
        }

        //Setup Selections
        else if(data.game.phase === "Night"){
            $('#day-info').html("Night " + data.game.day);

            if(data.user.isDead){
                $('#phase-info').html("Night Time");
                document.getElementById('phase-info').style.display = "block";
            }
            else{
                $('#phase-info').html("Perform Your Action");
                document.getElementById('phase-info').style.display = "block";
            }

            for(let i=0; i<data.players.length; i++){
                let id = data.players[i].username;
                document.getElementById(id).style.visibility = "hidden";
                if(data.players[i].isDead){
                    toAdd += '<div class="dead-player">' + data.players[i].username + '</div>';
                }
                else{
                    if(data.user.actionToPlayer === data.players[i].id){
                        if(data.user.role === "mafia"){
                            toAdd += '<div class="voted-player">' + data.players[i].username + ' ' + data.players[i].voteCount +
                            '</div>'
                        }
                        else {
                            toAdd += '<div class="voted-player">' + data.players[i].username + '</div>';
                        }
                    }
                    else {
                        if(data.user.role === "mafia"){
                            toAdd += '<div class="user">' + data.players[i].username + ' ' + data.players[i].voteCount +
                            '</div>'
                        }
                        else {
                            toAdd += '<div class="user">' + data.players[i].username + '</div>';
                        }
                    }
                }

                if(data.user.role === "detective" && !data.user.isDead){
                    if(!data.players[i].isDead){
                        if(data.players[i].id !== data.user.id) {
                            let id = data.players[i].username;
                            document.getElementById(id).style.visibility = "visible";
                        }
                    }
                }

                else if(data.user.role === "mafia" && !data.user.isDead){
                    if(!data.players[i].isDead && data.players[i].role !== "mafia"){
                        if(data.players[i].id !== data.user.id) {
                            let id = data.players[i].username;
                            document.getElementById(id).style.visibility = "visible";
                        }
                    }

                }

                else if(data.user.role === "guardian_angel" && !data.user.isDead){
                    if(!data.players[i].isDead){
                        if(data.players[i].id === data.user.id){
                            if(!data.user.selfHeal){
                                let id = data.players[i].username;
                                document.getElementById(id).style.visibility = "visible";
                            }
                        }
                        else {
                            let id = data.players[i].username;
                            document.getElementById(id).style.visibility = "visible";
                        }
                    }
                }
                else if(data.user.role === "town" && !data.user.isDead) {
                    if (!data.players[i].isDead) {
                        if (data.players[i].id !== data.user.id) {
                            let id = data.players[i].username;
                            document.getElementById(id).style.visibility = "visible";
                        }
                        $('#phase-info').html(town_questions[data.town_question]);
                        document.getElementById('phase-info').style.display = "block";
                    }
                }
            }
            $('#player-list').html(toAdd);
        }

        // Setup selections
        else if(data.game.phase === "Voting"){
            $('#day-info').html("Day " + data.game.day);
            $('#phase-info').html("Voting");
            document.getElementById('phase-info').style.display = "block";
            let toAdd = '';
            for(let i=0; i<data.players.length; i++){
                if(data.players[i].isDead){
                        toAdd += '<div class="dead-player">' + data.players[i].username + '</div>';
                }
                else if(data.players[i].id === data.user.id){
                    toAdd += '<div class="user">' + data.players[i].username + ' ' + data.players[i].voteCount +
                        '</div>';
                    document.getElementById(data.players[i].username).style.visibility = "hidden";
                }
                else{
                    if(data.user.actionToPlayer === data.players[i].id){
                        toAdd += '<div class="voted-player">' + data.players[i].username + ' ' + data.players[i].voteCount +
                            '</div>';
                    }
                    else{
                        toAdd += '<div class="user">' + data.players[i].username + ' ' + data.players[i].voteCount +
                            '</div>';
                    }
                    if(!data.user.isDead) {
                        let id = data.players[i].username;
                        document.getElementById(id).style.visibility = "visible";
                    }
                }
            }
            $('#player-list').html(toAdd);

        }

        else if(data.game.phase === "Defense" || data.game.phase === "Verdict" || data.game.phase === "Decision"){
            if(data.game.phase === "Decision"){
                $('#phase-info').html('Yes: ' + data.game.yay + ', No: ' + data.game.nay);
                document.getElementById('phase-info').style.display = "block";
            }
            else if(data.game.phase === "Defense"){
                for(let i=0; i<data.players.length; i++) {
                    if(data.players[i].id === data.game.votedPlayer){
                        $('#phase-info').html(data.players[i].username + ", defend yourself");
                        document.getElementById('phase-info').style.display = "block";
                        break;
                    }
                }
            }
            else {
                $('#phase-info').html(data.game.phase);
                document.getElementById('phase-info').style.display = "block";
            }

            if(data.game.phase === "Verdict"){
                if(data.user.isDead) {
                    document.getElementById("verdict").style.display = "none";
                    $('#verdict-text').html('');
                }else {
                    if(data.user.id !== data.game.votedPlayer) {
                        document.getElementById("verdict").style.display = "block";
                        var verdictText = '';
                        if (data.user.voteYes === 1) {
                            verdictText = '<h2 class="verdict verdict-yes">You Voted Yes </h2>';
                        } else if (data.user.voteYes === 0) {
                            verdictText = '<h2 class="verdict verdict-no">You Voted No</h2>'
                        } else {
                            verdictText = '<h2 class="verdict">You have not yet voted yet</h2>'
                        }
                        $('#verdict-text').html(verdictText);
                    }else{
                        document.getElementById("verdict").style.display = "none";
                        $('#verdict-text').html("The Town Will Decide Your Fate");
                    }
                }
            }
            else{
                document.getElementById("verdict").style.display = "none";
                $('#verdict-text').html('');
            }

            for(let i=0; i<data.players.length; i++){
                let id = data.players[i].username;
                document.getElementById(id).style.visibility = "hidden";
                if(data.players[i].isDead){
                    toAdd += '<div class="dead-player">' + data.players[i].username + '</div>';
                }
                else if(data.players[i].id === data.game.votedPlayer && data.game.phase !== "Decision"){
                    toAdd += '<div class="voted-player">' + data.players[i].username + '</div>';
                }
                else{
                    toAdd += '<div class="user">' + data.players[i].username + '</div>';
                }
            }
            $('#player-list').html(toAdd);
        }
        else{
            $('#phase-info').html(data.game.phase);
            document.getElementById('phase-info').style.display = "block";
            $('#day-info').html("Day " + data.game.day);
            for(let i=0; i<data.players.length; i++){
                let id = data.players[i].username;
                document.getElementById(id).style.visibility = "hidden";
                if(data.players[i].isDead){
                    toAdd += '<div class="dead-player">' + data.players[i].username + '</div>';
                }
                else{
                    toAdd += '<div class="user">' + data.players[i].username + '</div>';
                }
            }
            $('#player-list').html(toAdd);
        }

        //Game Ends
        let mafiaCount = 0;
        let townCount = 0;
        for(let i=0; i<data.players.length; i++){
            if(!data.players[i].isDead) {
                if (data.players[i].role === "mafia") {
                    mafiaCount += 1;
                }
                else{
                    townCount += 1;
                }
            }
        }
        if(mafiaCount>=townCount){
            endGame("mafia", data.user.role, data.players);
        }
        else if(mafiaCount === 0){
            endGame("town", data.user.role, data.players);
        }
    });

}

$(document).ready(function () {
    var update = setInterval(update, 1000);

    function update(){
        document.getElementById("verdict").style.display = "none";
        $.getJSON($SCRIPT_ROOT + '/_update', {
        }, function(data) {
            let toAdd = '';
            let role = data.role;
            isStarted = data.started;
            for(var i=0; i<data.players.length; i++){
                toAdd += '<div class="user">' + data.players[i].username + '</div>';
            }
            $('#player-list').html(toAdd);

            let toAddButton = '';
            for(i=0; i<data.players.length; i++){
                toAddButton += '<button class="vote btn-dark" id="';
                toAddButton += data.players[i].username;
                toAddButton += '"';
                toAddButton += ' type="button" onclick="vote(';
                toAddButton += "'" + data.players[i].username + "'";
                toAddButton += ')">Select</button><br>';
            }
            $('#button-list').html(toAddButton);

            for(i=0; i<data.players.length; i++) {
                let id = data.players[i].username;
                document.getElementById(id).style.visibility = "hidden";
            }

            var roleText = 'You are ' + data.name + ', ';

            if(isStarted) {

                document.getElementById("day-info").style.display = "block";
                document.getElementById("game-info").style.display = "block";

                clearInterval(update);
                game1 = setInterval(game_loop, 100);

                if (role === "mafia") {
                    roleText += "a member of the mafia!"
                }
                else if (role === "detective") {
                    roleText += "the detective!"
                }
                else if (role === "guardian_angel") {
                    roleText += "the guardian angel!"
                }
                else {
                    roleText += "a member of the town!"
                }
                $('#game-header').html(roleText);

                if(role === "mafia") {
                    let mafiaMembers = '<h3>' + 'Mafia Members' + '</h3>';
                    for (i = 0; i < data.players.length; i++) {
                        if (data.players[i].role === "mafia") {
                            mafiaMembers += '<div class="user">' + data.players[i].username + '</div>'
                        }
                    }
                    $('#mafia-members').html(mafiaMembers);
                }
            }
        });
    }

});
