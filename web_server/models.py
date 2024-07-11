import sqlite3

from web_server.fields import Field
from typing import TypeVar

DATABASE = "db.sqlite3"


class QuerySet:
    """Represents a query set for interacting with database models."""
    def __init__(self, model_cls) -> None:
        self.model_cls = model_cls
        self._db = sqlite3.connect(DATABASE)
        self._cursor = self._db.cursor()
        self._table = model_cls.__name__.lower()
        self.create_table()

    def create_table(self) -> None:
        """Create a database table if it does not exist based on the model's fields."""
        fields = ['id INTEGER PRIMARY KEY AUTOINCREMENT'] + \
                 [f'{field} {getattr(self.model_cls, field).field_type}' for field in self.model_cls._fields()
                  if field != "id"]
        create_table_query = f'CREATE TABLE IF NOT EXISTS {self._table} ({", ".join(fields)})'
        self._cursor.execute(create_table_query)
        self._db.commit()

    def all(self):
        """Retrieve all objects from the database table."""
        query = f'SELECT * FROM {self._table} ORDER BY id'
        self._cursor.execute(query)
        rows = self._cursor.fetchall()
        objects = []
        for row in rows:
            field_names = ['id'] + self.model_cls._fields()
            object_data = dict(zip(field_names, row))
            print(object_data)
            user = self.model_cls(**object_data)
            objects.append(user)
        return objects

    def filter(self, **kwargs):
        """Filter objects based on given conditions."""
        conditions = [f'{key}="{value}"' for key, value in kwargs.items()]
        conditions_str = ' AND '.join(conditions)
        query = f'SELECT * FROM {self._table} WHERE {conditions_str}'
        self._cursor.execute(query)
        rows = self._cursor.fetchall()
        return [self.model_cls(**dict(zip(["id"] + self.model_cls._fields(), row))) for row in rows]

    def get(self, **kwargs):
        """Retrieve a single object matching the given conditions."""
        results = self.filter(**kwargs)
        if len(results) == 1:
            return results[0]
        elif len(results) > 1:
            raise ValueError('Multiple objects returned, expected only one.')
        raise ValueError('Object matching query does not exist.')


class ModelMeta(type):
    """
    Metaclass for the base model class.

    This metaclass adds a QuerySet instance to each model class created using it.
    """
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        new_class.objects = QuerySet(new_class)
        return new_class


class Model(metaclass=ModelMeta):
    """
    Base model class representing a database record.

    This class provides methods for interacting with the database.
    """
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', None)
        for field in self._fields():
            setattr(self, field, kwargs.get(field, None))

    def save(self):
        """
        Save the current instance into the database.

        If the instance already exists in the database (i.e., has an id), it will update the existing record;
        otherwise, it will insert a new record.
        """
        query = QuerySet(self.__class__)
        fields = ', '.join([f'"{field}"' for field in self._fields() if field != 'id'])
        values = ', '.join([f'"{getattr(self, field)}"' for field in self._fields() if field != 'id'])

        if self.id is None:
            query._cursor.execute(f'INSERT INTO {self.__class__.__name__.lower()} ({fields}) VALUES ({values})')
            query._db.commit()
            self.id = query._cursor.lastrowid  # Set the id after inserting
        else:
            set_clause = ', '.join([f'{field}="{getattr(self, field)}"' for field in self._fields() if field != 'id'])
            query._cursor.execute(f'UPDATE {self.__class__.__name__.lower()} SET {set_clause} WHERE id="{self.id}"')
            query._db.commit()

    @classmethod
    def _fields(cls):
        """Retrieve a list of field names for the model class."""
        return [field for field in cls.__dict__.keys() if
                not field.startswith('__') and isinstance(getattr(cls, field), Field)]


