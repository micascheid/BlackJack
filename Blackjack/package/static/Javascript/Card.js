var socket = io.connect('http://' + document.domain + ':' + location.port);
var playerNum = 0;
var playerAmnt = 0;

function cardSocket(id){
   socket.emit('card_event', id);
}

function cardSocketRand(id){
    socket.emit('card_event_rand', id);
}

socket.on('get card response', function(card){
    var betButton = document.getElementById("bet");
    var stayButton = document.getElementById("stay");
    var hitButton = document.getElementById("hit");
    var splitButton = document.getElementById("split");
    var doubleDownButton = document.getElementById("double_down");
    card = JSON.parse(card);

    if(card.pid===1){
        console.log("dealer card:" + card.cnum);
        dealerTotal = card.total;
        console.log("Dealer Got card, total: " + dealerTotal);
    }

    betButton.disabled = true;
    console.log(card.seat);
    var playerDivT = document.getElementById("player"+card.seat+"Table");
    if(playerDivT.id === "playernullTable" && playerDivT.rows[0] !== undefined){
        playerDivT.rows[0].style.display = 'none';
    }
    console.log(playerDivT);
    if(card.lid===1){
        var row1Cells = playerDivT.rows[0].cells;
        if(row1Cells.length>=1) {
            var cellOnSplit1 = playerDivT.rows[0].insertCell(-1);
            cellOnSplit1.innerHTML = cardTranslation(card.cnum).toString() + " " + suitTrans(card.suit);
        }
    }else if(card.lid===2){
        var row2Cells = playerDivT.rows[1].cells;
        if(row2Cells.length>=1) {
            var cellOnSplit2 = playerDivT.rows[1].insertCell(-1);
            cellOnSplit2.innerHTML = cardTranslation(card.cnum).toString() + " " + suitTrans(card.suit);
        }
    }else{
        var row = playerDivT.insertRow(-1);
        var cellAdd = row.insertCell(-1);
        cellAdd.innerHTML = cardTranslation(card.cnum).toString() + " " + suitTrans(card.suit);
    }

    //handling of button accessibility
    var player = "player" + card.seat;
    var playerText = document.getElementById(player);

    if (player==="playernull"){
        player="Dealer";
    }
    if(card.lid===null){
        if(card.total < 21){
            if(player === "Dealer"){
                playerText.innerHTML = player + ": ";
            } else {
                playerText.innerHTML = player + ": " + card.total;
            }
             stayButton.diabled=false;
        }
        if(card.total > 21){
            playerText.innerText = player + ": Bust";
            hitButton.disabled=true;
            stayButton.disabled=true;
            splitButton.disabled = true;
            if(card.seat!==null) {
                console.log("shouldn't be here:" + card.seat);
                playerTurn(card.seat);
            }
        }
        if(card.total===21){
            playerText.innerText = player + ": BlackJack";
            hitButton.disabled=true;
            stayButton.disabled=true;
            if(card.seat!==null){
                console.log("shouldn't be here" + card.seat);
                playerTurn(card.seat);
            }
        }
    }

    if(card.lid!==null){
        if(card.total < 21){
             playerText.innerText = player + ": " + card.total;
        }
        if(card.total > 21){
            playerText.innerText = player + ": Bust";
            // playerTurn(playerNum);
            if(card.lid===2){
               hitButton.disabled=true;
               stayButton.disabled=true;
            }
        }
        if(card.total===21){
            playerText.innerText = player + ": BlackJack";
            if(card.lid===2){
                // playerTurn(playerNum);
               hitButton.disabled=true;
               stayButton.disabled=true;
            }
        }
    }
});

function playerTurn(turn){
    socket.emit('player_turn_event', turn);
}

