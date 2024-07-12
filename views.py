from web_server.fields import IntegerField
from web_server.utils import get_template, get_static, HTTPResponse, render
from tst_models import User


def index(request):
    if request.method == "GET":
        return render("index.html")
    elif request.method == "POST":
        form_data = request.form_data
        user = User(name=form_data["username"], age=15)
        user.save()
        return HTTPResponse(form_data)


def user(request) -> str:
    users = User.objects.all()
    return render("user.html", {"users": users})
