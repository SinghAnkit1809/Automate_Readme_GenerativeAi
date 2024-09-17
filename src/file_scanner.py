import argparse
import os
import sys
from dotenv import load_dotenv
from src.generator import AIReadmeGenerator
from src.utils import setup_logging, load_config

def main():
    load_dotenv()  # Load environment variables from .env file
    setup_logging()

    parser = argparse.ArgumentParser(description="Generate README.md using AI")
    parser.add_argument("project_path", help="Path to the project directory", type=str)
    parser.add_argument("--config", default="config/default_config.yaml", help="Path to configuration file")
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        sys.exit(1)

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("Error: GROQ_API_KEY not found in environment variables")
        sys.exit(1)

    try:
        generator = AIReadmeGenerator(api_key=api_key)
        readme_content = generator.create_readme(args.project_path, config['sections'])

        readme_path = os.path.join(args.project_path, "README.md")
        with open(readme_path, "w") as f:
            f.write(readme_content)

        print(f"README.md created successfully at {readme_path}")
    except Exception as e:
        print(f"An error occurred while generating the README: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()