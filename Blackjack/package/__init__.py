from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
import os

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'c56bec1880b567d61b7cdd462cc2070a'
socketio=SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from package.routes import AccountRoutes, GameplayRoutes