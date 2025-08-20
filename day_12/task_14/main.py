import asyncio
import os
from dotenv import load_dotenv
import logging  # Import for verbose logging

# Enable verbose logging (set to DEBUG for detailed output)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# AutoGen imports
from autogen_core.models import ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


async def main():
    # Initialize the model client (using Gemini via OpenAI-compatible client)
    model_client = OpenAIChatCompletionClient(
        model="gemini-2.0-flash",
        api_key=api_key,
        model_info=ModelInfo(
            vision=False,  # Not needed for text-based tasks
            function_calling=True,
            json_output=True,
            family="unknown",
            structured_output=True
        )
    )

    # Primary Agent: Analyzes code and drafts comments
    primary_agent = AssistantAgent(
        name="primary_agent",
        model_client=model_client,
        system_message=(
            "You are a code analyst. Analyze the given Python code and draft concise, meaningful comments. "
            "Focus on explaining purpose, logic, parameters, returns, and key steps. "
            "Output the code with integrated comments (e.g., using # for inline comments). "
            "After outputting, if revisions are needed, pass to the next agent. "
            "End the conversation by saying 'TERMINATE' when comments are final."
        )
    )

    # Feedback & Revision Agent: Reviews and refines comments
    feedback_agent = AssistantAgent(
        name="feedback_agent",
        model_client=model_client,
        system_message=(
            "You are a comment reviewer. Review the commented code for clarity, conciseness, and accuracy. "
            "Suggest refinements and output the revised code with improved comments. "
            "If already optimal, confirm and say 'TERMINATE' to end. Otherwise, pass back for further drafting."
        )
    )

    # Sample input Python code (replace with your own code string)
    input_code = """
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
"""

    # Termination condition: Stop when "TERMINATE" is mentioned
    termination = TextMentionTermination("TERMINATE")

    # Set up RoundRobinGroupChat for alternating between agents
    team = RoundRobinGroupChat(
        [primary_agent, feedback_agent],
        termination_condition=termination
    )

    # Run the chat starting with the input code as the task
    result = await team.run(task=f"Generate comments for this Python code:\n{input_code}")

    # Extract and display the final refined commented code (from the last message)
    if result.messages:
        final_commented_code = result.messages[-1].content
        print("Final Commented Code:\n")
        print(final_commented_code)
    else:
        print("No output generated.")


if __name__ == "__main__":
    asyncio.run(main())
