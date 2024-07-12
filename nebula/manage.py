# manage.py
import argparse

from nebula.commands import start_project


def cli_parser():
    parser = argparse.ArgumentParser(description="Manage your web server.")
    subparser = parser.add_subparsers(dest="command", help="Available commands")

    start_project = subparser.add_parser("startproject", help="Create a new project")
    start_project.add_argument("projectname", help="Name of the project")

    return parser


def main():
    parser = cli_parser()
    args = parser.parse_args()

    if args.command == "startproject":
        start_project(args.projectname)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
