# Job Application AI Assistant

A tool that uses AI agents to tailor your resume for specific job applications and prepare you for interviews.

## Overview

This project leverages the CrewAI framework to create a team of specialized AI agents that work together to:

1. Analyze job postings to extract key requirements
2. Review your resume and GitHub profile
3. Generate a tailored resume that highlights relevant skills and experience
4. Create interview preparation materials with potential questions and talking points

## Requirements

- Python 3.12+
- OpenAI API key
- SerperDev API key

## Usage

```bash
python job_application_crew.py --resume your_resume.md --job-url "https://example.com/job" --github-url "https://github.com/yourusername" --personal-writeup "Brief description about yourself"
```

### Required Arguments

- `--resume`: Path to your resume file (must be in Markdown format)
- `--job-url`: URL of the job posting
- `--github-url`: URL of your GitHub profile
- `--personal-writeup`: Brief personal description

### Optional Arguments

- `--output-dir`: Directory to save output files (default: "output")
- `--config-dir`: Directory containing configuration files (default: "config")
- `--model`: LLM model to use (default: "gpt-4o-mini")

## Output

The tool generates two files in the output directory:

- `tailored_resume.md`: A customized resume aligned with the job requirements
- `interview_materials.md`: Preparation materials for your interview

## Project Structure

- `job_application_crew.py`: Main script
- `config/`: Configuration files for agents and tasks
- `files/`: Sample files and output examples
