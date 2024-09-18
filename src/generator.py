import logging
import time
from typing import Any, Dict
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from .file_scanner import scan_project

class AIReadmeGenerator:
    def __init__(self, api_key: str):
        self.llm = ChatGroq(api_key=api_key)

    def _truncate_list(self, lst, max_items=10):
        if len(lst) > max_items:
            return lst[:max_items] + [f"... and {len(lst) - max_items} more"]
        return lst

    def _prepare_project_info(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "files": self._truncate_list(project_info['files']),
            "directories": self._truncate_list(project_info['directories']),
            "main_file": project_info['main_file'],
            "language": project_info['language'],
            "dependencies": self._truncate_list(project_info['dependencies'])
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(60),  # Wait 60 seconds between attempts
        retry=retry_if_exception_type(Exception)
    )
    def generate_readme_section(self, section_name: str, project_info: Dict[str, Any]) -> str:
        truncated_info = self._prepare_project_info(project_info)
        template = f"""
        Based on the following project information, generate the {section_name} section for a README.md file:
        
        Project files: {truncated_info['files']}
        Project directories: {truncated_info['directories']}
        Main file: {truncated_info['main_file']}
        Project language: {truncated_info['language']}
        Dependencies: {truncated_info['dependencies']}
        
        Generate a concise and informative {section_name} section in Markdown format:
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        
        logging.info(f"Attempting to generate section: {section_name}")
        try:
            result = chain.invoke({"section_name": section_name})
            logging.info(f"Successfully generated section: {section_name}")
            return result
        except Exception as e:
            logging.error(f"Error generating section {section_name}: {str(e)}")
            raise

    def create_readme(self, project_path: str, sections: list) -> str:
        logging.info(f"Scanning project: {project_path}")
        project_info = scan_project(project_path)
        
        readme_content = ""
        for section in sections:
            logging.info(f"Starting generation of section: {section}")
            try:
                section_content = self.generate_readme_section(section, project_info)
                readme_content += f"## {section}\n\n{section_content}\n\n"
                logging.info(f"Successfully added section: {section}")
                time.sleep(60)  # Wait 60 seconds between sections
            except Exception as e:
                logging.error(f"Failed to generate section {section}: {str(e)}")
                readme_content += f"## {section}\n\n[Error generating content for this section]\n\n"
        
        return readme_content