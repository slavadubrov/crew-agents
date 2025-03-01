"""Helper functions for the project."""

import os
from typing import Any

import yaml
from dotenv import find_dotenv, load_dotenv


def load_env():
    _ = load_dotenv(find_dotenv())


def get_openai_api_key():
    load_env()
    return os.getenv("OPENAI_API_KEY")


def get_serper_api_key():
    load_env()
    return os.getenv("SERPER_API_KEY")


def pretty_print_result(result):
    """Pretty print a result string.

    Args:
        result (str): The result string to pretty print.

    Returns:
        str: The pretty printed result string.
    """
    parsed_result = []
    for line in result.split("\n"):
        if len(line) > 80:
            words = line.split(" ")
            new_line = ""
            for word in words:
                if len(new_line) + len(word) + 1 > 80:
                    parsed_result.append(new_line)
                    new_line = word
                else:
                    if new_line == "":
                        new_line = word
                    else:
                        new_line += " " + word
            parsed_result.append(new_line)
        else:
            parsed_result.append(line)
    return "\n".join(parsed_result)


def load_configs(config_dir: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Load agent and task configurations from YAML files.

    Args:
        config_dir: Directory containing configuration files

    Returns:
        Tuple containing agent and task configurations
    """
    files = {
        "agents": f"{config_dir}/agents.yaml",
        "tasks": f"{config_dir}/tasks.yaml",
    }
    configs: dict[str, Any] = {}

    for config_type, file_path in files.items():
        with open(file_path, "r") as file:
            configs[config_type] = yaml.safe_load(file)

    return configs["agents"], configs["tasks"]
