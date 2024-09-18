import os
import json
import sys
from typing import Dict, Any

def scan_project(project_path: str) -> Dict[str, Any]:
    files = []
    directories = []
    main_file = ""
    language = ""
    dependencies = []

    # Scan the project directory
    for root, dirs, filenames in os.walk(project_path):
        for dir in dirs:
            directories.append(os.path.relpath(os.path.join(root, dir), project_path))
        for file in filenames:
            file_path = os.path.relpath(os.path.join(root, file), project_path)
            files.append(file_path)
            
            # Attempt to identify the main file and language
            if file.lower() in ['main.py', 'app.py', 'index.py']:
                main_file = file_path
                language = 'Python'
            elif file.lower() == 'package.json':
                main_file = file_path
                language = 'JavaScript/Node.js'
                # Parse package.json for dependencies
                try:
                    import json
                    with open(os.path.join(root, file), 'r') as f:
                        package_data = json.load(f)
                    dependencies = list(package_data.get('dependencies', {}).keys())
                except:
                    pass
            elif file.lower().endswith('.java'):
                if not main_file:  # Only set if not already set
                    main_file = file_path
                    language = 'Java'

    # If we haven't identified the language, make a guess based on file extensions
    if not language:
        extensions = [os.path.splitext(f)[1] for f in files if os.path.splitext(f)[1]]
        if '.py' in extensions:
            language = 'Python'
        elif '.js' in extensions:
            language = 'JavaScript'
        elif '.java' in extensions:
            language = 'Java'
        else:
            language = 'Unknown'

    # For Python projects, try to parse requirements.txt for dependencies
    if language == 'Python' and 'requirements.txt' in files:
        try:
            with open(os.path.join(project_path, 'requirements.txt'), 'r') as f:
                dependencies = [line.strip().split('==')[0] for line in f if line.strip() and not line.startswith('#')]
        except:
            pass

    return {
        "files": files,
        "directories": directories,
        "main_file": main_file,
        "language": language,
        "dependencies": dependencies
    }

# The main() function has been removed as it's now in run_generator.py