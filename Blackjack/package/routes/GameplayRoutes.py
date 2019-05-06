from Blackjack.package import app, db
from flask_login import login_required
from flask import render_template, redirect, url_for, jsonify, make_response, json, request
from flask_login import current_user
from Blackjack.package.Databases import database_model as dm
from Blackjack.package.Databases.database_model import User, Deck, Player, Table
from Blackjack.package.routes.Blackjack import RoundResult, HitResult, bust, reset_cards, add_dealer, cardTran, getCards, getPlayers, PlayerDealerCompare
from Blackjack.package import socketio
import random
import time


@login_required
@app.route('/gameplay_page', methods=['GET', 'POST'])
def gameplay_page():
    return render_template("Gameplay.html")

@app.route('/gameplay_page/<idC>', methods=['GET', 'POST'])
def gameplay_page_delete(idC):
    player = dm.Player.query.filter_by(id=idC).first()
    db.session.delete(player)
    db.session.commit()
    return redirect('/gameplay_page')

@login_required
@app.route('/table_one', methods=['GET', 'POST'])
def table_one():

    table = dm.Table.query.filter_by(tid=1).first()
    exist = dm.Player.query.filter_by(id=current_user.id).first()

    print("current user id", current_user.id)

    if table.tablestate!="joinable":
        return render_template("Gameplay.html")

    if table == None:
        return render_template("BlackjackTables/Gameplay.html")
    if table.seat > 0 and exist == None:
        player = dm.Player(amnt=current_user.funds, bet=0, id=current_user.id, ptid=1)
        playerFeild(table, player)

        table.seat = table.seat-1
        db.session.add(player)
        db.session.commit()
        players = getPlayers()
        cards = getCards()
        return render_template("BlackjackTables/Table1.html", player=player, players=players, cards=cards)
    else:
        players = getPlayers()
        cards = getCards()
        return render_template("BlackjackTables/Table1.html", player=exist, players=players, cards=cards)


    return render_template("Gameplay.html")

def getPlayers():
    players = dm.Player.query.all()
    return players

def getCards():
    cards = []
    for i in range (1,7):
        cards.append(dm.Deck.query.filter_by(pid=i))
    return cards

@app.route('/deck_build')
def deck_build():
    for t in range(1, 5):
        table = dm.Table(seat=6, tablestate="joinable")
        db.session.add(table)
        db.session.commit()
    for i in range(1, 5):#tables
        for j in range(0, 6):#decks
            for k in range(1, 14):#card
                suit="diamond"

                if suit=="diamond":
                    deck=dm.Deck(suit=suit, cnum=k, tid=i)
                    db.session.add(deck)
                    db.session.commit()
                    suit="hearts"

                if suit=="hearts":
                    deck=dm.Deck(suit=suit, cnum=k, tid=i)
                    db.session.add(deck)
                    db.session.commit()
                    suit="clubs"

                if suit=="clubs":
                    deck=dm.Deck(suit=suit, cnum=k, tid=i)
                    db.session.add(deck)
                    db.session.commit()
                    suit="spades"

                if suit=="spades":
                    deck=dm.Deck(suit=suit, cnum=k, tid=i)
                    db.session.add(deck)
                    db.session.commit()

    add_dealer()
    return redirect('create_account')

def table_four():
    return render_template("BlackjackTables/Table4.html")

def get_card(id):
    player = dm.Player.query.filter_by(id=id).first()
    valid = False
    cards = dm.Deck.query.filter_by(tid=1).all()
    seat = player.playerNum

    while not valid:
        rand = random.randint(-1, 311)
        cardSel = cards[rand]
        if cardSel.pid is None:
            cardSel.pid = player.pid
            if player.hand > 0:
                cardSel.lid = player.hand
                # handSwitchTotal = cardTotal(cardSel.pid, cardSel.lid)
                # if handSwitchTotal > 21 and player.hand < 2:
                #     player.hand = player.hand+1
                db.session.commit()

            total = cardTotal(id, cardSel.lid)
            db.session.commit()
            if total > 21:
                total = aceTotalChecker(total)
            cardEntry = CardEntry(cardSel, total, seat)
            valid = True

    finalCard = json.dumps(cardEntry)
    print("card entry", cardEntry)
    return finalCard

