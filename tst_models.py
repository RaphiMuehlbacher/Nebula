from web_server.fields import IntegerField, CharField
from web_server.models import Model


class User(Model):
    age = IntegerField()
    name = CharField()


class Book(Model):
    author = CharField()
    length = IntegerField()
