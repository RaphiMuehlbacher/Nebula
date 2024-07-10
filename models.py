from web_server.fields import IntegerField, CharField
from web_server.models import Model, QuerySet


class MyModel(Model):
    id = IntegerField()
    name = CharField()


obj = MyModel(name="Raphael Mühlbacher")


obj.save()

queryset = QuerySet(MyModel)
all_objects = queryset.all()
for obj in all_objects:
    print(obj.id, obj.name)


filtered_objects = queryset.filter(name="Raphael Mühlbacher")
for obj in filtered_objects:
    print(obj.id, obj.name)


single_object = queryset.get(id=1)
print(single_object.id, single_object.name)
