# serializers.py
class ModelSerializer:
    def __init__(self, instance=None, data=None, many=False):
        self.instance = instance
        self.data = data
        self.many = many
        self.validated_data = {}
        self.Meta = self.get_meta()
        self.model = self.Meta.model
        self.fields = self.Meta.fields or self.model._fields()

    def get_meta(self):
        if hasattr(self, 'Meta'):
            return self.Meta
        raise NotImplementedError('Class Meta is required')

    def is_valid(self):
        if self.many:
            self.validated_data = [self.validate(item) for item in self.data]
        else:
            self.validated_data = self.validate(self.data)
        return bool(self.validated_data)

    def validate(self, data):
        validated_data = {}
        for field in self.fields:
            if field in data:
                validated_data[field] = data[field]
        return validated_data

    def save(self):
        if self.many:
            self.instance = [self.create(item) for item in self.validated_data]
        else:
            if not self.instance:
                self.instance = self.create(self.validated_data)
            else:
                self.instance = self.update(self.instance, self.validated_data)
        return self.instance

    def create(self, validated_data):
        instance = self.model(**validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        if self.many:
            return [self.serialize_object(obj) for obj in instance]
        return self.serialize_object(instance)

    def serialize_object(self, instance):
        ret = {}
        for field in self.fields:
            ret[field] = getattr(instance, field)
        return ret

    def to_internal_value(self, data):
        if self.many:
            return [self.parse_data(item) for item in data]
        return self.parse_data(data)

    def parse_data(self, data):
        ret = {}
        for field in self.fields:
            ret[field] = data.get(field)
        return ret

