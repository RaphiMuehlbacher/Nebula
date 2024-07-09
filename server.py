import socket
import os

from urls import urlpatterns

# Define global settings
HOST, PORT = '', 8080


def handle_request(request):
    """Handles incoming HTTP requests and returns the appropriate response."""
    request_line = request.splitlines()[0]
    request_method, request_path, _ = request_line.split()

    if request_path in urlpatterns.keys():
        return urlpatterns[request_path]

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
