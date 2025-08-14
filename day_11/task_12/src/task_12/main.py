#!/usr/bin/env python
import warnings
from datetime import datetime
from crew import Task12

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def main():
	"""
	Run the Personalized Music Learning System (Task 12).
	"""
	inputs = {
		'instrument': 'piano',
		'skill_level': 'beginner',
		'current_year': str(datetime.now().year)
	}
	try:
		print("🚀 Task 12 - Personalized Music Learning System")
		print("=" * 60)
		result = Task12().crew().kickoff(inputs=inputs)
		print("\n✅ Completed!\n")
		print(result)
	except Exception as e:
		raise Exception(f"An error occurred while running Task 12: {e}")

if __name__ == "__main__":
	main()
