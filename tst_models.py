from nebula.fields import IntegerField, CharField
from nebula.models import Model


class User(Model):
    age = IntegerField()
    name = CharField()


class Book(Model):
    author = CharField()
    length = IntegerField()
