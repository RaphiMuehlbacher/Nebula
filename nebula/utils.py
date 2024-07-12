import os
from functools import lru_cache
from typing import Any

from jinja2 import Environment, FileSystemLoader

STATIC_DIR = 'static'
TEMPLATE_DIR = 'templates'

jinja2_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


class HTTPResponse:
    """Generates a basic HTTP response with a given content."""
    def __init__(self, content: str, status_code: int = 200, headers: dict = None):
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}

    def __str__(self) -> str:
        status_text = {200: "OK", 404: "Not Found", 405: "Method Not Allowed", 500: "Internal Server Error"}
        response_lines = [
            f"HTTP/1.1 {self.status_code} {status_text[self.status_code]}"
        ] + [f"{k}: {v}" for k, v in self.headers.items()] + ["", self.content]
        return "\r\n".join(response_lines)


def render(template_name: str, context: dict[str, Any] = None) -> HTTPResponse:
    """Renders a template with optional context data."""
    if context:
        template = jinja2_env.get_template(template_name)
        return HTTPResponse(template.render(context))
    return get_template(template_name)


def get_template(template_name: str) -> HTTPResponse:
    """Retrieves the content of a template file."""
    with open(os.path.join(TEMPLATE_DIR, template_name), 'r') as file:
        content = file.read()
    return HTTPResponse(content)


@lru_cache(maxsize=128)
def get_static(file_path: str) -> HTTPResponse:
    """Retrieves the content of a static file."""
    path = os.path.join(STATIC_DIR, file_path)
    if os.path.isfile(path):
        with open(path, 'r') as file:
            content = file.read()
        return HTTPResponse(content)
    return HTTPResponse("Resource not found", 404)
