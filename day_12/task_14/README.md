# Automated Code Comment Generator

This project implements a multi-agent system using AutoGen to automatically generate and refine meaningful comments for Python code. It leverages AI-powered agents to analyze code, draft initial comments, and iteratively refine them for clarity, conciseness, and accuracy.

## Problem Statement

Develop a system to generate meaningful comments for Python code. The Primary Agent analyzes the code and drafts comments, while the Feedback & Revision Agent refines them for clarity. The system ensures comments are concise and contextually accurate.

## Approach

- **Agents Implementation**: Two AutoGen agents are used:
  - **Primary Agent**: Analyzes the Python code and drafts concise, meaningful comments focusing on purpose, logic, parameters, returns, and key steps.
  - **Feedback & Revision Agent**: Reviews the drafted comments, suggests refinements for better clarity and accuracy, and outputs the revised code.
- **AI Integration**: Powered by AI LLMs (e.g., Gemini via OpenAI-compatible client) for comment generation and revision.
- **Workflow**: Utilizes AutoGen's `RoundRobinGroupChat` for iterative improvement through reflection loops, alternating between agents until termination (triggered by "TERMINATE" in responses).
- **Output**: The final output is the original code with integrated, refined comments displayed in the console.

## Expected Deliverables

- Python code with integrated, clear, and concise comments.
- Console output displaying the refined commented code.

## Requirements

To run this project, ensure you have Python 3.8+ installed. The following packages are required:

- `autogen-agentchat`
- `autogen-core`
- `autogen-ext[openai]` (for OpenAI-compatible model clients)
- `python-dotenv` (for loading environment variables)

**Note**: `asyncio` is part of the Python standard library, so no separate installation is needed.

Install the dependencies using pip:

```
pip install autogen-agentchat autogen-core autogen-ext[openai] python-dotenv

```


## Setup

1. **API Key Configuration**:
   - Create a `.env` file in the project root.
   - Add your Gemini API key (or compatible LLM key):
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

2. **Input Code**:
   - The code includes a sample Python function (Fibonacci calculator). Replace the `input_code` string in `main.py` with your own Python code snippet for commenting.

## Usage

1. Save the provided code as `main.py`.
2. Run the script:


3. **Verbose Mode (Optional)**:
- The code includes logging set to DEBUG level for verbose output, which tracks agent interactions and chat progression. Adjust the logging level in the code if needed (e.g., to INFO for less detail).

## Example Output

When run with the sample input, the console will display detailed logs (if verbose is enabled) followed by the final commented code, such as:

## Customization

- **Change Agents' Behavior**: Modify the `system_message` in each agent's initialization for different commenting styles.
- **Adjust Iterations**: The round-robin chat continues until "TERMINATE" is mentioned. Tweak system messages to control refinement depth.
- **Model Selection**: Update the `model` in `OpenAIChatCompletionClient` to use a different LLM if needed


