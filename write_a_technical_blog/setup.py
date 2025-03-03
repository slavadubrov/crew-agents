from setuptools import find_packages, setup

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
            "blog-gen=write_a_technical_blog.run:main",
        ],
    },
)
