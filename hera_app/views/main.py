import ldap
import re
from flask import (
    request,
    render_template,
    flash,
    redirect,
    url_for,
    g,
    jsonify,
    session,
    Blueprint,
)
from flask_login import current_user, login_user, logout_user, login_required
from datetime import timedelta





from hera_app import app, login_manager, db
from hera_app.auth import User, LoginForm


main = Blueprint('main', __name__)


def log_error(*args):
    print("HERA_ERROR:"),
    for arg in args:
        print(arg),
    print()


def log_info(*args):
    print("HERA_INFO:"),
    for arg in args:
        print(arg),
    print()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def current_user_name():
    if current_user.is_authenticated:
        return current_user.user_name
    else:
        return "Anonymous"


def load_username(username):
    print(username)

    return User.query.filter_by(username=username).first()


# @main.before_request
# def get_current_user():
#     g.user = current_user


@main.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=2)


# @main.route('/')
# @main.route('/index')
# @main.route('/home', methods=['GET', 'POST'])
# @login_required
# def home():
#     return render_template('home.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Error: You are already logged in')
        return redirect(url_for('dashboard.dashboard'))
    form = LoginForm()
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        if '@' in username:
            log_error(
                "user",
                username,
                "trying to login with email address instead of MSK user id",
            )
            flash(
                'Error: Please use your MSK user ID instead of email address as Username'
            )
            return render_template('login.html', form=form), 401

        try:
            result = User.try_login(username, password)
            groups = format_result(result)

        except ldap.INVALID_CREDENTIALS:
            log_error("user", username, "trying to login with invalid credentials")
            flash('Error: Invalid username or password. Please try again.')
            return render_template('login.html', form=form), 401

        user = load_username(username)
        # no authorization yet. for now, everybody who authenticates will be added to table
        if not user:
            user = User(username, str(groups))
            db.session.add(user)
            db.session.commit()
            log_info('new user commited', user.id, user.username, user.groups)
        else:
            log_info('existing user loaded', user.id, user.username, user.groups)
        login_user(user)
        log_info("user", username, "logged in successfully")
        flash('You were logged in. Welcome to the Oracle.')
        return redirect(url_for('dashboard.dashboard'))
    if form.errors:
        flash(
            'Error: '
            + ', '.join(['%s' % value[0] for (key, value) in form.errors.items()])
        )
    return render_template('login.html', form=form)


def format_result(result):
    p = re.compile('CN=(.*?)\,')
    groups = re.sub('CN=Users', '', str(result))
    return p.findall(groups)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out.')
    return redirect(url_for('main.login'))
