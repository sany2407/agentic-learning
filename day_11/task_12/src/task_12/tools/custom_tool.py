from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field

class PerformanceProjectInput(BaseModel):
	instrument: str = Field(..., description="User's instrument, e.g., piano, guitar")
	skill_level: str = Field(..., description="User's skill level, e.g., beginner, intermediate, advanced")

class PerformanceProject(BaseModel):
	title: str
	description: str
	difficulty: str
	timeline_weeks: int
	deliverable: str
	success_criteria: List[str]

class PerformanceProjectTool(BaseTool):
	name: str = "Performance Project Tool"
	description: str = (
		"Generates performance project ideas tailored to instrument and skill level"
	)
	args_schema: Type[BaseModel] = PerformanceProjectInput

	def _run(self, instrument: str, skill_level: str) -> List[PerformanceProject]:
		projects: List[PerformanceProject] = []
		if skill_level.lower() in ["beginner", "novice"]:
			if instrument.lower() == "piano":
				projects.append(PerformanceProject(
					title="Two-Hand Coordination Mini-Recital",
					description="Prepare 3 short pieces focusing on steady tempo and dynamics.",
					difficulty="beginner",
					timeline_weeks=4,
					deliverable="Recorded video of the 3 pieces (3–6 minutes total)",
					success_criteria=["Accurate rhythm", "Consistent tempo", "Basic dynamic contrast"]
				))
			elif instrument.lower() == "guitar":
				projects.append(PerformanceProject(
					title="Open Chords Song Cover",
					description="Learn and record a simple song using open chords and strumming.",
					difficulty="beginner",
					timeline_weeks=3,
					deliverable="Audio or video cover (2–4 minutes)",
					success_criteria=["Clean chord changes", "Stable strumming pattern"]
				))
		else:
			# default/advanced example
			projects.append(PerformanceProject(
				title="Solo Performance Recording Project",
				description="Prepare a polished recording of a solo piece appropriate to your level.",
				difficulty=skill_level.lower(),
				timeline_weeks=6,
				deliverable="High-quality audio/video recording",
				success_criteria=["Musical phrasing", "Technical accuracy", "Expressive dynamics"]
			))
		return projects
