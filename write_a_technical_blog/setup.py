from setuptools import setup, find_packages

setup(
    name="write_a_technical_blog",
    version="0.1.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "crewai",
        "langchain-openai",
        "crewai-tools",
    ],
    entry_points={
        "console_scripts": [
            "kickoff=write_a_technical_blog.main:kickoff",
        ],
    },
) 