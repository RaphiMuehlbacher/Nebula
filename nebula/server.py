# server.py
import importlib.util
import os
import re
import socket
from typing import Callable
from urllib.parse import parse_qs

from rich.console import Console
from watchdog.events import FileSystemEventHandler

from nebula.utils import HTTPResponse

# Define global settings
HOST, PORT = '', 40000
console = Console()


def load_urlpatterns_from_settings(settings_module_path):
    try:
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

    except Exception:
        console.print_exception()


def get_compiled_urlpatterns(urlpatterns: dict[str, Callable[..., HTTPResponse]]) -> list[tuple[re.Pattern[str], Callable[..., HTTPResponse]]]:
    compiled_urlpatterns = []

    for url_pattern, view_func in urlpatterns.items():
        regex_pattern = re.sub(r"<(\w+)>", r"(?P<\1>[^/]+)", url_pattern)
        regex_pattern = f"^{regex_pattern}$"
        compiled_urlpatterns.append((re.compile(regex_pattern), view_func))
    return compiled_urlpatterns


def handle_request(request: str) -> HTTPResponse:
    try:
        """Handles incoming HTTP requests and returns the appropriate response."""

        request_line = request.splitlines()[0]
        request_method, request_path, _ = request_line.split()

        settings_file = os.getenv("NEBULA_SETTINGS")
        urlpatterns = load_urlpatterns_from_settings(settings_file)
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
            form_data = parse_qs(request_body)
            form_data = {k: v[0] for k, v in form_data.items()}
            for regex_pattern, view_func in compiled_urlpatterns:
                match = regex_pattern.match(request_path)
                if match:
                    kwargs = match.groupdict()
                    request = Request(request_method, request_path, form_data)
                    return view_func(request=request, **kwargs)

            return HTTPResponse("Page not found", 404)

    except Exception:
        console.print_exception()


class Request:
    def __init__(self, method, path, form_data=None):
        self.method: str = method
        self.path: str = path
        self.form_data: dict[str, str] = form_data or {}


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, restart_server):
        super().__init__()
        self.restart_server = restart_server

    def on_modified(self, event):
        if event.src_path.endswith('.py') and not self.should_ignore(event.src_path):
            self.restart_server()

    @staticmethod
    def should_ignore(path: str) -> bool:
        parts = path.split(os.sep)[1:]
        ignore = any(part.startswith('.') or part.startswith('_') for part in parts if part)
        return ignore


class TCPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen()

        print("Listening at", server_socket.getsockname())

        while True:
            client_connection, client_address = server_socket.accept()
            print("Connected to:", client_address)
            request = client_connection.recv(1024).decode()
            if not request:
                continue

            response = handle_request(request)
            client_connection.sendall(str(response).encode())
            client_connection.close()


def start_server():
    tcpserver = TCPServer(HOST, PORT)
    tcpserver.start()
