import gradio as gr
import os
from dotenv import load_dotenv
from src.ui import create_ui

def main():
    # Load environment variables
    load_dotenv()

    # Check for API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Warning: GROQ_API_KEY not found in environment variables")

    # Create and launch the UI
    try:
        demo = create_ui()
        demo.launch(
            show_error=True, 
            show_api=False,
            # Uncomment the line below if you want public sharing
            # share=True
        )
    except Exception as e:
        print(f"Error launching Gradio app: {e}")

if __name__ == "__main__":
    main()