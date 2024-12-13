import os
import gradio as gr
import tempfile
import zipfile
from dotenv import load_dotenv
from .generator import AIReadmeGenerator

def generate_readme(project_folder):
    """
    Generate a user-friendly README for the uploaded project.
    """
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return "Error: GROQ_API_KEY not found in environment variables.", "Error: GROQ_API_KEY not found in environment variables."
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Extract uploaded ZIP file
            with zipfile.ZipFile(project_folder, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Generate the README
            generator = AIReadmeGenerator(api_key)
            readme_content = generator.generate_concise_readme(temp_dir)
            
            # Return the same content for both plain text and markdown
            return readme_content, readme_content
        except zipfile.BadZipFile:
            error_message = "Error: Uploaded file is not a valid ZIP archive."
            return error_message, error_message
        except Exception as e:
            error_message = f"Error generating README: {str(e)}"
            return error_message, error_message

def create_ui():
    """
    Create Gradio interface for the README Generator.
    """
    with gr.Blocks(title="AI README Generator") as demo:
        # Header Section
        with gr.Row(elem_id="header-row"):
            gr.Markdown(
                """
                # 🚀 AI README Generator
                Easily generate a well-structured README.md for your project by uploading a ZIP file of your codebase.
                """
            )

        # Upload Section
        with gr.Row(elem_id="upload-row", equal_height=True):
            with gr.Column():
                folder_input = gr.File(file_count="single", type="filepath", label="📂 Upload Your Project (ZIP)")
            with gr.Column():
                generate_btn = gr.Button("✨ Generate README", elem_id="generate-btn")

        # Output Section
        with gr.Row(elem_id="output-row", equal_height=False):
            with gr.Column():
                gr.Markdown("### 📝 Generated README.md (Plain Text)", elem_id="plain-text-label")
                readme_output = gr.Textbox(lines=20, interactive=False, elem_id="readme-output")
            with gr.Column():
                gr.Markdown("### 📄 README.md (Markdown Preview)", elem_id="markdown-preview-label")
                readme_markdown = gr.Markdown(elem_id="readme-markdown")

        # Button Functionality
        generate_btn.click(
            generate_readme, 
            inputs=[folder_input], 
            outputs=[readme_output, readme_markdown]
        )

    return demo

