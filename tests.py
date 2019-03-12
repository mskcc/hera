import unittest
from flask_testing import TestCase
from hera_app import app, db
from hera_app.views.auth import User


class BaseTestCase(TestCase):
    """A base test case."""

    def create_app(self):
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        # app.config[
        #     'SQLALCHEMY_DATABASE_URI'
        # ] = 'mysql+pymysql:/$TESTUSERDB@$HOST/$TESTDB'
        # app.config['SECRET_KEY'] = 'abc'
        # app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False

        return app

    # def setUp(self):
    #     db.create_all()
    #     # db.session.add(User("admin", "ad@min.com", "admin"))
    #     db.session.commit()

    # def tearDown(self):
    #     db.session.remove()
    #     db.drop_all()


class FlaskTestCase(BaseTestCase):

    # Ensure that flask was set up correctly
    def test_index(self):

        response = self.client.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Ensure flask-login redirects correctly
    def test_redirect(self):

        response = self.client.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            b'You should be redirected automatically to target URL' in response.data
        )

    # Ensure login reacts correctly for email as username
    def test_email_as_username(self):
        response = self.client.post(
            '/login', data={'username': 'email@email.com', 'password': '***'}
        )
        self.assertEqual(response.status_code, 401)
        self.assertTrue(
            b'Error: Please use your MSK user ID instead of email address as Username'
            in response.data
        )

    # Ensure login reacts correctly for incorrect creds
    def test_incorrect_creds(self):
        response = self.client.post(
            '/login', data={'username': 'test', 'password': '***'}
        )
        self.assertEqual(response.status_code, 401)
        self.assertTrue(
            b'Error: Invalid username or password. Please try again.' in response.data
        )


if __name__ == '__main__':
    unittest.main()