socket.on('player turn response', function (turn) {
    turn = JSON.parse(turn);
    var myDiv = document.getElementById(playerNum);

    var stayButton = document.getElementById("stay");
    var hitButton = document.getElementById("hit");
    var splitButton = document.getElementById("split");
    var doubleButton = document.getElementById("double_down");

    // console.log("My playerNum" + playerNum);
    if(playerNum === turn){
        //turn buttons on
        stayButton.disabled=false;
        hitButton.disabled=false;
        splitCheck();
        doubleDownCheck();
    } else if(turn===7 && playerNum===totalPlayers){
        console.log("time for dealer to play, total: " + dealerTotal + " turn:" + turn);
        dealerAISocket();
        stayButton.disabled=true;
        hitButton.disabled=true;
        splitButton.disabled=true;
        doubleButton.disabled=true;
    }
    // console.log(turn);

});

function dealerAISocket(){
    socket.emit('dealer_AI_event');
}

socket.on('get dealer AI', function (response) {
    var cards = JSON.parse(response);
    var i;
    var dealerDivT = document.getElementById("playernullTable");
    dealerDivT.rows[0].style.display = "";
    console.log("To display: " + cards.length);
    console.log(cards);
    if (cards.length > 0) {
        var playerDivT = document.getElementById("playernullTable");
        for (i = 0; i < cards.length; i++) {
            var row = playerDivT.insertRow(-1);
            var cellAdd = row.insertCell(-1);
            cellAdd.innerHTML = cardTranslation(cards[i].cnum).toString() + " " + suitTrans(cards[i].suit);
        }

        var playerText = document.getElementById("playernull");
        if (cards[cards.length - 1].total > 21) {
            playerText.innerText = "Dealer: Bust";
        } else if (cards[cards.length - 1].total === 21) {
            playerText.innerText = "Dealer: BlackJack";
        } else {
            playerText.innerText = "Dealer: " + cards[cards.length - 1].total;
        }
    }
    console.log("gettingCalled");
    evalSocket();

});


function passPlayerNum(playerNumPass){
    playerNum = playerNumPass;
}

function passPlayerAmnt(playerAmntPass){
    playerAmnt = playerAmntPass;
}

function getCard(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200){
            var socket = io.connect('http://' + document.domain + ':' + location.port);
              socket.on( 'my card response', function( card ) {
                console.log( "I got a response!");
                if( typeof card !== 'undefined' ) {
                    console.log(card.cardNum);
                }
              })
        }
    };
    xhttp.open('GET', '/get_card', false);
    xhttp.send();
}

function cardTranslation(num){
    var cardTrans;
    if(num === 11) cardTrans = "Jack";
    if(num === 12) cardTrans = "Queen";
    if(num === 13) cardTrans = "King";
    if(num < 11) cardTrans = num;
    return cardTrans;
}

function suitTrans(suit){
    var suitT;
    if(suit==="hearts") suitT="&hearts;";
    if(suit==="clubs") suitT="&clubs;";
    if(suit==="spades") suitT="&spades;";
    if(suit==="diamond") suitT="&diams;";
    return suitT;
}

function ready(){
        var leaveButton = document.getElementById("leave");
        var numBet = document.getElementById("numBet");
        var betButton = document.getElementById("bet");
        // var ready = document.getElementById("ready");
        var stay = document.getElementById("stay");
        var hit = document.getElementById("hit");
        var split = document.getElementById("split");
        var doubleDownButton = document.getElementById("double_down");
        var tableElem = document.getElementsByTagName("table");

        leaveButton.disabled=true;
        var dealerHeader = document.getElementById("playernull");
        dealerHeader.innerHTML="Dealer:";
        console.log("Tables: " + tableElem.length);
        var i;

        for(i = 0; i < tableElem.length; i++) {
            var localTableElem = tableElem[i].getElementsByTagName("tr");
            console.log("Rows to delete: " + localTableElem.length);
            var Parent = document.getElementById(tableElem[i].getAttribute("id"));
            while (Parent.hasChildNodes()) {
                Parent.removeChild(Parent.firstChild);
            }
        }

        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function () {
            if (this.readyState === 4 && this.status === 200){
                var state = this.responseText;
                console.log(state);
                if(state==="deal"){
                    deal();
                }
            }
        };
        xhttp.open('GET', '/ready', false);
        xhttp.send();
        betButton.disabled = true;

}
