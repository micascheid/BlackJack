var dealerTotal = 0;
var totalPlayers=0;
function deal() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if(xhttp.readyState === 4 && xhttp.status === 200){
            var response = this.responseText;
            var players = JSON.parse(response);
            var i;
            var j;
            totalPlayers=players.length;
            console.log(players);
            if(totalPlayers > 1) {
                console.log("running multi player");
                for (i = 0; i < 2; i++) {
                    for (j = 1; j < players.length + 1; j++) {
                        var id = players[j - 1].id;
                        cardSocket(id);
                    }
                    cardSocket(1);
                }
            }
            if(totalPlayers===1){
                console.log("running single player");
                for (i = 0; i < 2; i++){
                    var id = players[0].id;
                    cardSocketRand(id);
                    cardSocket(1);
                }
            }
            //Start the playing
            playerTurn(null);
        }
    };
    xhttp.open("GET","/deal_cards",false);
    xhttp.send();
    //splitButton.disabled = false;
}

function stay(){
    var hitButton = document.getElementById("hit");
    var stayButton = document.getElementById("stay");
    var betButton = document.getElementById("bet");
    var splitButton = document.getElementById("split");
    var doubleButton = document.getElementById("double_down");
    hitButton.disabled = true;

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if(this.readyState === 4 && this.status === 200){
            var response = this.responseText;
            var result = JSON.parse(response);
            console.log("TableState" + result.state);
            stayButton.disabled = true;
            hitButton.disabled = true;
            betButton.disabled = true;
            splitButton.disabled = true;
            doubleButton.disabled = true;
            if (result.over === "true") {
                playerTurn(playerNum);
            }else {
                console.log("next hand");
                hitButton.disabled = false;
                stayButton.disabled = false;
            }
        }
    };
    xhttp.open('GET', '/stay', false);
    xhttp.send();
}

function hit() {
    cardSocket(null);
    var doubleDownButton = document.getElementById("double_down");
    var split = document.getElementById("split");
    split.diabled = true;
    doubleDownButton.disabled = true;

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            var player = document.getElementById("player1");
            var response = this.responseText;
            var card = JSON.parse(response);
        }
    };
}

function split(check) {

    var xhttp = new XMLHttpRequest();
    var equality = "false";
    xhttp.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            var response = this.responseText;
            var result = JSON.parse(response);
            if (result.result === "equal" && check===false) {
                var splitButton = document.getElementById("split");
                var doubleButton = document.getElementById("double_down");
                splitButton.disabled = true;
                doubleButton.disabled = true;

                cardSocket(null);
            }
            if (check === true) {
                equality = result.result;
            }
        }
    };
    xhttp.open('GET', '/split', false);
    xhttp.send();
    return equality;
}

function splitCheck(){
    var xhttp = new XMLHttpRequest();
    var splitButton = document.getElementById("split");
    xhttp.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200){
            var response = this.responseText;
            if (response==="equal"){
                splitButton.disabled = false;
            } else {
                splitButton.disabled = true
            }
        }
    };
    xhttp.open('GET', '/splitCheck', false);
    xhttp.send();
}

function doubleDownCheck(){
    var double="false";
    var doubleDownButton = document.getElementById("double_down");
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200){
            var response = this.responseText;
            if (response==="true"){
                doubleDownButton.disabled = false;
            } else {
                doubleDownButton.disabled = true;
            }
        }
    };
    xhttp.open('GET','/doubleDownCheck', false);
    xhttp.send();
}

function dealerBlackJackCheck(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
          if(this.readyState === 4 && this.status === 200){
              var response = this.response;
              var result = JSON.parse(response);

              if (result.dealer === "over") {
                  console.log("DEALER BLACKJACK");
                  stay();
              }
          }
    };
    xhttp.open('GET', 'dealerBlackJackCheck', false);
    xhttp.send();
}

