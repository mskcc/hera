import ldap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired
from flask_login import UserMixin
from hera_app import app, db

ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

def get_ldap_connection():
    conn = ldap.initialize(app.config['AUTH_LDAP_URL'])
    conn.set_option(ldap.OPT_REFERRALS, 0)    
    return conn

class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(40), nullable=True)
    username = db.Column(db.String(40), nullable=False, unique=True)
    msk_group = db.Column(db.String(40), nullable=True)
    role = db.Column(db.String(40), nullable=True)

    def __init__(self, username, full_name=None, msk_group=None, role='user'):
        self.username = username
        self.msk_group = msk_group 
        self.role = role 
        self.full_name = full_name 

    @staticmethod
    def try_login(username, password):
        conn = get_ldap_connection()

        conn.simple_bind_s('%s@mskcc.org' % username, password)
        # attrs = ['memberOf']
        # attrs = ['sAMAccountName', 'displayName', 'memberOf', 'title']
        # result = conn.search_s(
        #     'DC=MSKCC,DC=ROOT,DC=MSKCC,DC=ORG',
        #     ldap.SCOPE_SUBTREE,
        #     'sAMAccountName=wagnerl',
        #     attrs,
        # )
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
        return str(self.id)

    def get_user_name(self):
        return str(self.user_name)

    def get_full_name(self):
        return str(self.full_name)

    def get_msk_group(self):
        return str(self.msk_group)

    def get_role(self):
        return str(self.role)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {'id': self.id, 'username': self.username, 'msk_group': self.msk_group, 'role': self.role}

class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired('MSK username is required')])
    password = PasswordField('Password', [InputRequired('Password is required')])
