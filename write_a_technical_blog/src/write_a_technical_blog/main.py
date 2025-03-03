#!/usr/bin/env python
import logging
import os
import re
import uuid

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel, Field

from write_a_technical_blog.crews.blog_planning_crew.blog_planning_crew import (
    BlogPlanningCrew,
)
from write_a_technical_blog.crews.blog_writing_crew.blog_writing_crew import (
    BlogWritingCrew,
)
from write_a_technical_blog.types import BlogPost, BlogPostOutline


# Configure logging
def setup_logging(log_file="output/blog_generation.log"):
    """Set up logging to file and console"""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create logger
    logger = logging.getLogger("blog_generator")
    logger.setLevel(logging.DEBUG)

    # File handler (with rotation)
    file_handler = logging.FileHandler(log_file)

    # # Console handler
    console_handler = logging.StreamHandler()

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Initialize logger
logger = setup_logging()


class BlogState(BaseModel):
    """State for the blog writing flow"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Python Design Patterns for Machine Learning"
    blog_posts: list[BlogPost] = []
    blog_roadmap: list[BlogPostOutline] = []
    topic: str = "Python Design Patterns for Machine Learning"
    goal: str = """
        Create a comprehensive series of technical blog posts about comprehensive
        overview with examples of the most common design patterns used in machine
        learning. Each post should explain a specific pattern with real-world 
        examples, code snippets, and diagrams. The content should be suitable for 
        intermediate Python ML Engineers looking to improve their skills.
    """


def parse_roadmap_file(roadmap_file_path):
    """Parse a roadmap markdown file to extract topic, goal, and blog post outlines."""
    with open(roadmap_file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Extract topic
    topic_match = re.search(r"## Topic: (.+?)(?:\n|$)", content)
    topic = topic_match.group(1).strip() if topic_match else ""

    # Extract goal
    goal_match = re.search(r"## Goal\n(.*?)\n\n## Planned Posts", content, re.DOTALL)
    goal = goal_match.group(1).strip() if goal_match else ""

    # Extract planned posts
    post_outlines = []
    post_sections = re.finditer(
        r"### \d+\. (.+?)\n\n(.*?)(?=\n\n### \d+\.|$)", content, re.DOTALL
    )

    for match in post_sections:
        title = match.group(1).strip()
        description = match.group(2).strip()
        post_outlines.append(BlogPostOutline(title=title, description=description))

    return topic, goal, post_outlines


class BlogFlow(Flow[BlogState]):
    """Flow for the blog writing process"""

    initial_state = BlogState
    skip_planning = False

    def __init__(self, skip_planning=False, roadmap_file=None):
        """Initialize the flow with options to skip planning phase."""
        super().__init__()
        self.skip_planning = skip_planning
        self.roadmap_file = roadmap_file

        # If skipping planning and using roadmap file, parse it
        if self.skip_planning and self.roadmap_file:
            topic, goal, post_outlines = parse_roadmap_file(self.roadmap_file)
            self.state.topic = topic
            self.state.goal = goal
            self.state.blog_roadmap = post_outlines
            logger.info(
                f"Loaded roadmap from {roadmap_file} with "
                f"{len(post_outlines)} posts"
            )

    @start()
    def generate_blog_roadmap(self):
        """Generate the roadmap for the blog series"""
        # Skip planning if using an existing roadmap
        if self.skip_planning:
            logger.info("Skipping planning phase, using provided roadmap")
            return self.state.blog_roadmap

        logger.info("Starting the Blog Planning Crew")
        output = (
            BlogPlanningCrew()
            .crew()
            .kickoff(inputs={"topic": self.state.topic, "goal": self.state.goal})
        )

        posts = output["posts"]
        logger.info(f"Blog Posts Roadmap: {posts}")

        self.state.blog_roadmap = posts

        # Create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)

        # Save the roadmap to the output directory
        roadmap_content = "# Blog Series Roadmap\n\n"
        roadmap_content += f"## Topic: {self.state.topic}\n\n"
        roadmap_content += f"## Goal\n{self.state.goal}\n\n"
        roadmap_content += "## Planned Posts\n\n"

        for i, post in enumerate(posts, 1):
            roadmap_content += f"### {i}. {post.title}\n\n"
            roadmap_content += f"{post.description}\n\n"

        with open("output/Blog_Series_Roadmap.md", "w", encoding="utf-8") as file:
            file.write(roadmap_content)

        logger.info("Roadmap saved to output/Blog_Series_Roadmap.md")

        return posts

    @listen(generate_blog_roadmap)
    async def write_blog_posts(self):
        """Write each blog post in the roadmap"""
        logger.info("Writing Blog Posts")

        async def write_single_post(post_outline, index):
            """Write a single blog post"""
            logger.info(f"Writing Blog Post {index+1}: {post_outline.title}")
            post_index_plus_one = index + 1  # Calculate this value separately
            output = (
                BlogWritingCrew()
                .crew()
                .kickoff(
                    inputs={
                        "goal": self.state.goal,
                        "topic": self.state.topic,
                        "post_title": post_outline.title,
                        "post_description": post_outline.description,
                        "blog_roadmap": [
                            outline.model_dump() for outline in self.state.blog_roadmap
                        ],
                        "post_index": index,
                        "post_index_plus_one": post_index_plus_one,
                        "total_posts": len(self.state.blog_roadmap),
                    }
                )
            )

            title = output["title"]
            content = output["content"]
            post = BlogPost(title=title, content=content)

            # Save the blog post to a file
            filename = f"output/Blog_Post_{index+1}_{title.replace(' ', '_')}.md"
            with open(filename, "w", encoding="utf-8") as file:
                file.write(content)

            logger.info(f"Blog post saved as {filename}")

            return post

        # Process one blog post at a time sequentially
        for i, post_outline in enumerate(self.state.blog_roadmap):
            post = await write_single_post(post_outline, i)
            self.state.blog_posts.append(post)

        logger.info(f"Completed writing {len(self.state.blog_posts)} blog posts")
        return self.state.blog_posts


def kickoff(skip_planning=False, roadmap_file=None):
    """Run the blog flow

    Args:
        skip_planning: If True, skip the planning phase and use roadmap_file instead
        roadmap_file: Path to the roadmap markdown file to use when skipping planning
    """
    logger.info("Starting Blog Generation Flow")

    if skip_planning and not roadmap_file:
        logger.error("roadmap_file must be provided when skip_planning is True")
        return

    if skip_planning:
        logger.info(f"Using roadmap file: {roadmap_file}")

    blog_flow = BlogFlow(skip_planning=skip_planning, roadmap_file=roadmap_file)
    blog_flow.kickoff()
    logger.info("Blog Generation Flow completed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate technical blog posts")
    parser.add_argument(
        "--skip-planning",
        action="store_true",
        help="Skip the planning phase and use an existing roadmap file",
    )
    parser.add_argument(
        "--roadmap-file",
        type=str,
        help="Path to the roadmap markdown file (required if --skip-planning is used)",
    )

    args = parser.parse_args()

    kickoff(skip_planning=args.skip_planning, roadmap_file=args.roadmap_file)
