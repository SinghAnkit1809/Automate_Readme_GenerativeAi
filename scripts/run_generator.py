import argparse
import os
import sys
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.generator import AIReadmeGenerator
from src.utils import setup_logging, load_config
def main():
    load_dotenv()  # Load environment variables from .env file
    setup_logging()
    parser = argparse.ArgumentParser(description="Generate README.md using AI")
    parser.add_argument("project_path", help="Path to the project directory", type=str)
    parser.add_argument("--config", default="config/default_config.yaml", help="Path to configuration file")
    args = parser.parse_args()
    config = load_config(args.config)
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    generator = AIReadmeGenerator(api_key=api_key)
    readme_content = generator.create_readme(args.project_path, config['sections'])
    readme_path = os.path.join(args.project_path, "README.md")
    with open(readme_path, "w") as f:
        f.write(readme_content)
    print(f"README.md created successfully at {readme_path}")

if __name__ == "__main__":
    main()