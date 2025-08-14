from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from tools.custom_tool import PerformanceProjectTool
import os
from dotenv import load_dotenv

load_dotenv()

@CrewBase
class Task12():
	"""Task12 crew - Personalized Music Learning System"""

	agents: List[BaseAgent]
	tasks: List[Task]

	def _setup_llm(self) -> LLM:
		api_key = os.getenv('GEMINI_API_KEY')
		if not api_key:
			raise ValueError("GEMINI_API_KEY environment variable is required")
		return LLM(
			model="gemini/gemini-1.5-flash",
			temperature=0.3,
			timeout=120,
			max_tokens=4000,
			top_p=0.9,
			frequency_penalty=0.1,
			presence_penalty=0.1,
			seed=42
		)

	@agent
	def theory_curator(self) -> Agent:
		return Agent(
			config=self.agents_config['theory_curator'], # type: ignore[index]
			verbose=True,
			llm=self._setup_llm()
		)

	@agent
	def practice_planner(self) -> Agent:
		return Agent(
			config=self.agents_config['practice_planner'], # type: ignore[index]
			verbose=True,
			llm=self._setup_llm()
		)

	@agent
	def project_suggestor(self) -> Agent:
		return Agent(
			config=self.agents_config['project_suggestor'], # type: ignore[index]
			verbose=True,
			tools=[PerformanceProjectTool()],
			llm=self._setup_llm()
		)

	@task
	def generate_theory_resources(self) -> Task:
		return Task(
			config=self.tasks_config['generate_theory_resources'], # type: ignore[index]
		)

	@task
	def create_practice_routines(self) -> Task:
		return Task(
			config=self.tasks_config['create_practice_routines'], # type: ignore[index]
		)

	@task
	def suggest_performance_projects(self) -> Task:
		# Base definition; final wiring is done in crew() with context and output file
		return Task(
			config=self.tasks_config['suggest_performance_projects'], # type: ignore[index]
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the Task12 crew"""
		# Wire tasks with context and only final Markdown output
		t1 = self.generate_theory_resources()
		t2 = self.create_practice_routines()
		t3 = Task(
			config=self.tasks_config['suggest_performance_projects'], # type: ignore[index]
			context=[t1, t2],
			output_file='music_learning_plan.md'
		)
		return Crew(
			agents=self.agents,
			tasks=[t1, t2, t3],
			process=Process.sequential,
			verbose=True,
			planning=False,
		)
