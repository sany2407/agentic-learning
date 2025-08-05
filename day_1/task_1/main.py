from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Retrieve the API key securely
api_key = os.getenv("GOOGLE_API_KEY")

# Configure Gemini client
client = genai.Client(api_key=api_key)

# Structured agenda system prompt
system_prompt = (
    "You are an assistant designed to help managers create structured meeting agendas for productive discussions.\n"
    "Instructions:\n"
    "- Generate a meeting agenda in a bulleted list format, using Structured Output.\n"
    "- Your agenda should contain the following clearly labeled sections:\n"
    "    - Objective: State the main goal or purpose of the meeting.\n"
    "    - Topics: List key topics or discussion points, each as a separate bullet.\n"
    "    - Action Items: End with expected decisions or assignments, each as a separate bullet.\n"
    "Requirements:\n"
    "- Input: Take the meeting objective as provided.\n"
    "- Output: Return only the structured agenda as a bulleted list with the required sections (Objective, Topics, Action Items).\n"
    "- Do not include extra commentary, just the requested structured output."
    
)

# Example input to test the prompt
meeting_objective = "Plan the upcoming team building event"

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=system_prompt
    ),
    contents=meeting_objective
)

# Output the generated agenda
print(response.text)
