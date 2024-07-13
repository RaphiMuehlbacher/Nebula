# server.py
import importlib.util
import os
import re
import socket
import sys
import traceback
from typing import Callable
from urllib.parse import parse_qs
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers.api import BaseObserver

from nebula.utils import HTTPResponse

# Define global settings
HOST, PORT = '', 8080


def load_urlpatterns_from_settings(settings_module_path):
    try:
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

    except KeyboardInterrupt:
        print("hallo")
        sys.exit(0)

    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()

        tb = traceback.TracebackException(exc_type, exc_value, exc_tb)
        print("".join(tb.format_exception_only()))
        return None


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

    except KeyboardInterrupt:
        sys.exit(0)

    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()

        tb = traceback.TracebackException(exc_type, exc_value, exc_tb)
        print("".join(tb.format_exception_only()))


class Request:
    def __init__(self, method, path, form_data=None):
        self.method: str = method
        self.path: str = path
        self.form_data: dict[str, str] = form_data or {}


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, server: "TCPServer"):
        self.server = server

    def on_any_event(self, event: FileSystemEvent) -> None:
        print(f'File {event.src_path} changed. Restarting server...')
        self.server.restart()


class TCPServer:
    def __init__(self, host, port, settings_module_path):
        self.host = host
        self.port = port
        self.settings_module_path = settings_module_path
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        """
        Starts the web server and listens for incoming connections.
        This function binds to the specified host and port, listens for incoming
        connections, and handles each client request in a loop.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        urlpatterns = load_urlpatterns_from_settings(self.settings_module_path)

        observer = Observer()
        event_handler = FileChangeHandler(self)
        observer.schedule(event_handler, path='.', recursive=True)
        observer.start()

        try:
            while True:
                client_connection, client_address = self.server_socket.accept()
                request = client_connection.recv(1024).decode()

                response = handle_request(request, urlpatterns)
                client_connection.sendall(str(response).encode())
                client_connection.close()
        except KeyboardInterrupt:
            print("Shutting down server...")
        finally:
            observer.stop()
            observer.join()
            self.server_socket.close()

    def restart(self):
        """Restarts the server by stopping the current instance and starting a new one."""
        try:
            self.server_socket.close()
            print("Closing server socket...")
        except Exception as e:
            print(f"Error closing server socket: {e}")

        try:
            print("Restarting the server...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(f"Error restarting server: {e}")
            traceback.print_exc()
