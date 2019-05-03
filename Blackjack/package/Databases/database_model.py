from Blackjack.package import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id          = db.Column(db.Integer, primary_key=True)
    first_name  = db.Column(db.String(60), nullable=False)
    last_name   = db.Column(db.String(60), nullable=False)
    email       = db.Column(db.String(60), unique=True, nullable=False)
    username    = db.Column(db.String(60), nullable=False, unique=True)
    password    = db.Column(db.String(60), nullable=False)
    funds       = db.Column(db.Integer, nullable=True)
    player      = db.relationship("Player", uselist=False, backref='user')

    def __repr__(self):
        return "Id: " + str(self.id) + "\tFirst Name: " + self.first_name + "\tLast Name: " + self.last_name + "\tEmail: " \
               + self.email + "\tUsername: " + self.username + "\tPassword: " + self.password + "\tFunds: " \
               + str(self.funds)


class Player(db.Model):
    __tablename__ = 'player'
    pid         = db.Column(db.Integer, primary_key=True)
    amnt        = db.Column(db.Integer, nullable=False)
    bet         = db.Column(db.Integer, nullable=False)
    id          = db.Column(db.Integer, db.ForeignKey('user.id'))
    ptid        = db.Column(db.Integer, db.ForeignKey('table.tid'))
    hand        = db.Column(db.Integer, default=0)
    over        = db.Column(db.Boolean, default=False)
    playerNum   = db.Column(db.Integer, default=None)

    def dictify(self):
        return {'pid':self.pid, 'amnt':self.amnt, 'bet':self.bet, 'id':self.id, 'ptid':self.ptid}

    def __repr__(self):
        return "pid: " + str(self.pid) + "\tamnt: " + self.amnt + "\tbet: " + self.bet + "\tid: " \
               + self.id + "\tptid: " + self.ptid

class Table(db.Model):
    __tablename__ = 'table'
    tid     = db.Column(db.Integer, primary_key=True)
    seat    = db.Column(db.Integer, nullable=False)
    tablestate = db.Column(db.String(20), nullable=False)

    tplayer = db.relationship("Player", backref='table')
    tdeck   = db.relationship("Deck", backref='table')

    def __repr__(self):
        return  "tid:" + str(self.tid) + "\tseat: " + str(self.seat)  + "\ttablestate: " + self.tablestate

class Deck(db.Model):
    __tablename__ = 'deck'
    cid     = db.Column(db.Integer, primary_key=True)
    suit    = db.Column(db.String(7), nullable=False)
    cnum    = db.Column(db.Integer, nullable=False)
    tid     = db.Column(db.Integer, db.ForeignKey('table.tid'))
    pid     = db.Column(db.Integer, db.ForeignKey('player.pid'))
    lid     = db.Column(db.Integer)

    def dictify(self):
        return {'cid':self.cid, 'suit':self.suit, 'cnum':self.cnum, 'tid':self.tid, 'pid':self.tid}

    def __repr__(self):
        return "cnum: " + str(self.cnum)
        # return "cid: " + self.cid + "\tsuit: " + str(self.suit) + "\tcnum: " + self.cnum + "\tpid: " \
        #        + self.pid + "tid: " + self.tid


#nginx will load all files in /usr/local/etc/nginx/servers/
