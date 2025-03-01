#!/usr/bin/env python3
"""
Job Application Crew Script

This script uses crewAI to tailor a resume for a specific job posting.
It accepts a resume file path (MUST BE IN MARKDOWN FORMAT), job posting URL, 
GitHub profile URL, and personal writeup as inputs. The script generates and 
saves a tailored resume and interview preparation materials to the specified 
output directory.

Usage:
    python job_application_crew.py --resume <resume_path.md> --job-url <job_url>
    --github-url <github_url> --personal-writeup <writeup>
    [--output-dir <dir>] [--config-dir <dir>] [--model <model_name>]
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any

import typer
from crewai import Agent, Crew, Task
from crewai_tools import FileReadTool, MDXSearchTool, ScrapeWebsiteTool, SerperDevTool

from common.utils import get_openai_api_key, get_serper_api_key, load_configs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = typer.Typer(help="Tailor a resume for a specific job posting.")


def create_agents(
    agents_config: dict[str, Any], resume_path: str, llm_name: str
) -> tuple[Agent, Agent, Agent, Agent]:
    """
    Create and return the agents for the crew.

    Args:
        agents_config: Configuration for the agents
        resume_path: Path to the resume file (must be in Markdown format)
        llm_name: Name of the language model to use

    Returns:
        Tuple of agents (researcher, profiler, resume_strategist,
        interview_preparer)
    """
    # Initialize tools
    tools: dict[str, Any] = {
        "search": SerperDevTool(),
        "scrape": ScrapeWebsiteTool(),
        "read_resume": FileReadTool(file_path=resume_path),
        "semantic_search": MDXSearchTool(mdx=resume_path),
    }

    # Common tools for all agents
    common_tools: list[Any] = [tools["scrape"], tools["search"]]
    resume_tools: list[Any] = [tools["read_resume"], tools["semantic_search"]]

    # Create agents
    researcher = Agent(
        config=agents_config["researcher_agent"],
        tools=common_tools,
        llm=llm_name,
    )

    profiler = Agent(
        config=agents_config["profiler_agent"],
        tools=common_tools + resume_tools,
        llm=llm_name,
    )

    resume_strategist = Agent(
        config=agents_config["resume_strategist_agent"],
        tools=common_tools + resume_tools,
        llm=llm_name,
        verbose=True,
    )

    interview_preparer = Agent(
        config=agents_config["interview_preparer_agent"],
        tools=common_tools + resume_tools,
        llm=llm_name,
        verbose=True,
    )

    return researcher, profiler, resume_strategist, interview_preparer


def create_tasks(
    tasks_config: dict[str, Any],
    agents: tuple[Agent, Agent, Agent, Agent],
    output_dir: str,
) -> list[Task]:
    """
    Create and return the tasks for the crew.

    Args:
        tasks_config: Configuration for the tasks
        agents: Tuple of agents to assign to tasks
        output_dir: Directory to save output files

    Returns:
        List of tasks for the crew to execute
    """
    researcher, profiler, resume_strategist, interview_preparer = agents

    # Task for Researcher Agent: Extract Job Requirements
    research_task = Task(
        description=tasks_config["research_task"]["description"],
        expected_output=tasks_config["research_task"]["expected_output"],
        agent=researcher,
        async_execution=tasks_config["research_task"]["async"],
    )

    # Task for Profiler Agent: Compile Comprehensive Profile
    profile_task = Task(
        description=tasks_config["profile_task"]["description"],
        expected_output=tasks_config["profile_task"]["expected_output"],
        agent=profiler,
        async_execution=tasks_config["profile_task"]["async"],
    )

    # Task for Resume Strategist Agent: Align Resume with Job Requirements
    resume_strategy_task = Task(
        description=tasks_config["resume_strategy_task"]["description"],
        expected_output=(tasks_config["resume_strategy_task"]["expected_output"]),
        output_file=f"{output_dir}/tailored_resume.md",
        context=[research_task, profile_task],
        agent=resume_strategist,
    )

    # Task for Interview Preparer Agent: Develop Interview Materials
    interview_preparation_task = Task(
        description=tasks_config["interview_preparation_task"]["description"],
        expected_output=(tasks_config["interview_preparation_task"]["expected_output"]),
        output_file=f"{output_dir}/interview_materials.md",
        context=[research_task, profile_task, resume_strategy_task],
        agent=interview_preparer,
    )

    return [
        research_task,
        profile_task,
        resume_strategy_task,
        interview_preparation_task,
    ]


def setup_environment(output_dir: Path, model: str) -> Path:
    """
    Set up environment variables and directories.

    Args:
        output_dir: Directory to save output files
        model: Name of the language model to use

    Returns:
        Path object for the output directory
    """
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)

    # Set up environment variables
    os.environ["OPENAI_API_KEY"] = get_openai_api_key()
    os.environ["OPENAI_MODEL_NAME"] = model
    os.environ["SERPER_API_KEY"] = get_serper_api_key()

    return output_dir


def validate_markdown_file(file_path: str) -> bool:
    """
    Validate that the file exists and has a markdown extension.

    Args:
        file_path: Path to the file to validate

    Returns:
        True if valid, False otherwise
    """
    path = Path(file_path)
    return path.exists() and path.suffix.lower() in [".md", ".mdx", ".markdown"]


@app.command()
def tailor_resume(
    resume: str = typer.Option(
        ...,
        help="Path to the resume file (MUST BE IN MARKDOWN FORMAT: .md, .mdx, or .markdown)",
    ),
    job_url: str = typer.Option(..., help="URL of the job posting"),
    github_url: str = typer.Option(..., help="URL of the GitHub profile"),
    personal_writeup: str = typer.Option(
        ..., help="Personal writeup about the candidate"
    ),
    output_dir: str = typer.Option("output", help="Directory to save output files"),
    config_dir: str = typer.Option(
        "config", help="Directory containing configuration files"
    ),
    model: str = typer.Option("gpt-4o-mini", help="LLM model to use"),
) -> None:
    """
    Tailor a resume for a specific job posting.

    This command creates a crew of AI agents that analyze a job posting and
    your resume, then generate a tailored resume and interview preparation
    materials.

    IMPORTANT: The resume file MUST be in Markdown format (.md, .mdx, or .markdown)
    as the tools used require this specific format to properly analyze the content.

    The output files (tailored_resume.md and interview_materials.md) are saved
    to the specified output directory.
    """
    # Validate resume file is in markdown format
    if not validate_markdown_file(resume):
        logger.error(
            f"Resume file '{resume}' does not exist or is not in Markdown format. "
            f"Please provide a valid Markdown file (.md, .mdx, or .markdown)."
        )
        sys.exit(1)

    # Convert output_dir to Path object
    output_path = Path(output_dir)

    # Set up environment
    setup_environment(output_path, model)

    # Load configurations
    agents_config, tasks_config = load_configs(config_dir)

    # Create agents
    logger.info(f"Creating agents with resume (Markdown): {resume}")
    agents = create_agents(agents_config, resume, model)

    # Create tasks
    logger.info("Creating tasks")
    tasks = create_tasks(tasks_config, agents, output_dir)

    # Create and run the crew
    job_application_crew = Crew(agents=list(agents), tasks=tasks, verbose=True)

    # Set up inputs for the crew
    job_application_inputs = {
        "job_posting_url": job_url,
        "github_url": github_url,
        "personal_writeup": personal_writeup,
    }

    # Run the crew
    logger.info(f"Starting job application crew with Markdown resume: {resume}")
    result = job_application_crew.kickoff(inputs=job_application_inputs)

    # Log completion message
    logger.info("Job application crew completed successfully!")
    logger.info(f"Tailored resume saved to: {output_path}/tailored_resume.md")
    logger.info(f"Interview materials saved to: {output_path}/interview_materials.md")

    return result


if __name__ == "__main__":
    app()
