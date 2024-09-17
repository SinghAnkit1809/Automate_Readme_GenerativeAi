from setuptools import setup, find_packages

setup(
    name="ai-readme-generator",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        'langchain',
        'groq',
        'pyyaml',
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'generate-readme=scripts.run_generator:main',
        ],
    },
)