#!/usr/bin/env python3
"""
LinkedIn Profile to Job Application Converter

This script uses crewAI to tailor a resume for a specific job posting.
It takes a LinkedIn profile PDF as the primary input and generates
a tailored resume and interview preparation materials.
"""

import logging
import os
from pathlib import Path

import typer
from crewai import Agent, Crew, Task
from crewai_tools import PDFSearchTool, ScrapeWebsiteTool, SerperDevTool

from common.utils import get_openai_api_key, get_serper_api_key, load_configs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Typer app
app = typer.Typer(help="Convert LinkedIn PDF to tailored job application")


def create_agents(config, linkedin_pdf_path, model_name):
    """Create and return agents with specialized roles."""
    # Set up tools
    tools = {
        "search": SerperDevTool(),
        "scrape": ScrapeWebsiteTool(),
        "pdf_search": PDFSearchTool(pdf=linkedin_pdf_path),
    }

    # Define tool sets
    common_tools = [tools["scrape"], tools["search"]]
    profile_tools = [tools["pdf_search"]]
    all_tools = common_tools + profile_tools

    # Create specialized agents
    researcher = Agent(
        config=config["researcher_agent"],
        tools=common_tools,
        llm=model_name,
    )

    profiler = Agent(
        config=config["profiler_agent"],
        tools=all_tools,
        llm=model_name,
    )

    resume_strategist = Agent(
        config=config["resume_strategist_agent"],
        tools=all_tools,
        llm=model_name,
        verbose=True,
    )

    interview_preparer = Agent(
        config=config["interview_preparer_agent"],
        tools=all_tools,
        llm=model_name,
        verbose=True,
    )

    return researcher, profiler, resume_strategist, interview_preparer


def create_tasks(config, agents, output_dir):
    """Create workflow tasks for the job application process."""
    researcher, profiler, resume_strategist, interview_preparer = agents

    # Research job requirements
    research_task = Task(
        description=config["research_task"]["description"],
        expected_output=config["research_task"]["expected_output"],
        agent=researcher,
        async_execution=config["research_task"]["async"],
    )

    # Analyze LinkedIn profile
    profile_task = Task(
        description=config["profile_task"]["description"],
        expected_output=config["profile_task"]["expected_output"],
        agent=profiler,
        async_execution=config["profile_task"]["async"],
    )

    # Create tailored resume
    resume_task = Task(
        description=config["resume_strategy_task"]["description"],
        expected_output=config["resume_strategy_task"]["expected_output"],
        output_file=f"{output_dir}/tailored_resume.md",
        context=[research_task, profile_task],
        agent=resume_strategist,
    )

    # Prepare interview materials
    interview_task = Task(
        description=config["interview_preparation_task"]["description"],
        expected_output=config["interview_preparation_task"]["expected_output"],
        output_file=f"{output_dir}/interview_materials.md",
        context=[research_task, profile_task, resume_task],
        agent=interview_preparer,
    )

    return [research_task, profile_task, resume_task, interview_task]


def setup_environment(output_dir, model):
    """Set up environment variables and create output directory."""
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)

    # Set environment variables
    os.environ["OPENAI_API_KEY"] = get_openai_api_key()
    os.environ["OPENAI_MODEL_NAME"] = model
    os.environ["SERPER_API_KEY"] = get_serper_api_key()

    return output_dir


@app.command()
def tailor_resume(
    linkedin_pdf: str = typer.Option(
        ..., help="Path to your LinkedIn profile PDF export"
    ),
    job_url: str = typer.Option(..., help="URL of the job posting"),
    github_url: str = typer.Option(..., help="URL of your GitHub profile"),
    output_dir: str = typer.Option("output", help="Directory to save output files"),
    config_dir: str = typer.Option(
        "config", help="Directory containing configuration files"
    ),
    model: str = typer.Option("gpt-4o-mini", help="LLM model to use"),
):
    """
    Convert your LinkedIn PDF profile into a tailored job application.

    This tool analyzes your LinkedIn profile PDF and a job posting to create:
    1. A tailored resume matching the job requirements
    2. Interview preparation materials with talking points
    """
    # Convert string path to Path object
    output_path = Path(output_dir)

    # Set up environment
    setup_environment(output_path, model)

    # Load configurations
    agents_config, tasks_config = load_configs(config_dir)

    # Log the start of processing
    logger.info(f"Processing LinkedIn PDF: {linkedin_pdf}")

    # Create agents with access to the LinkedIn PDF
    agents = create_agents(agents_config, linkedin_pdf, model)

    # Create workflow tasks
    tasks = create_tasks(tasks_config, agents, output_dir)

    # Create and configure the crew
    job_application_crew = Crew(agents=list(agents), tasks=tasks, verbose=True)

    # Set up inputs for the crew
    inputs = {
        "job_posting_url": job_url,
        "github_url": github_url,
    }

    # Run the crew
    logger.info("Starting job application process...")
    job_application_crew.kickoff(inputs=inputs)

    # Log completion and output locations
    logger.info("Job application process completed successfully!")
    logger.info(f"Tailored resume: {output_path}/tailored_resume.md")
    logger.info(f"Interview materials: {output_path}/interview_materials.md")


if __name__ == "__main__":
    app()
