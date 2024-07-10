class Field:
    def __init__(self, field_type):
        self.field_type = field_type


class IntegerField(Field):
    def __init__(self):
        super().__init__('INTEGER')


class CharField(Field):
    def __init__(self):
        super().__init__('TEXT')
