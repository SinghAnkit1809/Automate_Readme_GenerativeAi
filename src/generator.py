import logging
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from .file_scanner import scan_project
   
class AIReadmeGenerator:
    def __init__(self, api_key: str):
        self.llm = ChatGroq(api_key=api_key)

    def generate_readme_section(self, section_name: str, project_info: dict) -> str:
        template = f"""
        Based on the following project information, generate the {section_name} section for a README.md file:
        
        Project files: {project_info['files']}
        Project directories: {project_info['directories']}
        Main file: {project_info['main_file']}
        Project language: {project_info['language']}
        Dependencies: {project_info['dependencies']}
        
        Generate a concise and informative {section_name} section in Markdown format:
        """
        
        prompt = PromptTemplate(template=template, input_variables=[])
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run()

    def create_readme(self, project_path: str, sections: list):
        logging.info(f"Scanning project: {project_path}")
        project_info = scan_project(project_path)
        
        readme_content = ""
        for section in sections:
            logging.info(f"Generating section: {section}")
            readme_content += f"## {section}\n\n"
            readme_content += self.generate_readme_section(section, project_info) + "\n\n"
        
        return readme_content