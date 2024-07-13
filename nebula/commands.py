# commands.py
from nebula.server import TCPServer
import os
import importlib.resources


def start_server(host, port):
    project_name = os.getenv('NEBULA_SETTINGS')
    tcpserver = TCPServer(host, port, project_name)
    tcpserver.start()


def start_project(project_name):
    with importlib.resources.path('nebula', 'project_template') as template_dir:
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

        if item == "__pycache__":
            continue

        elif os.path.exists(dst_path):
            raise ValueError(f"{dst_path} already exists")

        elif os.path.isdir(src_path):
            os.makedirs(dst_path, exist_ok=True)
            copy_template_contents(src_path, dst_path, project_name)
        elif item.endswith('.py'):
            with open(src_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                content = template_content.replace("{{ project_name }}", project_name)

            with open(dst_path, 'w', encoding='utf-8') as new_file:
                new_file.write(content)
