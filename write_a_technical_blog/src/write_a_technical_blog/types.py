from pydantic import BaseModel


class BlogPostOutline(BaseModel):
    """Model for a single blog post outline"""

    title: str
    description: str


class BlogRoadmap(BaseModel):
    """Model for the entire blog series roadmap"""

    posts: list[BlogPostOutline]


class BlogPost(BaseModel):
    """Model for a single blog post"""

    title: str
    content: str
