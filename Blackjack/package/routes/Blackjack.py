from package import app, db
from flask_login import login_required
from flask import render_template, redirect, url_for, jsonify, make_response, json, request
from flask_login import current_user
from package.Databases import database_model as dm
from package.Databases.database_model import User, Deck, Player, Table
from package.routes.Results import HitResult, SplitResult, RoundResult
import time

class DoubleDown:
    def __init__(self, bet, funds):
        self.bet = bet
        self.funds = funds

    def dictify(self):
        return {"bet": self.bet, "funds": self.funds}


class Bet:
    def __init__(self, funds):
        self.funds = funds

    def dicitify(self):
        return {"funds": self.funds}

def bust(total, res):
    if total > 21:
        res = "You Lost"
    elif total == 21:
        res = "BLACKJACK"
    return res


@login_required
@app.route('/ready', methods=['GET', 'POST'])
def ready():
    ready = "False"
    player = dm.Player.query.filter_by(id=current_user.id).first()
    player.hand = 0
    # player.bet = 5
    db.session.commit()

    cards = Deck.query.all()
    for card in cards:
        if card.pid is not None:
            card.pid = None
            card.lid = None
            db.session.commit()

    #Go through all players and check their bets
    #If all their bets are > 0 then set tablestate to deal

    players = getPlayers()
    table = Table.query.filter_by(tid=1).first()
    state = table.tablestate
    for player in players:
        #print(player.bet)
        if player.bet == 0:
            state = "waiting"
            return ready
        else:
            state = "deal"
    db.session.commit()
    return state


@login_required
@app.route('/stay', methods=['GET', 'POST'])
def stay():
    player = dm.Player.query.filter_by(id=current_user.id).first()
    table = Table.query.filter_by(tid=1).first()
    state = table.tablestate

    if player.hand == 2 or player.hand == 0:
        print("player over")
        return jsonify({"over":"true"})
    else:
        print("Looks like you have another hand")
        player.hand+=1
        db.session.commit()
        return jsonify({"over":"false"})


@login_required
@app.route('/hit', methods=['GET', 'POST'])
def hit():
    total = 0
    result = "Hit"
    player = Player.query.filter_by(id=current_user.id).first()
    print(player.dictify())
    for card in Deck.query.filter_by(pid=player.pid).all():
        total += cardTran(card.cnum)
    print("Total cards added: ", total)
    #if(total)
    newResult = bust(total, result)
    print(newResult)

    return jsonify(HitResult(str(total), newResult).dictify())


@login_required
@app.route('/split', methods=['GET', 'POST'])
def split():
    split_alert = "Splitting"
    player = Player.query.filter_by(id=current_user.id).first()
    player.hand = 1
    db.session.commit()
    pid = player.pid
    cards = Deck.query.filter_by(pid=pid).all()
    if cards[0].cnum == cards[1].cnum:
        cards[0].lid = 1
        cards[1].lid = 2
        db.session.commit()
        print("Equal")
        result = "equal"
    else:
        print("Not Equal")
        result = "not equal"

    return jsonify(SplitResult(split_alert, result).dictify())


@login_required
@app.route('/splitCheck', methods=['GET','POST'])
def splitCheck():
    player = Player.query.filter_by(id=current_user.id).first()
    # note that player.hand = 1 will only work for 1 split aka two hands
    pid = player.pid
    cards = Deck.query.filter_by(pid=pid).all()
    if cards[0].cnum == cards[1].cnum:
        result = "equal"
    else:
        result = "notequal"

    return result


@login_required
@app.route('/doubleDownCheck', methods=['GET','POST'])
def doubleDownCheck():
    player = Player.query.filter_by(id=current_user.id).first()
    player_cards = Deck.query.filter_by(pid=player.pid).all()
    user = User.query.filter_by(id=player.id).first()
    #total = int(player_cards[0].cnum) + int(player_cards[1].cnum)
    if player.hand == 1:
        total = cardTotal(current_user.id, 1)
    elif player.hand == 2:
        total = cardTotal(current_user.id, 2)
    else:
        total = cardTotal(current_user.id, None)

    if total == 9 or total == 10 or total == 11:
        return "true"
    return "false"


@login_required
@app.route('/dealerBlackJackCheck', methods=['GET', 'POST'])
def dealerBlackJackCheck():
    dealer = Player.query.filter_by(pid=1).first()
    dealerTotal = cardTotal(dealer.pid, None)

    if dealerTotal == 21:
        print("DEALER HIT BLACKJACK")
        return jsonify({"dealer":"over"})

    return jsonify({"dealer":"continue"})


def reset_cards():
    cards = Deck.query.all()
    for card in cards:
        if card.pid is not None:
            card.pid = None
            card.lid = None
            db.session.commit()
    return redirect(url_for('gameplay_page'))


