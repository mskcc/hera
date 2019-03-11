from flask import Flask
# from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_pyfile("config.py")

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'
# login_manager.login_message = ''

# from first_app.auth.views import auth
# from first_app.home.views import home

# app.register_blueprint(auth)
# app.register_blueprint(home)


csrf = CSRFProtect(app)

import hera_app.views
