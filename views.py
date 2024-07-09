from utils import get_template, get_static


def index():
    return get_template("index.html")


def about():
    return get_template("about.html")


def hello():
    return get_static("hello.txt")
