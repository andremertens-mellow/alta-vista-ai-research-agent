from setuptools import setup, find_packages

setup(
    name="alta-vista-ai",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "openai",
        "python-dotenv",
    ],
) 