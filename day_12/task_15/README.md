# 🍽️ Meal Nutrition Analyzer

A multi-agent system that analyzes the nutritional content of user-provided meals using AutoGen framework and LLMs. The system provides detailed nutritional breakdowns including calories, proteins, carbohydrates, and fats without relying on external APIs.

## 📋 Table of Contents

- [Problem Statement](#problem-statement)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Example](#example)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)

## 🎯 Problem Statement

Build a system to analyze the nutritional content of user-provided meals. The system should:
- Collect meal details through an interactive interface
- Calculate nutritional values using intelligent agents
- Use LLMs for meal interpretation and custom tools for calculations
- Avoid dependency on external APIs
- Provide accurate nutritional breakdowns with calorie and macronutrient details

## ✨ Features

- **Interactive Meal Analysis**: Continuous conversation interface for analyzing multiple meals
- **Multi-Agent Architecture**: Uses specialized agents for input processing, nutrition estimation, and validation
- **Custom Nutrition Tool**: Built-in nutrition database with common ingredients
- **LLM-Powered Intelligence**: Leverages Gemini 2.0 Flash for intelligent meal interpretation
- **Comprehensive Reports**: Detailed breakdown of calories, proteins, carbs, and fats
- **No External APIs**: Self-contained system with hardcoded nutrition database
- **User-Friendly Interface**: Clear prompts, visual separators, and easy exit options

## 🏗️ Architecture

The system implements AutoGen's Sequential Conversation Pattern with three specialized agents:

1. **Input Processor Agent**: Structures meal descriptions into analyzable format
2. **Nutrition Calculation Agent**: Estimates nutritional values using LLM knowledge
3. **Validation Agent**: Uses custom nutrition computation tool for accurate calculations

The agents work in a round-robin fashion, passing information between each other until a final validated report is generated.

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### Setup

1. **Clone the repository**:
```
git clone https://github.com/sany2407/agentic-learning.git
cd day_12
cd task_15
```

2. **Create virtual environment**:
```
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

```

3. **Install dependencies**:
```
pip install -r requirements.txt

```

4. **Create `.env` file**


5. **Add your API key to `.env`**:
```
GEMINI_API_KEY=your_gemini_api_key_here

```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following:


### Getting Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key and add it to your `.env` file

## 📖 Usage

### Running the Application

```
python main.py
```


### Interactive Commands

- **Analyze a meal**: Enter meal description (e.g., "grilled chicken 200g, rice 150g, broccoli 100g")
- **Exit the program**: Type `exit`, `quit`, or `q`
- **Continue analysis**: After each report, choose to analyze another meal or exit

### Meal Description Format

The system accepts natural language meal descriptions:

"grilled chicken 200g, rice 150g, broccoli 100g"
"2 eggs, 2 slices of bread, 1 glass of milk"
"beef steak 250g with mashed potato 200g and spinach 100g"


## 🔄 How It Works

1. **Input Collection**: System prompts user for meal description
2. **Input Processing**: Input Processor Agent structures the meal into ingredient list
3. **Nutrition Estimation**: Nutrition Agent provides preliminary nutritional estimates
4. **Validation**: Validation Agent uses the custom nutrition tool for accurate calculations
5. **Report Generation**: Final validated nutritional report is displayed
6. **Continuation**: User can choose to analyze another meal or exit

### Agent Flow

User Input → Input Processor → Nutrition Agent → Validation Agent → Final Report


## 📝 Example

### Input:
Enter your meal details: grilled chicken 200g, rice 150g, broccoli 100g


### Output:
📊 NUTRITIONAL ANALYSIS COMPLETE
Nutritional Breakdown:

Chicken (200g): 330.0 cal, 62.0g protein, 0.0g carbs, 7.2g fats

Rice (150g): 195.0 cal, 4.1g protein, 42.0g carbs, 0.5g fats

Broccoli (100g): 55.0 cal, 3.7g protein, 11.0g carbs, 0.6g fats

Totals: 580.0 calories, 69.8g protein, 53.0g carbs, 8.3g fats
