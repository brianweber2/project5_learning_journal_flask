import datetime

from peewee import *


DATABASE = SqliteDatabase('journal.db')


class Entry(Model):
    title = CharField(max_length=100)
    date = DateTimeField(default=datetime.datetime.now)
    time = IntegerField()
    notes = TextField()
    resources = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-date',)


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Entry], safe=True)
    DATABASE.close()
