import socket

from urls import urlpatterns
from web_server.utils import not_found_404

# Define global settings
HOST, PORT = '', 8080


def handle_request(request: str) -> str:
    """Handles incoming HTTP requests and returns the appropriate response."""
    request_line = request.splitlines()[0]
    print(request_line)
    request_method, request_path, _ = request_line.split()

    if request_path in urlpatterns.keys():
        view_func = urlpatterns[request_path]
        return view_func()

    for url_pattern, view_func in urlpatterns.items():
        if url_pattern.count("<") > 0 and url_pattern.count(">") > 0:
            url_parts = url_pattern.split("/")
            request_parts = request_path.split("/")

            if len(url_parts) == len(request_parts):
                for i in range(len(url_parts)):
                    if url_parts[i].startswith("<") and url_parts[i].endswith(">"):
                        return view_func(request_parts[i])

    return not_found_404()


def start_server():
    """
     Starts the web server and listens for incoming connections.

    This function binds to the specified host and port, listens for incoming
    connections, and handles each client request in a loop.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f'Serving HTTP on port {PORT} ...')

    while True:
        client_connection, client_address = server_socket.accept()
        request = client_connection.recv(1024).decode('utf-8')

        response = handle_request(request)
        client_connection.sendall(response.encode('utf-8'))
        client_connection.close()


if __name__ == '__main__':
    start_server()
