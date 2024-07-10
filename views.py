from web_server.utils import get_template, get_static, HTTPResponse, render
from tst_models import User


def index():
    return render("index.html")


def user():
    Raphi = User(age=13, name="Raphi")
    Raphi.save()
    users = User.objects.all()
    for user in users:
        print("name", user.name)
        print("age", user.age)
        print("id", user.id)
    return render("user.html", {"users": users})


