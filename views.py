from utils import get_template, get_static, HTTPResponse, render


def index():
    return render("index.html", {"name": "Raphi"})


def about():
    return render("about.html")


def hello():
    return get_static("hello.txt")


def name(name):
    return HTTPResponse(name)


