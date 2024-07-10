import views
from typing import Callable

# type hints not necessary
urlpatterns: dict[str, Callable[..., str]] = {
    "/": views.index,
    "/users": views.user
}


