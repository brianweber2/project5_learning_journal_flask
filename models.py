import datetime

from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
from peewee import *


DATABASE = SqliteDatabase('journal.db')


class Entry(Model):
    title = CharField(max_length=100)
    date = DateField()
    time_spent = CharField(max_length=100)
    learning = TextField()
    resources = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-date',)


    @classmethod
    def create_entry(cls, title, date, time_spent, learning, resources):
        """Creates a new journal entry object."""
        with DATABASE.transaction():
            cls.create(
                title=title,
                date=date,
                time_spent=time_spent,
                learning=learning,
                resources=resources
            )


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin
                )
        except IntegrityError:
            raise ValueError("User already exists!")


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Entry, User], safe=True)
    DATABASE.close()
