import unittest
import unittest.mock as mock

from playhouse.test_utils import test_database
from peewee import *
from datetime import datetime

import app
from models import Entry, User


TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([Entry, User], safe=True)


USER_DATA = {
    'username': 'brianweber2',
    'email': 'test@gmail.com',
    'password': 'test_password',
    'password2': 'test_password'
}

LOGIN_DATA = {
    'email': 'test_0@email.com',
    'password': 'test_password'
}

ENTRY_DATA = {
    'title': 'This is a Test',
    'date': '2016-12-23',
    'time_spent': '40 Hours',
    'learning': 'learning',
    'resources': 'resources',
    'tags': 'entry, test'
}


class UserModelTestCase(unittest.TestCase):
    @staticmethod
    def create_users(count=2):
        for i in range(count):
            User.create_user(
                username='test_user{}'.format(i),
                email='test_{}@email.com'.format(i),
                password='test_password'
            )


    def test_create_user(self):
        with test_database(TEST_DB, (User,)):
            self.create_users()
            self.assertEqual(User.select().count(), 2)
            self.assertNotEqual(User.select().get().password, 'test_password')


    def test_create_duplicate_user(self):
        with test_database(TEST_DB, (User,)):
            self.create_users()
            with self.assertRaises(ValueError):
                User.create_user(
                    username='test_user1',
                    email='test_@email.com',
                    password='password'
                )


class EntryModelTestCase(unittest.TestCase):
    def test_create_entry(self):
        with test_database(TEST_DB, (User, Entry)):
            UserModelTestCase.create_users()
            user = User.select().get()
            Entry.create_entry(
                title=ENTRY_DATA['title'],
                date=ENTRY_DATA['date'],
                time_spent=ENTRY_DATA['time_spent'],
                learning=ENTRY_DATA['learning'],
                resources=ENTRY_DATA['resources'],
                user=user,
                tags=ENTRY_DATA['tags']
            )
            entry = Entry.select().get()

            self.assertEqual(Entry.select().count(), 1)
            self.assertEqual(entry.user, user)


    # def test_get_journal(self):
    #     with test_database(TEST_DB, (User, Entry)):
    #         UserModelTestCase.create_users()
    #         user = User.select().get()
    #         Entry.create_entry(
    #             title=ENTRY_DATA['title'],
    #             date=ENTRY_DATA['date'],
    #             time_spent=ENTRY_DATA['time_spent'],
    #             learning=ENTRY_DATA['learning'],
    #             resources=ENTRY_DATA['resources'],
    #             user=user,
    #             tags=ENTRY_DATA['tags']
    #         )
    #         entries = Entry.select().where(Entry.user == self)
    #         self.assertEqual(entries.count(), 2)


class ViewTestCase(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        app.app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.app.test_client()


class UserViewsTestCase(ViewTestCase):
    def test_registration(self):
        with test_database(TEST_DB, (User,)):
            rv = self.app.post('/register', data=USER_DATA)
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')


    def test_good_login(self):
        with test_database(TEST_DB, (User,)):
            UserModelTestCase.create_users(1)
            rv = self.app.post('/login', data=LOGIN_DATA)
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')


    def test_bad_login(self):
        with test_database(TEST_DB, (User,)):
            rv = self.app.post('/login', data=LOGIN_DATA)
            self.assertEqual(rv.status_code, 200)


    def test_logout(self):
        with test_database(TEST_DB, (User,)):
            UserModelTestCase.create_users(1)
            self.app.post('/login', data=LOGIN_DATA)

            rv = self.app.get('/logout')
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')


    def test_logged_out_menu(self):
        rv = self.app.get('/')
        self.assertIn('login', rv.get_data(as_text=True).lower())
        self.assertIn('register', rv.get_data(as_text=True).lower())


    def test_logged_in_menu(self):
        with test_database(TEST_DB, (User,)):
            UserModelTestCase.create_users(1)
            self.app.post('/login', data=LOGIN_DATA)
            rv = self.app.get('/')
            self.assertIn('new entry', rv.get_data(as_text=True).lower())
            self.assertIn('logout', rv.get_data(as_text=True).lower())


class EntryViewsTestCase(ViewTestCase):
    def test_empty_db(self):
        with test_database(TEST_DB, (User, Entry)):
            UserModelTestCase.create_users(1)
            self.app.post('/login', data=LOGIN_DATA)
            rv = self.app.get('/')
            self.assertIn('click new entry button at the top right corner of '
                'this page to get started', rv.get_data(as_text=True).lower())


    def test_entry_create(self):
        with test_database(TEST_DB, (User, Entry)):
            UserModelTestCase.create_users(1)
            self.app.post('/login', data=LOGIN_DATA)

            ENTRY_DATA['user'] = User.select().get()
            rv = self.app.post('/add', data=ENTRY_DATA)
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')
            self.assertEqual(Entry.select().count(), 1)


if __name__ == '__main__':
    unittest.main()
