from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI

from write_a_technical_blog.types import BlogRoadmap


@CrewBase
class BlogPlanningCrew:
    """Blog Planning Crew - Creates a roadmap for a technical blog series"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = ChatOpenAI(model="gpt-4o-mini")  # Default model, can be changed later

    @agent
    def strategist(self) -> Agent:
        """Strategist agent - develops high-level strategy for the blog series"""
        search_tool = SerperDevTool()
        return Agent(
            config=self.agents_config["strategist"],
            tools=[search_tool],
            llm=self.llm,
            allow_delegation=True,
            verbose=True,
        )

    @agent
    def planner(self) -> Agent:
        """Planner agent - creates detailed outlines for each blog post"""
        return Agent(
            config=self.agents_config["planner"],
            llm=self.llm,
            allow_delegation=True,
            verbose=True,
        )

    @agent
    def reviewer(self) -> Agent:
        """Reviewer agent - ensures the plan is coherent and valuable"""
        return Agent(
            config=self.agents_config["reviewer"],
            llm=self.llm,
            allow_delegation=True,
            verbose=True,
        )

    @task
    def develop_strategy(self) -> Task:
        """Task for developing the high-level strategy for the blog series"""
        return Task(
            config=self.tasks_config["develop_strategy"],
        )

    @task
    def create_blog_outlines(self) -> Task:
        """Task for creating detailed outlines for each blog post"""
        return Task(
            config=self.tasks_config["create_blog_outlines"],
        )

    @task
    def review_roadmap(self) -> Task:
        """Task for reviewing the blog roadmap"""
        return Task(
            config=self.tasks_config["review_roadmap"],
            output_pydantic=BlogRoadmap,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Blog Planning Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            manager_llm=ChatOpenAI(model="gpt-4o", temperature=0.3),
            process=Process.hierarchical,
            verbose=True,
        )
