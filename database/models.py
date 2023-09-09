from peewee import *
from playhouse.sqliteq import SqliteQueueDatabase

db = SqliteQueueDatabase('database.db')


class User(Model):
    tg_id = IntegerField(primary_key=True, unique=True)
    tg_nickname = CharField()
    balance = DecimalField(decimal_places=2)
    referrer = IntegerField(null=True)

    class Meta:
        db_table = 'Users'
        database = db


class Order(Model):
    id = IntegerField(primary_key=True, unique=True, null=False)
    sim5_id = CharField(unique=True, null=False)
    user = ForeignKeyField(User.tg_id, backref='orders')
    service = CharField()
    country = CharField()
    operator = CharField()
    phone_number = CharField(null=True)
    price = DecimalField(decimal_places=2)
    status = CharField()

    class Meta:
        db_table = 'Orders'
        database = db


def connect():
    print('conn')
    db.connect()
    db.create_tables([User, Order])

