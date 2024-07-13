# server.py
import importlib.util
import os
import re
import socket
from typing import Callable
from urllib.parse import parse_qs

from nebula.utils import HTTPResponse

# Define global settings
HOST, PORT = '', 8080


def load_urlpatterns_from_settings(settings_module_path):
    # Import the settings module dynamically
    spec = importlib.util.spec_from_file_location("settings", settings_module_path)
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)

    # Get the URL_CONF path from settings
    url_conf_path = getattr(settings, 'ROOT_URLCONF', None)
    if not url_conf_path:
        raise ImportError(f"URL_CONF not found in {settings_module_path}")

    # Import the URL_CONF module dynamically
    spec = importlib.util.spec_from_file_location("url_conf", url_conf_path)
    url_conf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(url_conf)

    # Ensure urlpatterns is defined in the imported module
    if not hasattr(url_conf, 'urlpatterns'):
        raise ImportError(f"urlpatterns not found in {url_conf_path}")

    return url_conf.urlpatterns


def get_compiled_urlpatterns(urlpatterns: dict[str, Callable[..., HTTPResponse]]) -> list[tuple[re.Pattern[str], Callable[..., HTTPResponse]]]:
    compiled_urlpatterns = []

    for url_pattern, view_func in urlpatterns.items():
        regex_pattern = re.sub(r"<(\w+)>", r"(?P<\1>[^/]+)", url_pattern)
        regex_pattern = f"^{regex_pattern}$"
        compiled_urlpatterns.append((re.compile(regex_pattern), view_func))
    return compiled_urlpatterns


def handle_request(request: str, urlpatterns) -> HTTPResponse:
    """Handles incoming HTTP requests and returns the appropriate response."""

    request_line = request.splitlines()[0]
    print(request)
    request_method, request_path, _ = request_line.split()

    settings_file = os.getenv("NEBULA_SETTINGS")  # e.g mysite.settings
    # i want mysite.settings.URL_CONF
    compiled_urlpatterns = get_compiled_urlpatterns(urlpatterns)

    if request_method == "GET":
        for regex_pattern, view_func in compiled_urlpatterns:
            match = regex_pattern.match(request_path)
            if match:
                kwargs = match.groupdict()
                request = Request(request_method, request_path)
                return view_func(request=request, **kwargs)

        return HTTPResponse("Page not found", 404)

    elif request_method == "POST":
        _, request_body = request.split("\r\n\r\n", 1)
        print("request_body", request_body)
        form_data = parse_qs(request_body)
        form_data = {k: v[0] for k, v in form_data.items()}
        for regex_pattern, view_func in compiled_urlpatterns:
            match = regex_pattern.match(request_path)
            if match:
                kwargs = match.groupdict()
                request = Request(request_method, request_path, form_data)
                return view_func(request=request, **kwargs)

        return HTTPResponse("Page not found", 404)


class Request:
    def __init__(self, method, path, form_data=None):
        self.method: str = method
        self.path: str = path
        self.form_data: dict[str, str] = form_data or {}


class TCPServer:
    def __init__(self, host, port, settings_module_path):
        self.host = host
        self.port = port
        self.settings_module_path = settings_module_path

    def start(self):
        """
        Starts the web server and listens for incoming connections.

        This function binds to the specified host and port, listens for incoming
        connections, and handles each client request in a loop.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()

        urlpatterns = load_urlpatterns_from_settings(self.settings_module_path)

        print("Listening at", server_socket.getsockname())

        while True:
            client_connection, client_address = server_socket.accept()
            print("Connected to:", client_address)
            request = client_connection.recv(1024).decode()

            response = handle_request(request, urlpatterns)
            client_connection.sendall(str(response).encode())
            client_connection.close()


if __name__ == '__main__':
    server = TCPServer(HOST, PORT)
    server.start()

