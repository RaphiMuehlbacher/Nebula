# commands.py
import shutil
import sys

from nebula.server import TCPServer
from nebula import project_template
import os
import importlib.resources


def start_server(host, port):
    project_name = os.getenv('NEBULA_SETTINGS')
    tcpserver = TCPServer(host, port, project_name)
    print(f"Starting server at {host}:{port}")
    tcpserver.start()


def start_project(project_name):
    # Locate the template directory within the package
    with importlib.resources.path('nebula', 'project_template') as template_dir:
        # Copy all files and directories from template_dir to the new project directory
        copy_template_contents(template_dir, os.getcwd(), project_name)

    os.remove("__init__.py")
    os.rename(os.path.join(os.getcwd(), "project_name"), project_name)
    print(f"Created project '{project_name}' successfully.")


def copy_template_contents(src, dst, project_name):
    """
    Recursively copy template contents to destination directory,
    processing .py-tpl files by substituting placeholders.
    """
    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)

        if os.path.isdir(src_path):
            # Recursively copy directories
            os.makedirs(dst_path, exist_ok=True)
            copy_template_contents(src_path, dst_path, project_name)
        elif item.endswith('.py'):
            with open(src_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                # Example placeholder replacement (customize as per your template format)
                content = template_content.replace("{{ project_name }}", project_name)

            # Write processed content to destination file
            with open(dst_path, 'w', encoding='utf-8') as new_file:
                new_file.write(content)
