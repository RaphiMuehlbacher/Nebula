from web_server.fields import IntegerField, CharField
from web_server.models import Model


class User(Model):
    age = IntegerField()
    name = CharField()

    def __init__(self, **kwargs):
        self.age = kwargs.get('age', None)
        self.name = kwargs.get('name', None)
        self.id = kwargs.get('id', None)
