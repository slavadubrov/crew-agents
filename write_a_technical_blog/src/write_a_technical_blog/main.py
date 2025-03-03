#!/usr/bin/env python
import os
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


class BlogState(BaseModel):
    """State for the blog writing flow"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Python Design Patterns for Machine Learning"
    blog_posts: list[BlogPost] = []
    blog_roadmap: list[BlogPostOutline] = []
    topic: str = "Python Design Patterns for Machine Learning"
    goal: str = """
        Create a comprehensive series of technical blog posts about comprehensive overview with examples of the most common design patterns used in machine learning.
        Each post should explain a specific pattern with real-world examples, code snippets, and diagrams.
        The content should be suitable for intermediate Python ML Engineers looking to improve their skills.
    """


class BlogFlow(Flow[BlogState]):
    """Flow for the blog writing process"""

    initial_state = BlogState

    @start()
    def generate_blog_roadmap(self):
        """Generate the roadmap for the blog series"""
        print("Starting the Blog Planning Crew")
        output = (
            BlogPlanningCrew()
            .crew()
            .kickoff(inputs={"topic": self.state.topic, "goal": self.state.goal})
        )

        posts = output["posts"]
        print("Blog Posts Roadmap:", posts)

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

        return posts

    @listen(generate_blog_roadmap)
    async def write_blog_posts(self):
        """Write each blog post in the roadmap"""
        print("Writing Blog Posts")

        async def write_single_post(post_outline, index):
            """Write a single blog post"""
            print(f"Writing Blog Post {index+1}: {post_outline.title}")
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
                        "post_index_plus_one": post_index_plus_one,  # Add the new value
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

            print(f"Blog post saved as {filename}")

            return post

        # Process one blog post at a time sequentially
        for i, post_outline in enumerate(self.state.blog_roadmap):
            post = await write_single_post(post_outline, i)
            self.state.blog_posts.append(post)

        print(f"Completed writing {len(self.state.blog_posts)} blog posts")
        return self.state.blog_posts


def kickoff():
    """Run the blog flow"""
    blog_flow = BlogFlow()
    blog_flow.kickoff()


if __name__ == "__main__":
    kickoff()