def add_dealer():
    user = User(first_name="Dealer", last_name="b", email="b", username="b", password="b", funds=1000)
    db.session.add(user)
    db.session.commit()
    userDealer = User.query.filter_by(id=1).first()
    dealer = Player(pid=userDealer.id, amnt=userDealer.funds, bet=5, id=userDealer.id, ptid=1)
    db.session.add(dealer)
    db.session.commit()


def cardTran(num):
    newNum = num
    if(newNum > 10):
        newNum = 10
    if(newNum == 1):
        newNum = 11

    return newNum


def getPlayers():
    players = dm.Player.query.all()
    return players


def getCards():
    cards = []
    for i in range (1,7):
        cards.append(dm.Deck.query.filter_by(pid=i))
    return cards


@login_required
@app.route('/bet', methods=['GET', 'POST'])
def bet():
    player = Player.query.filter_by(id=current_user.id).first()
    user = User.query.filter_by(id=player.id).first()
    table = Table.query.filter_by(tid=1).first()
    if request.method == 'POST':
        num = request.json
        funds = int(user.funds)
        print("Current Funds: ", funds)
        bet = int(num['num'])
        print("Bet: ", bet)
        funds -= bet
        print("Remaining funds: ", funds)
        user.funds = funds
        player.bet = bet
        table.tablestate = "betting"
        db.session.commit()

    return render_template("Gameplay.html")


@login_required
@app.route('/check_funds', methods=['GET', 'POST'])
def check_funds():
    player = Player.query.filter_by(id=current_user.id).first()
    user = User.query.filter_by(id=player.id).first()
    funds = int(user.funds)
    return jsonify(Bet(funds).dicitify())


@login_required
@app.route('/double_down', methods=['GET', 'POST'])
def double_down():
    player = Player.query.filter_by(id=current_user.id).first()
    player_cards = Deck.query.filter_by(pid=player.pid).all()
    user = User.query.filter_by(id=player.id).first()
    print(player_cards[0].cnum)
    print(player_cards[1].cnum)
    total = int(player_cards[0].cnum) + int(player_cards[1].cnum)
    print("Double down total: ", total)
    if total == 9 or total == 10 or total == 11:
        print("You can double down")
        new_bet = int(player.bet) * 2
        new_funds = int(user.funds) - player.bet
        player.bet = new_bet
        user.funds = new_funds
        print("Player double down bet: ", player.bet)
        print("Updated funds after double down: ", user.funds)
        db.session.commit()


    return jsonify(DoubleDown(new_bet, new_funds).dictify())


def cardTotal(pid, lid):
    total = 0
    player = Player.query.filter_by(id=pid).first()
    ppid = player.pid
    playerCards = Deck.query.filter_by(pid=ppid, lid=lid).all()
    for card in playerCards:
        total += cardTran(card.cnum)
    return total


def PlayerDealerCompare(i, player, dealerScoreTotal):

    playerScoreTotal = cardTotal(player.pid, i)
    handNum = "hand" + str(i)
    user = current_user

    if playerScoreTotal > dealerScoreTotal and playerScoreTotal <= 21:
        # JSON variables to pass
        winnings = player.bet
        if playerScoreTotal == 21:
            winnings = winnings*1.5

        tableValue = player.amnt + winnings

        player.amnt = tableValue
        db.session.commit()
        user.funds = player.amnt
        db.session.commit()

        finalResult = {handNum:[{"WLT":"win","player":player.playerNum,"playerAmnt":player.amnt,"playerNum":player.playerNum}]}

    if playerScoreTotal < dealerScoreTotal and dealerScoreTotal > 21 and playerScoreTotal <= 21:
        # JSON variables to pass
        winnings = player.bet
        if playerScoreTotal == 21:
            winnings = winnings*1.5

        tableValue = player.amnt + winnings

        player.amnt = tableValue
        db.session.commit()
        user.funds = player.amnt
        db.session.commit()

        finalResult = {handNum: [{"WLT": "win", "player": player.playerNum, "playerAmnt": player.amnt, "playerNum": player.playerNum}]}

    if playerScoreTotal == dealerScoreTotal:
        tableValue = player.amnt
        # Database manipulation

        player.amnt = tableValue
        db.session.commit()
        user.funds = player.amnt
        db.session.commit()

        finalResult = {handNum:[{"WLT":"Tie","player":player.playerNum,"playerAmnt":player.amnt,"playerNum":player.playerNum}]}

    if playerScoreTotal < dealerScoreTotal and dealerScoreTotal<=21 or playerScoreTotal > 21:
        # JSON variables to pass
        winnings = -1 * player.bet
        tableValue = player.amnt + winnings
        print("TABLEVALUE", tableValue)

        player.amnt = tableValue
        db.session.commit()
        user.funds = player.amnt

        finalResult = {handNum:[{"WLT":"Loss","player":player.playerNum,"playerAmnt":player.amnt,"playerNum":player.playerNum}]}

    return finalResult
