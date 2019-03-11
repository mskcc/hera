import ldap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired
from flask_login import UserMixin
from hera_app import app


def get_ldap_connection():
    conn = ldap.initialize(app.config['AUTH_LDAP_URL'])
    conn.set_option(ldap.OPT_REFERRALS, 0)
    return conn




class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username
       

    @staticmethod
    def try_login(username, password):
        conn = get_ldap_connection()
        # conn.simple_bind_s('%s@mskcc.org' % username, password)
        conn.simple_bind_s('cn=%s,dc=example,dc=org' % username, password)

        conn.unbind_s()

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return True

    def get_id(self):
        return unicode(self.id)


class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired('Username is required')])
    password = PasswordField('Password', [InputRequired('Password is required')])
