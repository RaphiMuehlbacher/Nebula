import re
import socket
from typing import Callable
from urllib.parse import parse_qs

from urls import urlpatterns

from nebula.utils import HTTPResponse

# Define global settings
HOST, PORT = '', 8080


def get_compiled_urlpatterns(urlpatterns: dict[str, Callable[..., HTTPResponse]]) -> list[tuple[re.Pattern[str], Callable[..., HTTPResponse]]]:
    compiled_urlpatterns = []

    for url_pattern, view_func in urlpatterns.items():
        regex_pattern = re.sub(r"<(\w+)>", r"(?P<\1>[^/]+)", url_pattern)
        regex_pattern = f"^{regex_pattern}$"
        compiled_urlpatterns.append((re.compile(regex_pattern), view_func))
    return compiled_urlpatterns


def handle_request(request: str) -> HTTPResponse:
    """Handles incoming HTTP requests and returns the appropriate response."""

    request_line = request.splitlines()[0]
    print(request)
    request_method, request_path, _ = request_line.split()

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
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start(self):
        """
        Starts the web server and listens for incoming connections.

        This function binds to the specified host and port, listens for incoming
        connections, and handles each client request in a loop.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()

        print("Listening at", server_socket.getsockname())

        while True:
            client_connection, client_address = server_socket.accept()
            print("Connected to:", client_address)
            request = client_connection.recv(1024).decode()

            response = handle_request(request)
            client_connection.sendall(str(response).encode())
            client_connection.close()
            

if __name__ == '__main__':
    server = TCPServer(HOST, PORT)
    server.start()

