import re
import socket
from typing import Callable

from urls import urlpatterns
from web_server.utils import not_found_404, HTTPResponse

# Define global settings
HOST, PORT = '', 8080


def get_compiled_urlpatterns(urlpatterns: dict[str, Callable[..., str]]):
    compiled_urlpatterns = []

    for url_pattern, view_func in urlpatterns.items():
        regex_pattern = re.sub(r"<(\w+)>", r"(?P<\1>[^/]+)", url_pattern)
        regex_pattern = f"^{regex_pattern}$"
        compiled_urlpatterns.append((re.compile(regex_pattern), view_func))
    return compiled_urlpatterns


def handle_request(request: str) -> str:
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
                return view_func(**kwargs)

        return not_found_404()

    elif request_method == "POST":
        _, request_body = request.split("\r\n\r\n", 1)
        print(request_body)
        pass


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
        server_socket.listen(5)

        print("Listening at", server_socket.getsockname())

        while True:
            client_connection, client_address = server_socket.accept()
            print("Connected to:", client_address)
            request = client_connection.recv(1024).decode()

            response = handle_request(request)
            client_connection.sendall(response.encode())
            client_connection.close()


if __name__ == '__main__':
    tcpserver = TCPServer(HOST, PORT)
    tcpserver.start()
