# Task 12 — Personalized Music Learning System

A CrewAI-powered, sequential multi-agent system that creates a personalized music learning plan based on a user's instrument and skill level. The system curates music theory resources, generates practice routines, and suggests performance projects using a custom tool.

## ✨ Features
- Three specialized agents running in sequence (Process.sequential)
- Custom tool: PerformanceProjectTool for project ideas
- Gemini LLM support via `GEMINI_API_KEY`
- Single Markdown report output: `music_learning_plan.md`

## 🧩 Architecture
- Agents
  - Theory Curator: selects curated music theory resources for the instrument/level
  - Practice Planner: generates daily practice routines with durations
  - Project Suggestor: proposes performance projects using the custom tool
- Tasks (executed sequentially)
  1) Generate theory resources
  2) Create practice routines
  3) Suggest performance projects and compile the final Markdown report
- Custom Tool
  - `PerformanceProjectTool` (in `src/task_12/tools/custom_tool.py`)
  - Input schema (Pydantic): `{ instrument: str, skill_level: str }`
  - Output: list of project objects (title, description, difficulty, timeline_weeks, deliverable, success_criteria)

## 📦 Repository layout (this task)
```
task_12/
  ├─ README.md
  └─ src/task_12/
     ├─ main.py                 # Entry point to run the crew
     ├─ crew.py                 # Crew, agents, tasks wiring (sequential)
     ├─ config/
     │  ├─ agents.yaml          # Agent configs (theory_curator, practice_planner, project_suggestor)
     │  └─ tasks.yaml           # Task prompts and expected outputs
     └─ tools/
        └─ custom_tool.py       # PerformanceProjectTool (Pydantic input/output)
```

## 🔧 Prerequisites
- Python 3.10–3.13
- Installed dependencies (CrewAI and friends)
- A valid Google Gemini API key in your environment

## 🔐 Environment
Set your Gemini key before running:
```bash
export GEMINI_API_KEY=your_actual_gemini_api_key_here
```
(Optional `.env` in project root is also supported.)

## ▶️ Run
From the task directory:
```bash
cd task_12/src/task_12
python main.py
```
This will:
- Run three tasks sequentially (curation → routine → projects)
- Produce a single Markdown report: `music_learning_plan.md`

## 🧠 Inputs
Inputs are set in `src/task_12/main.py`:
```python
inputs = {
  'instrument': 'piano',
  'skill_level': 'beginner',
  'current_year': '2025'
}
```
Change `instrument` and `skill_level` as needed (e.g., `guitar`, `advanced`).

## 📄 Output
- File: `task_12/src/task_12/music_learning_plan.md`
- Sections:
  - Music Theory Resources (curated list with titles, types, URLs)
  - Practice Routine (blocks with descriptions and minutes + total time)
  - Performance Projects (title, description, timeline, deliverable, success criteria)

## 🛠️ Custom Tool (PerformanceProjectTool)
- Location: `src/task_12/tools/custom_tool.py`
- Pydantic input `PerformanceProjectInput`:
  - `instrument: str`
  - `skill_level: str`
- Returns a list of structured `PerformanceProject` items used by the Project Suggestor agent.

## ⚙️ LLM Configuration
- Configured in `src/task_12/crew.py` using CrewAI's `LLM` with model `gemini/gemini-1.5-flash`.
- Planning is disabled to avoid non-Gemini fallback: the system runs sequentially without hierarchical planning.

## ❓ Troubleshooting
- Missing or invalid key: ensure `GEMINI_API_KEY` is exported or present in `.env`.
- Imports when running locally: run from `task_12/src/task_12` so local imports resolve.
- Output not found: verify the script completed; the report is written as `music_learning_plan.md` in the same directory you ran `main.py` from.

## 📜 License
For educational/demo purposes. Adapt as needed for your use case.
