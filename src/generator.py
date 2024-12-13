import logging
import os
import re
from typing import Any, Dict, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .file_scanner import quick_scan_project

class AIReadmeGenerator:
    def __init__(self, api_key: str):
        self.llm = ChatGroq(
            api_key=api_key, 
            model_name="llama3-70b-8192"
        )

    def read_file_content(self, file_path: str) -> str:
        """
        Read the content of a file, handling different encodings and file sizes.
        
        Args:
            file_path (str): Path to the file to read
        
        Returns:
            str: File content or error message
        """
        try:
            # Limit file reading to prevent memory issues
            with open(file_path, 'r', encoding='utf-8') as file:
                # Read first 10000 characters to prevent large files from overwhelming the system
                return file.read(10000)
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"

    def analyze_project_structure(self, project_path: str) -> Dict[str, Any]:
        """
        Perform a comprehensive analysis of the project.
        
        Args:
            project_path (str): Path to the project directory
        
        Returns:
            Dict: Detailed project analysis
        """
        # Use existing quick_scan_project for initial analysis
        project_info = quick_scan_project(project_path)
        
        # Collect file contents
        file_contents = {}
        for file in project_info.get('files', []):
            full_path = os.path.join(project_path, file)
            if os.path.isfile(full_path):
                file_contents[file] = self.read_file_content(full_path)
        
        # Extract docstrings and comments from main files
        code_insights = {}
        main_files = ['app.py', 'main.py', 'src/ui.py', 'src/generator.py']
        for main_file in main_files:
            full_path = os.path.join(project_path, main_file)
            if os.path.exists(full_path):
                code_insights[main_file] = self.extract_code_insights(full_path)
        
        # Combine all information
        comprehensive_analysis = {
            "project_structure": project_info,
            "file_contents": file_contents,
            "code_insights": code_insights,
            "requirements": self.read_requirements(project_path)
        }
        
        return comprehensive_analysis

    def extract_code_insights(self, file_path: str) -> Dict[str, str]:
        """
        Extract insights from Python files.
        
        Args:
            file_path (str): Path to the Python file
        
        Returns:
            Dict: Extracted insights including docstrings, key functions, etc.
        """
        insights = {
            "module_docstring": "",
            "key_functions": [],
            "key_classes": []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # Extract module-level docstring
                module_docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                if module_docstring_match:
                    insights['module_docstring'] = module_docstring_match.group(1).strip()
                
                # Find key functions
                function_matches = re.findall(r'def\s+(\w+)\(.*?\):\s*"""(.*?)"""', content, re.DOTALL)
                insights['key_functions'] = [
                    f"{name}: {desc.strip()}" 
                    for name, desc in function_matches
                ]
                
                # Find key classes
                class_matches = re.findall(r'class\s+(\w+).*?:\s*"""(.*?)"""', content, re.DOTALL)
                insights['key_classes'] = [
                    f"{name}: {desc.strip()}" 
                    for name, desc in class_matches
                ]
        except Exception as e:
            insights['error'] = str(e)
        
        return insights

    def read_requirements(self, project_path: str) -> List[str]:
        """
        Read project requirements file.
        
        Args:
            project_path (str): Path to the project directory
        
        Returns:
            List[str]: List of requirements
        """
        try:
            req_path = os.path.join(project_path, 'requirements.txt')
            if os.path.exists(req_path):
                with open(req_path, 'r') as f:
                    return [line.strip() for line in f if line.strip() and not line.startswith('#')]
            return []
        except Exception:
            return []

    def generate_concise_readme(self, project_path: str) -> str:
        """
        Generate a README based on comprehensive project analysis.
        
        Args:
            project_path (str): Path to the project directory
        
        Returns:
            str: Generated README content
        """
        # Analyze the project comprehensively
        project_analysis = self.analyze_project_structure(project_path)
        
        # Prepare a detailed prompt for the LLM
        template = """
        Generate a comprehensive README.md based on the following project analysis:

        PROJECT STRUCTURE:
        {project_structure}

        FILE CONTENTS:
        {file_contents}

        CODE INSIGHTS:
        {code_insights}

        REQUIREMENTS:
        {requirements}

        Based on this information, create a professional, detailed README.md that:
        - Explains the project's purpose and functionality
        - Describes key features and components
        - Provides clear setup and usage instructions
        - Highlights technical details
        - Includes any relevant dependencies or prerequisites

        Ensure the README is informative, well-structured, and tailored to the specific project.
        """

        # Prepare context for the LLM
        context = {
            "project_structure": str(project_analysis.get('project_structure', 'No structure information')),
            "file_contents": '\n'.join([f"{k}:\n{v}" for k, v in project_analysis.get('file_contents', {}).items()]),
            "code_insights": '\n'.join([f"{k}:\n{str(v)}" for k, v in project_analysis.get('code_insights', {}).items()]),
            "requirements": '\n'.join(project_analysis.get('requirements', []))
        }

        try:
            # Generate README using LLM
            prompt = ChatPromptTemplate.from_template(template)
            chain = prompt | self.llm | StrOutputParser()
            
            readme_content = chain.invoke(context)
            return readme_content.strip()
        except Exception as e:
            logging.error(f"README generation error: {str(e)}")
            return f"# Project README\n\nUnable to generate README automatically.\n\nError: {str(e)}"