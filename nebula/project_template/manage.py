# manage.py
import argparse
import os

from nebula.commands import start_server

def cli_parser():
    parser = argparse.ArgumentParser(description="Manage your web server.")
    subparser = parser.add_subparsers(dest="command", help="Available commands")

    runserver_parser = subparser.add_parser("runserver", help="Start the web server")
    runserver_parser.add_argument("--host", default="127.0.0.1", help="Host to bind the server")
    runserver_parser.add_argument("--port", default=8080, help="Port to bind the server")

    return parser


def main():
    parser = cli_parser()
    args = parser.parse_args()

    if args.command == "runserver":
        start_server(args.host, args.port)

    else:
        parser.print_help()


if __name__ == "__main__":
    os.environ.setdefault("NEBULA_SETTINGS", "{{ project_name }}\\settings.py")
    main()
