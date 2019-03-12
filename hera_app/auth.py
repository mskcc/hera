import ldap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired
from flask_login import UserMixin
from hera_app import app, db


def get_ldap_connection():
    conn = ldap.initialize(app.config['AUTH_LDAP_URL'])
    conn.set_option(ldap.OPT_REFERRALS, 0)
    return conn


class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), nullable=False)
    groups = db.Column(db.Text, nullable=False)

    def __init__(self, username, groups):
        self.username = username
        self.groups = groups

    @staticmethod
    def try_login(username, password):
        conn = get_ldap_connection()

        conn.simple_bind_s('%s@mskcc.org' % username, password)
        attrs = ['memberOf']
        # attrs = ['sAMAccountName', 'displayName', 'memberOf', 'title']
        result = conn.search_s(
            'DC=MSKCC,DC=ROOT,DC=MSKCC,DC=ORG',
            ldap.SCOPE_SUBTREE,
            'sAMAccountName=wagnerl',
            attrs,
        )
        conn.unbind_s()
        return result

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
        return str(self.id)

    def get_groups(self):
        return str(self.groups)


class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired('Username is required')])
    password = PasswordField('Password', [InputRequired('Password is required')])
