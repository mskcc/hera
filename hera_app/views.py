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
)

from functools import wraps

from hera_app import app
from hera_app.auth import User, LoginForm


def get_ldap_connection():
    conn = ldap.initialize(app.config['AUTH_LDAP_URL'])
    conn.set_option(ldap.OPT_REFERRALS, 0)
    return conn


def log_error(*args):
    print("DELPHI_ERROR:"),
    for arg in args:
        print(arg),
    print()


def log_info(*args):
    print("DELPHI_INFO:"),
    for arg in args:
        print(arg),
    print()


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))

    return wrap


# @login_manager.user_loader
# def load_user(userid):
#     try:
#         #: Flask Peewee used here to return the user object
#         return User.get(User.id==userid)
#     except User.DoesNotExist:
#         return None


@app.route('/')
@login_required
def index():
    print(current_user)
    return render_template('index.html')  # render a template
    # return "Hello, World!"  # return a string


@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        flash('Error: You are already logged in')

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
            return render_template('login.html', form=form)

        try:
            conn = get_ldap_connection()
            conn.simple_bind_s('%s@mskcc.org' % username, password)
            # conn.simple_bind_s('cn=%s,dc=example,dc=org' % username, password)
            attrs = ['memberOf']
            # attrs = ['sAMAccountName', 'displayName', 'memberOf', 'title']
            result = conn.search_s(
                'DC=MSKCC,DC=ROOT,DC=MSKCC,DC=ORG',
                ldap.SCOPE_SUBTREE,
                'sAMAccountName=wagnerl',
                attrs,
            )
            print(result)
            conn.unbind_s()

            p = re.compile('CN=(.*?)\,')
            m = re.sub('CN=Users', '', str(result))
            m = p.findall(m)
            print(m)

        except ldap.INVALID_CREDENTIALS:
            log_error("user", username, "trying to login with invalid credentials")
            flash('Error: Invalid username or password. Please try again.')
            return render_template('login.html', form=form)

        log_info("user", username, "logged in successfully")
        flash('You were logged in.')
        session['logged_in'] = True
        session['username'] = username
        session['groups'] = m
        return redirect(url_for('home'))
    if form.errors:
        return jsonify(
            {
                'type': 'error',
                'msg': 'Error: '
                + ', '.join(['%s' % value[0] for (key, value) in form.errors.items()]),
            }
        )
    # return render_template('login.html', form=form, next=get_redirect_target())
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('home'))


@app.route('/tables')
@login_required
def tables():
    return render_template('tables.html')
