from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import logging
import os

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] HERA %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


# logger = logging.getLogger('hera')
# if (os.environ['FLASK_ENV']== 'local_development'):
#     current_dir = os.getcwd()
#     logging_file_handler = logging.FileHandler(current_dir+'/hera.log')
# else:
#     logging_file_handler = logging.FileHandler('/data/www/uwsgi/logs/hera.log')
# logging_stream_handler = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
# logging_file_handler.setFormatter(formatter)
# logging_stream_handler.setFormatter(formatter)
# logger.addHandler(logging_file_handler)
# logger.addHandler(logging_stream_handler)
# logger.setLevel(logging.INFO)

app = Flask(__name__)
app.config.from_pyfile("secret_config.py")
# app.config.from_pyfile("config.py")
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user.login'
login_manager.login_message = ''





# User model/table creation
from hera_app.auth import User

# SQLAlchemy only creates if not exist
db.create_all()
db.session.commit()

from .views.tables import tables
app.register_blueprint(tables)

from .views.user import user
app.register_blueprint(user)

# different blueprint naming because calling the blueprint and the view function 'dashboard'
# would mask the global name
from .views.dashboard import dashboard_blueprint
app.register_blueprint(dashboard_blueprint)


csrf = CSRFProtect(app)

