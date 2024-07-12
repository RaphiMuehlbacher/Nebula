import views
from typing import Callable

from nebula.utils import HTTPResponse

# type hints not necessary
urlpatterns: dict[str, Callable[..., HTTPResponse]] = {
    "/": views.index,
    "/users": views.user
}


