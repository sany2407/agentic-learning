# Structured Meeting Agenda Generator

This Python project uses the Google Gemini API to automatically generate well-structured meeting agendas based on a simple meeting objective. Designed for managers and teams, it outputs a clear, actionable agenda in a consistent markdown format, making meeting planning easier and more effective.

## Features

- **Automatic agenda generation** based on your meeting's objective.
- Produces a **bulleted, structured output** with Objective, Topics, and Action Items sections.
- Utilizes Google Gemini's large language model for high-quality content.
- **Configuration with .env** file for API key security.


## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/sany2407/agentic-learning.git
cd day_1
cd task_1
```


### 2. Create a Python Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```


### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Make sure the following packages are included in `requirements.txt`:

```
google-generativeai
python-dotenv
```


### 4. Set Up Google Gemini API Key

- Create a `.env` file in the project root directory.
- Add your Google API key to the file as follows:

```
GOOGLE_API_KEY=your-google-api-key-here
```

> **Note:** You need access to Google's Gemini API and a valid key. See [Google Gemini Documentation](https://ai.google.dev/gemini-api/docs) for instructions on obtaining an API key.

### 5. Run the Script

Edit the script (e.g. `main.py`) to change your meeting objective as needed:

```python
meeting_objective = "Plan the upcoming team building event"
```

Then execute:

```bash
python main.py
```

You will see a structured meeting agenda printed in your terminal.

## Example Usage

**Input Objective:**

```
Plan the upcoming team building event
```

**Output Agenda:**

```
- Objective: Plan the upcoming team building event
- Topics:
    - Set event date and location
    - Decide on activities and agenda
    - Delegate responsibilities
- Action Items:
    - Assign coordinator roles
    - Book venue
    - Send invitations to team
```


## Customizing Your Meeting Agenda

- Change the `meeting_objective` string in the script to your own meeting goal.
- The agenda structure and style are controlled by the instructions in the system prompt and can be modified to fit your needs.

## Promting Techniques Used

- One Shot Prompting
- Few Shot Prompting
- Negative Prompting

## Troubleshooting

- Ensure your `.env` file contains the correct API key.
- If you experience package issues, verify `google-generativeai` and `python-dotenv` are installed.
- For API errors, check your account limits and API access.


## License

This project is provided for educational and demonstration purposes. Please comply with the Google Generative AI API Terms of Service when using this code.

## Chat Link

The chat link for the project is below 
[ChatGpt Chat Link](https://chatgpt.com/share/688c825b-6cd8-8009-9582-f5432fbf7b1c)

# The pdf is in the output folder

**Happy productive meetings!**