# Technical Blog Writer with CrewAI

This project uses CrewAI to generate technical blog posts with a team of specialized AI agents. The system is designed to create high-quality, informative, and engaging technical content with proper code examples and diagrams.

## Features

- **Blog Planning Crew**: Creates a comprehensive roadmap for a technical blog series
  - Strategist: Develops high-level strategy and identifies target audience
  - Planner: Creates detailed outlines for each blog post
  - Reviewer: Ensures the plan is coherent and valuable

- **Blog Writing Crew**: Writes individual blog posts based on the roadmap
  - Researcher: Gathers accurate, up-to-date information on the topic
  - Content Writer: Creates the main blog post content
  - Code Writer: Develops clear, well-documented code examples
  - Diagram Creator: Creates visual diagrams using Mermaid syntax
  - Reviewer: Ensures the blog post is accurate, clear, and engaging

- **Output**: All content is saved as Markdown files in the `output` directory

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install the package:
   ```bash
   pip install -e .
   ```

## Configuration

Create a `.env` file in the root directory with your API keys:

```
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key  # For web search capabilities
```

## Usage

You can customize the blog topic and goal in the `BlogState` class in `src/write_a_technical_blog/main.py`.

To run the flow:

```bash
python -m write_a_technical_blog.main
```

This will:
1. Generate a blog series roadmap
2. Create individual blog posts based on the roadmap
3. Save all content as Markdown files in the `output` directory

## Customization

- **LLM Model**: By default, the system uses `gpt-4o-mini`. You can change this in the crew files.
- **Blog Topic**: Modify the `topic` and `goal` in the `BlogState` class.
- **Agent Configurations**: Customize agent roles, goals, and backstories in the YAML config files.

## Output

The system generates:
- A roadmap file (`Blog_Series_Roadmap.md`) with the overall plan
- Individual blog post files with content, code examples, and diagrams

## License

MIT
