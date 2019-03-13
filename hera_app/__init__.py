from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
app.config.from_pyfile("secret_config.py")
# app.config.from_pyfile("config.py")
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'
login_manager.login_message = ''


# User model/table creation
from hera_app.auth import User

# SQLAlchemy only creates if not exist
db.create_all()
db.session.commit()

from .views.tables import tables
app.register_blueprint(tables)

from .views.main import main
app.register_blueprint(main)




csrf = CSRFProtect(app)

