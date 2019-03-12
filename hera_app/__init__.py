from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
# app.config.from_pyfile("secret_config.py")
app.config.from_pyfile("config.py")
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = ''


# User model/table creation
from hera_app.auth import User

db.create_all()
db.session.commit()

csrf = CSRFProtect(app)

import hera_app.views
