import socket
import os

# Define global settings
HOST, PORT = '', 8080
STATIC_DIR = 'static'
TEMPLATE_DIR = 'templates'

# Define a simple routing table
ROUTES = {}

def route(path):
    """Decorator to register a route."""
    def decorator(func):
        ROUTES[path] = func
        return func
    return decorator


def template(template_name):
    """Reads an HTML template file."""
    with open(os.path.join(TEMPLATE_DIR, template_name), 'r') as file:
        content = file.read()

    return f"""HTTP/1.1 200 OK

    {content}
    """
def static_file_response(file_path):
    """Serves static files."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return f"""HTTP/1.1 200 OK

{content}
"""
    else:
        return """HTTP/1.1 404 Not Found

File not found
"""

@route('/')
def index():
    return template("index.html")


@route('/static/<path>')
def static_files(path):
    """Handler for static files."""
    return static_file_response(path)

def handle_request(request):
    """Handles incoming HTTP requests and returns the appropriate response."""
    request_line = request.splitlines()[0]
    request_method, path, _ = request_line.split()

    # Check for static file requests
    if path.startswith('/static/'):
        file_path = path.lstrip('/')
        return static_file_response(file_path)

    # Route to the appropriate view function
    for route_path, view_func in ROUTES.items():
        if route_path == path or route_path.startswith('/static/') and path.startswith(route_path[:-1]):
            return view_func()

    # Default 404 response
    return """HTTP/1.1 404 Not Found

Resource not found
"""

def start_server():
    """Starts the web server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f'Serving HTTP on port {PORT} ...')

    while True:
        client_connection, client_address = server_socket.accept()
        request = client_connection.recv(1024).decode('utf-8')
        print(request)

        response = handle_request(request)
        client_connection.sendall(response.encode('utf-8'))
        client_connection.close()

if __name__ == '__main__':
    start_server()
