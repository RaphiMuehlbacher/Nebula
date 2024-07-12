from web_server.fields import IntegerField
from web_server.utils import get_template, get_static, HTTPResponse, render
from tst_models import User


def index():
    return render("index.html")


def user(name, age, moin) -> str:
    print(name, age, moin)
    users = User.objects.filter(name=name, age=age)
    return render("user.html", {"users": users})