def aceTotalChecker(total):
    cards = Deck.query.filter_by(pid=current_user.id).all()
    aceList = []

    for card in cards:
        if(card.cnum==1):
            aceList.append(card)

    for i in range(0, len(aceList)):
        player = Player.query.filter_by(id=current_user.id)
        if player.hand == None:
            total = cardTotal(current_user.id, None)
        else:
            total = cardTotal(current_user.id, player.hand)

        if total > 21:
            total -= 10

    return total

def get_card_split_test(id):
    player = dm.Player.query.filter_by(id=id).first()
    valid = False
    cards = dm.Deck.query.filter_by(tid=1).all()

    playerCards = Deck.query.filter_by(pid=player.pid).all()
    print("Len Player cards: ", len(playerCards))
    if len(playerCards) == 0:
        print("first card")
        card1 = 13
        cardSel1 = cards[card1]
        cardSel1.pid = player.pid
        db.session.commit()
        total = cardTotal(id, cardSel1.lid)
        cardEntry = CardEntry(cardSel1, total)
        finalCard = jsonify(cardEntry)

    if len(playerCards) == 1:
        print("second card")
        card2 = 14
        cardSel2 = cards[card2]
        cardSel2.pid = player.pid
        db.session.commit()
        total = cardTotal(id, cardSel2.lid)
        cardEntry = CardEntry(cardSel2, total)
        finalCard = jsonify(cardEntry)

    if len(playerCards) >= 2:
        print("hit card")
        while not valid:
            rand = random.randint(-1,311)
            cardSel = cards[rand]
            if cardSel.pid is None:
                cardSel.pid = player.pid
                if player.hand > 0:
                    cardSel.lid = player.hand
                    handSwitchTotal = cardTotal(cardSel.pid, cardSel.lid)
                    if handSwitchTotal > 21 and player.hand < 2:
                        player.hand = player.hand+1
                    db.session.commit()
                total = cardTotal(id, cardSel.lid)
                db.session.commit()
                cardEntry = CardEntry(cardSel, total)

                valid = True
        finalCard = jsonify(cardEntry)
    return finalCard

def CardEntry(card, total, playerNum):
    cardEntry = {'cid': card.cid,
                 'suit': card.suit,
                 'cnum': card.cnum,
                 'tid': card.tid,
                 'pid': card.pid,
                 'lid': card.lid,
                 'total': total,
                 'seat': playerNum}
    return cardEntry

@socketio.on('player_turn_event')
def turnEvent(turn):
    #print("Turn:", turn)
    players = getPlayers()
    lastPlayer = len(players)-1

    if turn==None:
        player1 = Player.query.filter_by(ptid=1, playerNum=1).first()
        playerNum = player1.playerNum
        socketio.emit('player turn response', playerNum)
    elif turn==lastPlayer:
        print("last player")
        state = Table.query.filter_by(tid=1).first()
        state.tablestate="over"
        db.session.commit()
        playerNum=7
        #dealerAI()
        socketio.emit('player turn response', playerNum)
    else:
        nextPlayer = Player.query.filter_by(ptid=1, playerNum=turn + 1).first()
        newPlayerNum = nextPlayer.playerNum
        socketio.emit('player turn response', newPlayerNum)


@socketio.on('card_event')
def cardEvent(id):
    dealerCards = Deck.query.filter_by(tid=1, pid=1).all()

    #id none if for when a player is hitting
    if id==None:
        card = get_card(current_user.id)
        socketio.emit('get card response', card)
    else:
        print("In card_event else")
        card = get_card(id)
        socketio.emit('get card response', card)

@socketio.on('card_event_rand')
def cardEventRand(id):
    dealerCards = Deck.query.filter_by(tid=1, pid=1).all()

    # id none if for when a player is hitting
    if id == None:
        card = get_card(current_user.id)
        socketio.emit('get card response', card)
    else:
        print("In card_event else")
        card = get_card_double(id)
        socketio.emit('get card response', card)

def get_card_double(id):
    #sub 16-19
    player = dm.Player.query.filter_by(id=id).first()
    valid = False
    cards = dm.Deck.query.filter_by(tid=1).all()
    seat = player.playerNum

    while not valid:
        rand = random.randint(15, 19)
        cardSel = cards[rand]
        if cardSel.pid is None:
            cardSel.pid = player.pid
            db.session.commit()

            total = cardTotal(id, cardSel.lid)
            if total > 21:
                total = aceTotalChecker(total)
            cardEntry = CardEntry(cardSel, total, seat)
            valid = True

    finalCard = json.dumps(cardEntry)
    print("card entry", cardEntry)
    return finalCard

