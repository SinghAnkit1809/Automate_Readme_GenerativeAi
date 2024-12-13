import os
import json
import re
from typing import Dict, Any

def analyze_code_for_purpose(file_path: str) -> str:
    """
    Analyze a Python file to extract purpose from docstrings or comments.
    """
    purpose = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            # Extract comments or docstrings from the first 30 lines
            for line in lines[:30]:
                # Match docstrings or comments
                if re.match(r'^\s*#', line) or re.match(r'^\s*"""', line):
                    purpose.append(line.strip("# ").strip('"""').strip())
    except Exception:
        pass
    return " ".join(purpose)[:250]  # Limit to 250 characters

def quick_scan_project(project_path: str) -> Dict[str, Any]:
    """
    Perform a detailed scan of the project directory, including purpose analysis.
    """
    def get_all_files_and_dirs(path):
        files = []
        dirs = []
        for root, directories, filenames in os.walk(path):
            for file in filenames:
                files.append(os.path.relpath(os.path.join(root, file), path))
            for dir in directories:
                dirs.append(os.path.relpath(os.path.join(root, dir), path))
        return {
            'files': files[:10],  # Limit to 10 for concise output
            'directories': dirs[:10]
        }

    scan_result = get_all_files_and_dirs(project_path)
    top_level_files = os.listdir(project_path)

    # Detect language and main file
    main_files = {
        'Python': ['main.py', 'app.py', 'index.py'],
        'JavaScript': ['index.js', 'app.js', 'server.js'],
        'Java': ['Main.java', 'App.java']
    }

    language = 'Unknown'
    main_file = ''
    project_purpose = ''
    for lang, possible_mains in main_files.items():
        for main in possible_mains:
            if main in top_level_files:
                language = lang
                main_file = main
                project_purpose = analyze_code_for_purpose(os.path.join(project_path, main))
                break
        if language != 'Unknown':
            break

    # Detect dependencies
    dependencies = []
    try:
        if 'requirements.txt' in top_level_files:
            with open(os.path.join(project_path, 'requirements.txt'), 'r') as f:
                dependencies = [line.strip().split('==')[0] for line in f 
                                if line.strip() and not line.startswith('#')][:5]
        elif 'package.json' in top_level_files:
            with open(os.path.join(project_path, 'package.json'), 'r') as f:
                package_data = json.load(f)
                dependencies = list(package_data.get('dependencies', {}).keys())[:5]
    except Exception:
        pass

    return {
        "files": scan_result['files'],
        "directories": scan_result['directories'],
        "main_file": main_file or "Main file not detected",
        "language": language,
        "dependencies": dependencies or ["No dependencies detected"],
        "purpose": project_purpose or "No purpose detected from the code"
    }
