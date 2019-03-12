SECRET_KEY = ***
WTF_CSRF_SECRET_KEY = ***
AUTH_LDAP_URL = 'ldaps://ldapha.mskcc.root.mskcc.org/'

SQLALCHEMY_DATABASE_URI = "mysql+pymysql:://$USER:$PW@&HOST:$PORT/$DB"

# explicitly disabling according to SQLAlchemy's docs
SQLALCHEMY_TRACK_MODIFICATIONS = False

# docker ldap
# AUTH_LDAP_URL = 'ldap://localhost/:389'
