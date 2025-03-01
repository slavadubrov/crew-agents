# Job Application PDF Analyzer

A tool that uses AI agents to analyze your LinkedIn profile PDF, tailor a resume for specific job applications, and prepare you for interviews.

## Overview

This project leverages the CrewAI framework to create a team of specialized AI agents that work together to:

1. Analyze job postings to extract key requirements
2. Process your LinkedIn profile PDF and GitHub profile
3. Generate a tailored resume that highlights relevant skills and experience
4. Create interview preparation materials with potential questions and talking points

## Requirements

- Python 3.12+
- OpenAI API key
- SerperDev API key

## Installation

```bash
# Clone the repository
git clone [your-repo-url]
cd job-application-pdf

# Install required packages
pip install -r requirements.txt

# Set up environment variables
export OPENAI_API_KEY="your_openai_api_key"
export SERPER_API_KEY="your_serperdev_api_key"
```

## Usage

```bash
python job_application_crew.py --linkedin-pdf your_profile.pdf --job-url "https://example.com/job" --github-url "https://github.com/yourusername"
```

### Required Arguments

- `--linkedin-pdf`: Path to your LinkedIn profile PDF export
- `--job-url`: URL of the job posting
- `--github-url`: URL of your GitHub profile

### Optional Arguments

- `--output-dir`: Directory to save output files (default: "output")
- `--config-dir`: Directory containing configuration files (default: "config")
- `--model`: LLM model to use (default: "gpt-4o-mini")

## Output

The tool generates two files in the output directory:

- `tailored_resume.md`: A customized resume aligned with the job requirements
- `interview_materials.md`: Preparation materials for your interview

## Project Structure

- `job_application_crew.py`: Main script that orchestrates the AI agents
- `config/`: Configuration files for agents and tasks
  - `agents.yaml`: Defines the roles and goals of the AI agents
  - `tasks.yaml`: Defines the workflow tasks and their expected outputs
- `common/utils.py`: Utility functions for loading configurations and API keys
- `output/`: Directory where generated files are saved
- `files/`: Sample files and output examples

## How It Works

1. **Job Research Agent**: Analyzes the job posting to extract key requirements
2. **Personal Profiler Agent**: Examines your LinkedIn PDF and GitHub profile
3. **Resume Strategist Agent**: Creates a tailored resume highlighting relevant skills
4. **Interview Preparer Agent**: Generates interview preparation materials

All agents work collaboratively, sharing information to create the most effective application materials.

## License

Personal use only. Not for distribution.