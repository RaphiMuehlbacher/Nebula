import os
from functools import lru_cache

from jinja2 import Environment, FileSystemLoader

STATIC_DIR = 'static'
TEMPLATE_DIR = 'templates'

jinja2_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def render(template_name, context=None):
    if context:
        template = jinja2_env.get_template(template_name)
        return HTTPResponse(template.render(context))
    return get_template(template_name)


def get_template(template_name: str) -> str:
    """Reads an HTML template file."""
    with open(os.path.join(TEMPLATE_DIR, template_name), 'r') as file:
        content = file.read()

    return HTTPResponse(content)


@lru_cache(maxsize=128)
def get_static(file_path: str) -> str:
    path = os.path.join(STATIC_DIR, file_path)
    """Serves static files."""
    if os.path.exists(path) and os.path.isfile(path):
        with open(path, 'r') as file:
            content = file.read()
        return HTTPResponse(content)
    else:
        return not_found_404()


def HTTPResponse(content: str) -> str:
    return f"""\
HTTP/1.1 200 OK

{content}
"""

def not_found_404():
    return """\
HTTP/1.1 404 Not Found

Resource not found
"""

