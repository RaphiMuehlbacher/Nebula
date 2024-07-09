import os

STATIC_DIR = 'static'
TEMPLATE_DIR = 'templates'


def get_template(template_name: str) -> str:
    """Reads an HTML template file."""
    with open(os.path.join(TEMPLATE_DIR, template_name), 'r') as file:
        content = file.read()

    return f"""HTTP/1.1 200 OK

{content}
"""


def get_static(file_path: str) -> str:
    path = os.path.join(STATIC_DIR, file_path)
    """Serves static files."""
    if os.path.exists(path):
        with open(path, 'r') as file:
            content = file.read()
        return f"""HTTP/1.1 200 OK

{content}
"""
    else:
        return """HTTP/1.1 404 Not Found

File not found
"""


def HTTPResponse(content: str) -> str:
    return f"""HTTP/1.1 200 OK

{content}
"""

def not_found_404():
    return """HTTP/1.1 404 Not Found

Resource not found
"""

