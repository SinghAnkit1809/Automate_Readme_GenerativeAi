import os
def scan_project(project_path: str) -> dict:
    project_info = {
        "files": [],
        "directories": [],
        "main_file": None,
        "language": None,
        "dependencies": set(),
    }
    for root, dirs, files in os.walk(project_path):
        rel_path = os.path.relpath(root, project_path)
        if rel_path != '.':
            project_info["directories"].append(rel_path)
        for file in files:
            file_path = os.path.join(rel_path, file)
            project_info["files"].append(file_path)
            if file.lower() in ('main.py', 'index.js', 'app.py', 'server.js'):
                project_info["main_file"] = file_path
            if file.endswith('.py'):
                project_info["language"] = "Python"
                scan_python_dependencies(os.path.join(root, file), project_info["dependencies"])
            elif file.endswith('.js'):
                project_info["language"] = "JavaScript"
                scan_js_dependencies(os.path.join(root, file), project_info["dependencies"])
    project_info["dependencies"] = list(project_info["dependencies"])
    return project_info
def scan_python_dependencies(file_path: str, dependencies: set):
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip().startswith('import') or line.strip().startswith('from'):
                parts = line.split()
                if parts[0] == 'from':
                    dependencies.add(parts[1].split('.')[0])
                else:
                    dependencies.add(parts[1].split('.')[0])
def scan_js_dependencies(file_path: str, dependencies: set):
    with open(file_path, 'r') as file:
        for line in file:
            if 'require(' in line:
                start = line.index('require(') + 9
                end = line.index(')', start)
                module = line[start:end].strip('\'"')
                if not module.startswith('.'):
                    dependencies.add(module)