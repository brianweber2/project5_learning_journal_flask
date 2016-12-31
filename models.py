import datetime

from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
from peewee import *

from slugify import slugify


DATABASE = SqliteDatabase('journal.db')


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


    def get_journal(self):
        """Get all journal entries for a user."""
        return Entry.select().where(Entry.user == self)


    def get_tagged_journals(self, tag):
        """Get all journal entries for a user and a specific tag."""
        return Entry.select().where(
            (Entry.user == self) & Entry.tags.contains(tag))


class Entry(Model):
    title = CharField(max_length=100)
    slug = CharField(max_length=100)
    date = DateField()
    time_spent = CharField(max_length=100)
    learning = TextField()
    resources = TextField()
    user = ForeignKeyField(
        rel_model=User,
        related_name='entries'
    )
    tags = CharField(default="")

    class Meta:
        database = DATABASE
        order_by = ('-date',)


    def __init__(self, *args, **kwargs):
        if not 'slug' in kwargs:
            kwargs['slug'] = slugify(kwargs.get('title', ''))
        super().__init__(*args, **kwargs)


    @classmethod
    def create_entry(cls, title, date, time_spent, learning,
                     resources, user, tags):
        """Creates a new journal entry object."""
        with DATABASE.transaction():
            cls.create(
                title=title,
                date=date,
                time_spent=time_spent,
                learning=learning,
                resources=resources,
                user=user,
                tags=tags
            )


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Entry, User], safe=True)
    DATABASE.close()