@login_required
@app.route('/deal_cards')
def deal_cards():
    #deal cards only returns a list of players to whom shall recieive cards
    print("dealing cards")
    players = Player.query.filter_by(ptid=1).all()
    playerIds = []
    for i in range(1, len(players)):
        playerIds.append({"id":players[i].pid})

    print("Player ids", playerIds)
    state = Table.query.filter_by(tid=1).first()
    state.tablestate = "dealt"
    db.session.commit()
    return json.dumps(playerIds)

@socketio.on('dealer_AI_event')
def dealerAI():
    dealer = Player.query.filter_by(ptid=1, pid=1).first()
    dealerCardsTotal = cardTotal(dealer.pid, None)
    table = Table.query.filter_by(tid=1).first()
    cards = []
    while(dealerCardsTotal<17):
        card = get_card(dealer.pid)
        card = json.loads(card)
        cards.append(card)
        dealerCardsTotal=cardTotal(dealer.pid, None)

    table.tablestate = "dealerdone"
    db.session.commit()
    socketio.emit('get dealer AI', json.dumps(cards))

@socketio.on('eval_event')
def evalEvent():
    dealer = Player.query.filter_by(pid=1).first()
    dealerScoreTotal = cardTotal(dealer.pid, None)
    print("Dealer Total:", dealerScoreTotal)

    player = Player.query.filter_by(pid=current_user.id, ptid=1).first()
    handResults = []

    if player.hand != 0:
        print("VALUE", player.amnt)
        handResults.append(PlayerDealerCompare(1, player, dealerScoreTotal))
        handResults.append(PlayerDealerCompare(2, player, dealerScoreTotal))
        player.bet = 0
        db.session.commit()

    else:
        handResults.append(PlayerDealerCompare(None, player, dealerScoreTotal))
        player.bet = 0
        db.session.commit()
    for i in handResults:
        print("Hand Result Size", i)
    table = Table.query.filter_by(tid=1).first()
    table.tablestate = "joinable"
    db.session.commit()
    # return json example {"hand1":["WLT":"WIN"],"hand2":["WLT":"WIN"]}
    socketio.emit('eval_response', json.dumps(handResults))

def cardTotal(pid, lid):
    total = 0
    player = Player.query.filter_by(id=pid).first()
    ppid = player.pid
    playerCards = Deck.query.filter_by(pid=ppid, lid=lid).all()
    for card in playerCards:
        total += cardTran(card.cnum)
    return total

def bust(total, res):
    if total > 21:
        res = "You Lost"
    elif total == 21:
        res = "BLACKJACK"
    return res

@login_required
@app.route('/leave', methods=['GET', 'POST'])
def leave():

    #remove player from table
    player = Player.query.filter_by(id=current_user.id).first()
    seatNum = player.playerNum
    db.session.delete(player)
    db.session.commit()

    #adjust other player seating
    players = getPlayers()
    for p in players:
        if(p.playerNum != None):
            if p.playerNum > seatNum:
                p.playerNum -= 1
                db.session.commit()
    table = Table.query.filter_by(tid=1).first()
    table.seat += 1
    db.session.commit()
    return redirect(url_for('gameplay_page'))

@login_required
@app.route('/build_card', methods=['GET', 'POST'])
def build_card():
    return render_template("BuildCard.html")

def playerFeild(table, player):
    if table.seat == 6:
        player.playerNum = 1
    if table.seat == 5:
        player.playerNum = 2
    if table.seat == 4:
        player.playerNum = 3
    if table.seat == 3:
        player.playerNum = 4
    if table.seat == 2:
        player.playerNum = 5
    if table.seat == 1:
        player.playerNum = 6
    db.session.commit()

@app.errorhandler(404)
def pageNotfound(e):
    return render_template('404.html'), 404

@app.route('/database_wipe', methods=['GET', 'POST'])
def databaseWipe():
    #Please note this needs to take place in Deck, Player, Table, User
    #Then run deck build afterwards

    db.session.query(Deck).delete()
    db.session.commit()
    db.session.query(Player).delete()
    db.session.commit()
    db.session.query(Table).delete()
    db.session.commit()
    db.session.query(User).delete()
    db.session.commit()

    return redirect('deck_build')



















