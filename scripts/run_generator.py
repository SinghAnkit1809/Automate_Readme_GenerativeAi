import argparse
import os
import sys
import logging
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.generator import AIReadmeGenerator
from src.utils import setup_logging, load_config

def main():
    load_dotenv()  # Load environment variables from .env file
    setup_logging(level=logging.INFO)  # Set logging level to INFO for less verbose output

    parser = argparse.ArgumentParser(description="Generate README.md using AI")
    parser.add_argument("project_path", help="Path to the project directory", type=str)
    parser.add_argument("--config", default="config/default_config.yaml", help="Path to configuration file")
    args = parser.parse_args()

    print("Starting README generation process...")

    try:
        config = load_config(args.config)
        print(f"Successfully loaded configuration from {args.config}")
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        sys.exit(1)

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("GROQ_API_KEY not found in environment variables")
        sys.exit(1)

    try:
        print("Initializing AIReadmeGenerator...")
        generator = AIReadmeGenerator(api_key=api_key)
        
        print(f"Starting README creation for project: {args.project_path}")
        print("This process may take several minutes due to API rate limiting. Please be patient.")
        readme_content = generator.create_readme(args.project_path, config['sections'])

        readme_path = os.path.join(args.project_path, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        print(f"README.md created successfully at {readme_path}")
        print("Please review the generated README and make any necessary adjustments.")
    except Exception as e:
        print(f"An error occurred while generating the README: {str(e)}")
        print("Please check the logs for more detailed information.")
        sys.exit(1)

if __name__ == "__main__":
    main()