# server.py
import importlib.util
import os
import re
import socket
import sys
from typing import Callable
from urllib.parse import parse_qs
import socketserver

from rich.console import Console
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from nebula.utils import HTTPResponse

# Define global settings
HOST, PORT = '', 8080
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


def handle_request(request: str, urlpatterns) -> HTTPResponse:
    try:
        """Handles incoming HTTP requests and returns the appropriate response."""

        request_line = request.splitlines()[0]
        request_method, request_path, _ = request_line.split()

        settings_file = os.getenv("NEBULA_SETTINGS")
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
    def __init__(self, server: "MyTCPServer"):
        self.server = server

    def on_any_event(self, event: FileSystemEvent) -> None:
        if not self.should_ignore(event.src_path):
            print(f'File {event.src_path} changed. Restarting server...')
            self.server.restart()

    @staticmethod
    def should_ignore(path: str) -> bool:
        parts = path.split(os.sep)[1:]
        ignore = any(part.startswith('.') for part in parts if part)
        return ignore


class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            request = self.request.recv(1024).decode().strip()
            response = handle_request(request, self.server.urlpatterns)
            self.request.sendall(str(response).encode())
        except Exception:
            console.print_exception()
            response = HTTPResponse("Internal Server Error", 500)
            self.request.sendall(str(response).encode())


class MyTCPServer(socketserver.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, settings_module_path):
        self.settings_module_path = settings_module_path
        self.urlpatterns = load_urlpatterns_from_settings(settings_module_path)
        super().__init__(server_address, RequestHandlerClass)

    def restart(self):
        self.server_close()
        print(f"""
Starting development server at http://{self.server_address[0]}:{self.server_address[1]}/
Quit the server with CTRL-BREAK.
""")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def start_observer(self):
        event_handler = FileChangeHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, path='.', recursive=True)
        self.observer.start()

    def serve_forever(self):
        self.start_observer()
        try:
            super().serve_forever()
        except KeyboardInterrupt:
            print("Shutting down server...")
        finally:
            self.cleanup()

    def cleanup(self):
        if hasattr(self, 'observer'):
            self.observer.stop()
            self.observer.join()
