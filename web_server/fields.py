class Field:
    """Base class representing a database field."""
    def __init__(self, field_type):
        self.field_type = field_type


class IntegerField(Field):
    """Integer field for the database."""
    def __init__(self):
        super().__init__('INTEGER')


class FloatField(Field):
    """Float field for the database."""
    def __init__(self):
        super().__init__('REAL')


class CharField(Field):
    """Character field for the database."""
    def __init__(self):
        super().__init__('TEXT')
