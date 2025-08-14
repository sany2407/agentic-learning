from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from tools.custom_tool import LaTeXValidatorTool
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@CrewBase
class LaTeXCorrectionCrew():
    """LaTeX Document Correction System crew"""

    agents: List[BaseAgent] = []
    tasks: List[Task] = []

    def _setup_llm(self) -> LLM:
        """Configure LLM to use Gemini"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        print(f"✅ Using Gemini API key: {api_key[:10]}...{api_key[-4:]}")
        
        return LLM(
            model="gemini/gemini-1.5-flash",
            temperature=0.1,
            timeout=120,
            max_tokens=4000,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            seed=42
        )

    @agent
    def manager_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['manager_agent'], # type: ignore[index]
            verbose=True,
            allow_delegation=True,
            max_iter=3,
            llm=self._setup_llm()
        )

    @agent
    def document_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['document_analyzer'], # type: ignore[index]
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            tools=[LaTeXValidatorTool()],
            llm=self._setup_llm()
        )

    @agent
    def document_corrector(self) -> Agent:
        return Agent(
            config=self.agents_config['document_corrector'], # type: ignore[index]
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            llm=self._setup_llm()
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'], # type: ignore[index]
        )

    @task
    def correction_task(self) -> Task:
        return Task(
            config=self.tasks_config['correction_task'], # type: ignore[index]
            output_file='latex_correction_report.md'
        )

    def create_agents_and_tasks(self):
        """Manually create agents and tasks"""
        self.agents = [
            self.manager_agent(),
            self.document_analyzer(),
            self.document_corrector()
        ]
        self.tasks = [
            self.analysis_task(),
            self.correction_task()
        ]

    @crew
    def crew(self) -> Crew:
        """Creates the LaTeX Document Correction System crew"""
        # Ensure agents and tasks are created
        if not self.agents or not self.tasks:
            self.create_agents_and_tasks()
            
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            planning=False,  # Disable planning to avoid OpenAI dependency
            manager_agent=self.agents[0]  # First agent is the manager
        )
