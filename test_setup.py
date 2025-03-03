#!/usr/bin/env python
"""
Test script to verify the setup of the Technical Blog Writer.
This script checks if the required packages are installed and
the environment is properly configured.
"""

import os
import sys

from dotenv import load_dotenv


def check_environment():
    """Check if the environment is properly set up."""
    # Load environment variables
    load_dotenv()

    # Check for required API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    serper_key = os.getenv("SERPER_API_KEY")

    if not openai_key or openai_key == "your_openai_api_key_here":
        print("⚠️  Warning: OPENAI_API_KEY is not set or is using the default value.")
        print("    Please update the .env file with your actual OpenAI API key.")
    else:
        print("✅ OpenAI API key is configured.")

    if not serper_key or serper_key == "your_serper_api_key_here":
        print("⚠️  Warning: SERPER_API_KEY is not set or is using the default value.")
        print("    This key is needed for the research agent to search the web.")
        print("    You can get a key at https://serper.dev")
    else:
        print("✅ Serper API key is configured.")


def check_imports():
    """Check if required packages are installed."""
    try:
        import crewai

        print(f"✅ CrewAI is installed (version: {crewai.__version__})")
    except ImportError:
        print("❌ CrewAI is not installed. Please run: pip install crewai")
        return False

    try:
        import langchain_openai

        print("✅ langchain-openai is installed")
    except ImportError:
        print(
            "❌ langchain-openai is not installed. Please run: pip install langchain-openai"
        )
        return False

    try:
        import crewai_tools

        print("✅ crewai-tools is installed")
    except ImportError:
        print("❌ crewai-tools is not installed. Please run: pip install crewai-tools")
        return False

    return True


def check_project_structure():
    """Check if the project structure is correct."""
    # Check for the crews directory
    crews_path = os.path.join("src", "write_a_technical_blog", "crews")
    if not os.path.exists(crews_path):
        print(f"❌ Crews directory not found at {crews_path}")
        return False

    print("✅ Project structure looks good")
    return True


if __name__ == "__main__":
    print("🔍 Testing Technical Blog Writer setup...")
    print("\n1. Checking environment variables:")
    check_environment()

    print("\n2. Checking required packages:")
    imports_ok = check_imports()

    print("\n3. Checking project structure:")
    structure_ok = check_project_structure()

    print("\n📋 Summary:")
    if imports_ok and structure_ok:
        print("✅ Basic setup looks good! You can now run the application.")
        print("   To customize the blog topic, edit the BlogState in main.py")
        print("   To run the application: python -m write_a_technical_blog")
    else:
        print(
            "❌ There are issues with the setup. Please fix them before running the application."
        )

    print(
        "\nNote: Make sure to update the .env file with your actual API keys before running."
    )
