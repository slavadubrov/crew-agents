from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from langchain_openai import ChatOpenAI

from write_a_technical_blog.types import BlogPost

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()


@CrewBase
class BlogWritingCrew:
    """Blog Writing Crew - Creates a technical blog post"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = ChatOpenAI(model="gpt-4o-mini")  # Default model, can be changed later

    @agent
    def researcher(self) -> Agent:
        """Researcher agent - gathers information on the topic"""
        return Agent(
            config=self.agents_config["researcher"],
            tools=[search_tool, scrape_tool],
            llm=self.llm,
            allow_delegation=True,
            verbose=True,
        )

    @agent
    def content_writer(self) -> Agent:
        """Content Writer agent - creates the main blog content"""
        return Agent(
            config=self.agents_config["content_writer"],
            tools=[search_tool, scrape_tool],
            llm=self.llm,
            allow_delegation=True,
            verbose=True,
        )

    @agent
    def code_writer(self) -> Agent:
        """Code Writer agent - develops clear, well-documented code examples"""
        return Agent(
            config=self.agents_config["code_writer"],
            tools=[search_tool, scrape_tool],
            llm=self.llm,
            allow_delegation=True,
            verbose=True,
        )

    @agent
    def diagram_creator(self) -> Agent:
        """Diagram Creator agent - creates visual diagrams using Mermaid"""
        return Agent(
            config=self.agents_config["diagram_creator"],
            llm=self.llm,
            allow_delegation=True,
            verbose=True,
        )

    @agent
    def reviewer(self) -> Agent:
        """Reviewer agent - ensures the blog post is accurate and engaging"""
        return Agent(
            config=self.agents_config["reviewer"],
            llm=self.llm,
            allow_delegation=True,
            verbose=True,
        )

    @task
    def research_topic(self) -> Task:
        """Task for researching the blog post topic"""
        return Task(
            config=self.tasks_config["research_topic"],
        )

    @task
    def write_content(self) -> Task:
        """Task for writing the main blog content"""
        return Task(
            config=self.tasks_config["write_content"],
        )

    @task
    def create_code_examples(self) -> Task:
        """Task for creating code examples for the blog post"""
        return Task(
            config=self.tasks_config["create_code_examples"],
        )

    @task
    def create_diagrams(self) -> Task:
        """Task for creating diagrams for the blog post"""
        return Task(
            config=self.tasks_config["create_diagrams"],
        )

    @task
    def review_blog_post(self) -> Task:
        """Task for reviewing the blog post"""
        return Task(
            config=self.tasks_config["review_blog_post"],
            output_pydantic=BlogPost,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Blog Writing Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            manager_llm=ChatOpenAI(model="gpt-4o", temperature=0.3),
            process=Process.hierarchical,
            verbose=True,
        )