function bet() {
    checkFundsBet();
    //add if statement further movement of that player
    var hit = document.getElementById("hit");
    var stay = document.getElementById("stay");
    var split = document.getElementById("split");
    var betButton = document.getElementById("bet");
    var num = document.getElementById("numBet");
    var bet = 0;

    var doubleDownButton = document.getElementById("double_down");
    var currentbet = document.getElementById("currentbet");
    doubleDownButton.disabled = true;
    betButton.disabled = false;
    hit.disabled = true;
    stay.disabled = true;
    split.disabled = true;
    num.disabled = false;

    console.log("The input number is:" + num.value);

    if(Number.isInteger(parseInt(num.value)) && parseInt(num.value) <= playerAmnt){
        bet = num.value;
        currentbet.innerHTML = "Current bet: " + bet;
        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/bet", true);
        xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhttp.send(JSON.stringify({"num":bet}));
        console.log("Before ready");
        ready();
    }else{
        alert("Not a valid bet");
    }
}

function checkFundsBet() {
    var stay = document.getElementById("stay");
    var hit = document.getElementById("hit");
    var split = document.getElementById("split");
    var doubeDownButton = document.getElementById("double_down");
    xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200)
        {
            var response = this.responseText;
            var check = JSON.parse(response);
            console.log("Outside if statement");
            //console.log("Funds: " + check['funds']);
            if(check.funds <= 0)
            {
                console.log(check.funds);
                alert("INSUFFICIENT FUNDS!!!");
                stay.disabled = true;
                hit.disabled = true;
                split.disabled = true;
                doubeDownButton.disabled = true;
                // window.location.replace("http://127.0.0.1:5000/gameplay_page")
            }

        }
    };
    xhttp.open('GET', '/check_funds', true);
    xhttp.send();
}

function doubleDown() {
    cardSocket(null);
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if(this.readyState === 4 && this.status === 200) {
            var response = this.responseText;
            var card = JSON.parse(response);
            var currentbet = document.getElementById("currentbet");
            currentbet.innerHTML="Current bet: " + card.bet;
            console.log(card.bet);
            //document.body.appendChild(doubleDownBet);
        }
    };
    xhttp.open('GET', '/double_down', true);
    xhttp.send();

    stay();
}

function evalSocket(){
    socket.emit('eval_event');
}

socket.on('eval_response', function (result) {
        result = JSON.parse(result);
        console.log("json.parse: " + result);

        var checker = result[0].handNone;

        if(typeof checker !=='undefined'){
            var table = document.getElementById("player"+result[0].handNone[0].player+"Table");
            var row = table.insertRow(-1);
            var rowCell = row.insertCell(-1);
            rowCell.innerHTML = result[0].handNone[0].WLT;
            //playerAmnt = result[0].handNone[0].playerAmnt;
            var tablefunds = document.getElementById("tablefunds");
            if(result[0].handNone[0].playerNum === playerNum){
                playerAmnt = result[0].handNone[0].playerAmnt;
                tablefunds.innerHTML = "You are player: " + playerNum + " you have " + playerAmnt;
            }
            //else is for displaying the win/loss for a split hand
        } else{
            var table = document.getElementById("player"+result[0].hand1[0].player+"Table");
            var row1 = table.rows[0];
            var row1AddCell = row1.insertCell(-1);
            row1AddCell.innerHTML = result[0].hand1[0].WLT;

            var row2 = table.rows[1];
            var row2AddCell = row2.insertCell(-1);
            row2AddCell.innerHTML = result[1].hand2[0].WLT;

            var tablefunds = document.getElementById("tablefunds");
            playerAmnt = result[1].hand2[0].playerAmnt;
            tablefunds.innerHTML = "You are player: " + playerNum + " you have " + playerAmnt;
        }
        setTimeout(roundOverButtons,10000);
});

function dealerTotalFunc(card) {
    return card.total;
}


function roundOverButtons(){
    var betButton = document.getElementById("bet");
    var currentbet = document.getElementById("currentbet");
    var leaveButton = document.getElementById("leave");
    //Reset everyones cards
    var i;
    for(i=1; i<7; i++){
        var playerHeader = document.getElementById("player"+i);
        playerHeader.innerHTML="player"+i+":";
    }
    ready();
    currentbet.innerHTML="Current bet:";

    betButton.disabled=false;
    leaveButton.disabled = false;


}



