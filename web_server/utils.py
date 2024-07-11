import os
from functools import lru_cache
from typing import Any

from jinja2 import Environment, FileSystemLoader

STATIC_DIR = 'static'
TEMPLATE_DIR = 'templates'

jinja2_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def render(template_name: str, context: dict[str, Any] = None) -> str:
    """Renders a template with optional context data."""
    if context:
        template = jinja2_env.get_template(template_name)
        return HTTPResponse(template.render(context))
    return get_template(template_name)


def get_template(template_name: str) -> str:
    """Retrieves the content of a template file."""
    with open(os.path.join(TEMPLATE_DIR, template_name), 'r') as file:
        content = file.read()
    return HTTPResponse(content)


@lru_cache(maxsize=128)
def get_static(file_path: str) -> str:
    """Retrieves the content of a static file."""
    path = os.path.join(STATIC_DIR, file_path)
    if os.path.isfile(path):
        with open(path, 'r') as file:
            content = file.read()
        return HTTPResponse(content)
    return not_found_404()


def HTTPResponse(content: str) -> str:
    """Generates a basic HTTP response with a given content."""
    return f"""\
HTTP/1.1 200 OK

{content}
"""


def not_found_404() -> str:
    """ Generates a basic 404 Not Found HTTP response."""
    return """\
HTTP/1.1 404 Not Found

Resource not found
"""

