# 🗣️ Automated Debate Moderator (Multi-Agent System)

This project implements an **Automated Debate Moderator** using **AutoGen’s multi-agent framework**.  
The system is designed to **moderate debates** by generating topics, evaluating arguments, scoring responses, and ensuring fairness throughout discussions.  

---

## 📌 Problem Statement
Build a system to **moderate debates** by:  
- Generating debate topics  
- Evaluating participant arguments  
- Scoring responses based on quality  
- Ensuring fairness and coherence in discussions  
- Providing feedback to participants  

The system uses **multiple AI agents**, powered by LLMs, to collaboratively analyze and score debates in a structured group conversation.  

---

## 🏗️ System Architecture

### 🔹 Agents and Their Roles
1. **Topic Generator**  
   - Proposes engaging and balanced debate topics.  
   - Ensures topics are non-biased and thought-provoking.  

2. **Argument Evaluator**  
   - Analyzes participants’ arguments.  
   - Assesses clarity, logic, and persuasiveness.  

3. **Score Keeper**  
   - Assigns numerical scores to each argument.  
   - Maintains a record of participant performance.  

4. **Fairness Monitor**  
   - Detects bias in scoring or evaluation.  
   - Ensures equal opportunity for both participants.  

5. **Feedback Provider**  
   - Generates constructive feedback for each participant.  
   - Suggests improvements for clarity, reasoning, and delivery.  

6. **Coordinator**  
   - Oversees the entire debate flow.  
   - Assigns responsibilities to other agents and maintains structure.  

---

## 🔄 Workflow

1. **Topic Generation**  
   - The **Topic Generator** proposes a debate topic.  
   - The **Coordinator** finalizes and announces it.  

2. **Argument Collection**  
   - Participants provide their arguments.  
   - The **Coordinator** routes them to evaluators.  

3. **Evaluation & Scoring**  
   - The **Argument Evaluator** reviews the arguments.  
   - The **Score Keeper** assigns scores.  
   - The **Fairness Monitor** checks for consistency.  

4. **Feedback Delivery**  
   - The **Feedback Provider** gives improvement suggestions.  

5. **Final Output**  
   - Scores, feedback, and a fairness summary are presented.  

---

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sany2407/agentic-learning.git
   cd day_12
   cd task_13
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Mac/Linux
   .venv\Scripts\activate      # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Usage

Run the system:
```bash
python main.py
```

You will be prompted to start a debate session.  
The system will:  
- Generate a topic  
- Accept participant arguments  
- Evaluate and score responses  
- Provide fairness checks and feedback  

---

## 📊 Example Flow

**Generated Topic:**  
*"Should AI be granted legal personhood?"*  

**Participant A Argument:**  
"AI systems are tools created by humans and should not have rights."  

**Participant B Argument:**  
"Advanced AI systems with autonomy deserve recognition to ensure accountability."  

**Evaluation (by Argument Evaluator):**  
- A: Logical and ethical standpoint, but lacks depth.  
- B: Strong point on accountability, but needs evidence.  

**Scores (by Score Keeper):**  
- A: 7/10  
- B: 8/10  

**Fairness Monitor Check:**  
- Both participants received equal opportunity.  
- Scoring aligned with evaluation.  

**Feedback:**  
- A: Strengthen argument with examples of AI misuse.  
- B: Provide evidence or case studies on AI accountability.  

---

## ✅ Deliverables
- Moderated debate with structured arguments.  
- Scored responses with fairness validation.  
- Constructive feedback for improvement.  

---

## 📌 References
- [AutoGen Documentation](https://microsoft.github.io/autogen/)  
- *Agentic AI Problem Statement (Day 12) – Task 13: Automated Debate Moderator*  
