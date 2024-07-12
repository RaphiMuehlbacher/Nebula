import views
from typing import Callable

from web_server.utils import HTTPResponse

# type hints not necessary
urlpatterns: dict[str, Callable[..., HTTPResponse]] = {
    "/": views.index,
    "/users": views.user
}


