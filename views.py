from web_server.fields import IntegerField
from web_server.utils import get_template, get_static, HTTPResponse, render
from tst_models import User


def index():
    return render("index.html")


def user() -> str:
    Raphi = User(age=14, name="Raphi")
    Raphi.save()
    users = User.objects.get(id=1)

    return render("user.html", {"users": users})
