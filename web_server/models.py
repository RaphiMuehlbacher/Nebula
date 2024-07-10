import sqlite3
from typing import Type

from web_server.fields import Field

DATABASE = "db.sqlite3"


class Model:
    def __init__(self, **kwargs):
        for field in self._fields():
            setattr(self, field, kwargs.get(field, None))

    def save(self):
        query = QuerySet(self.__class__)
        fields = ', '.join([f'"{field}"' for field in self._fields() if field != 'id'])
        values = ', '.join([f'"{getattr(self, field)}"' for field in self._fields() if field != 'id'])

        if self.id is None:
            query._cursor.execute(f'INSERT INTO {self.__class__.__name__.lower()} ({fields}) VALUES ({values})')
        else:
            set_clause = ', '.join([f'{field}="{getattr(self, field)}"' for field in self._fields() if field != 'id'])
            query._cursor.execute(f'UPDATE {self.__class__.__name__.lower()} SET {set_clause} WHERE id="{self.id}"')

        query._db.commit()
        if self.id is None:
            self.id = query._cursor.lastrowid

    @classmethod
    def _fields(cls):
        return [field for field in cls.__dict__.keys() if
                not field.startswith('__') and isinstance(getattr(cls, field), Field)]


class QuerySet:
    def __init__(self, model_cls):
        self.model_cls = model_cls
        self._db = sqlite3.connect(DATABASE)
        self._cursor = self._db.cursor()
        self._table = model_cls.__name__.lower()
        self.create_table()

    def create_table(self):
        fields = ['id INTEGER PRIMARY KEY AUTOINCREMENT'] + \
                 [f'{field} {getattr(self.model_cls, field).field_type}' for field in self.model_cls._fields()
                  if field != "id"]
        create_table_query = f'CREATE TABLE IF NOT EXISTS {self._table} ({", ".join(fields)})'
        self._cursor.execute(create_table_query)
        self._db.commit()

    def all(self):
        query = f'SELECT * FROM {self._table}'
        self._cursor.execute(query)
        rows = self._cursor.fetchall()
        return [self.model_cls(**dict(zip(self.model_cls._fields() + ['id'], row))) for row in rows]

    def filter(self, **kwargs):
        conditions = [f'{key}="{value}"' for key, value in kwargs.items()]
        conditions_str = ' AND '.join(conditions)
        query = f'SELECT * FROM {self._table} WHERE {conditions_str}'
        self._cursor.execute(query)
        rows = self._cursor.fetchall()
        return [self.model_cls(**dict(zip(self.model_cls._fields() + ['id'], row))) for row in rows]

    def get(self, **kwargs):
        results = self.filter(**kwargs)
        if len(results) == 1:
            return results[0]
        elif len(results) > 1:
            raise ValueError('Multiple objects returned, expected only one.')
        raise ValueError('Object matching query does not exist.')

