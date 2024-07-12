# commands.py
import shutil

from nebula.server import TCPServer
import importlib.resources as pkg_resources
import os


def start_server(host, port):
    tcpserver = TCPServer(host, port)
    print(f"Starting server at {host}:{port}")
    tcpserver.start()


def start_project(project_name):
    # Create a new directory for the project
    try:
        os.makedirs(project_name)
    except FileExistsError:
        print(f"Directory '{project_name}' already exists.")
        return

    # Locate the template directory within the package
    with pkg_resources.path('nebula', 'project_template') as template_dir:
        # Copy initial project files/templates to the new directory
        for root, dirs, files in os.walk(template_dir):
            # Skip __pycache__ and any other unwanted directories
            dirs[:] = [d for d in dirs if d != '__pycache__']

            for file in files:
                src = os.path.join(root, file)
                relative_path = os.path.relpath(src, template_dir)
                dst = os.path.join(project_name, relative_path)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(src, dst)

    print(f"Created project '{project_name}' successfully.")

