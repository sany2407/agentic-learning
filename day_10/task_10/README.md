
# 🎯 Event Attendee Engagement Analysis System

A sophisticated AI-powered system that analyzes event attendee data and develops comprehensive strategies to enhance engagement using CrewAI and Google Gemini.


## 🔍 Overview

The Event Attendee Engagement Analysis System is designed to help event organizers understand attendee behavior patterns and develop data-driven strategies to improve participation and engagement. The system uses two specialized AI agents working in collaboration:

- **Attendee Analyst Agent**: Analyzes engagement metrics and identifies patterns
- **Engagement Strategist Agent**: Develops actionable strategies based on analysis findings


## ✨ Features

### 🤖 AI-Powered Analysis

- **Dual Agent System**: Specialized agents for analysis and strategy development
- **Google Gemini Integration**: Advanced AI capabilities for deep insights
- **Sequential Processing**: Analysis findings directly inform strategy recommendations


### 📊 Comprehensive Metrics Analysis

- Participation rate analysis for events and sessions
- Attendee feedback sentiment analysis
- Engagement pattern identification (peak times, drop-off points)
- Session format effectiveness comparison
- Demographic analysis of engaged vs. disengaged attendees


### 📈 Strategic Recommendations

- Pre-event engagement tactics
- During-event participation techniques
- Post-event follow-up strategies
- Technology solution recommendations
- ROI-focused budget considerations


### 📄 Professional Reporting

- **Markdown Export**: Automatically generates formatted reports
- **Timestamped Files**: Organized file naming with timestamps
- **Comprehensive Documentation**: Complete analysis and strategy details
- **Actionable Insights**: Clear next steps and implementation guidance


## 🏗️ System Architecture

### Agents

#### 👨💼 Attendee Analyst Agent

- **Role**: Event Data Specialist
- **Goal**: Identify engagement gaps and analyze attendee behavior patterns
- **Expertise**: Quantitative analysis of participation rates, feedback metrics, and engagement patterns


#### 👩💼 Engagement Strategist Agent

- **Role**: Event Planning Consultant
- **Goal**: Develop comprehensive engagement strategies to boost participation
- **Expertise**: Translating data insights into actionable strategies across various event formats


### Tasks

#### 📊 Attendee Analysis Task

- **Input**: List of events/sessions with engagement data
- **Output**: Comprehensive analysis report with identified gaps and patterns
- **Focus**: Quantitative metrics and comparative analysis


#### 🎯 Engagement Strategy Task

- **Input**: Analysis findings + event data
- **Output**: Detailed strategy with implementation roadmap
- **Focus**: Actionable recommendations with measurable KPIs


## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key


### Step 1: Clone the Repository

Clone the repository to your local machine

### Step 2: Create Virtual Environment (Recommended)

Set up a Python virtual environment to isolate dependencies

### Step 3: Install Dependencies

Install all required packages using the provided requirements file

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root with your Google Gemini API key

## ⚙️ Configuration

### Getting Your Google Gemini API Key

1. Visit Google AI Studio at https://aistudio.google.com/
2. Sign in with your Google account
3. Click **"Get API Key"** → **"Create API Key"**
4. Choose an existing Google Cloud project or create a new one
5. Copy your API key and add it to your `.env` file

### Environment Variables

| Variable | Description | Required |
| :-- | :-- | :-- |
| `GEMINI_API_KEY` | Your Google Gemini API key | Yes |

## 🎯 Usage

### Basic Usage

Run the system with included sample data to see how it works

### Custom Event Data

1. Create a JSON file with your event data following the specified format
2. Load and analyze your custom data using the file input function

### Programmatic Usage

Import the main class and use it programmatically in your own applications

## 📊 Data Format

### Event Data Structure

The system expects JSON data with specific fields for events, sessions, and metrics:

- **Event Level**: ID, name, type, overall metrics
- **Session Level**: ID, name, type, duration, attendance data
- **Engagement Metrics**: Poll responses, chat messages, social shares
- **Feedback Data**: Scores, completion rates, participation numbers


### Required Fields

| Field | Type | Description |
| :-- | :-- | :-- |
| `event_id` | string | Unique event identifier |
| `event_name` | string | Display name of the event |
| `event_type` | string | Type of event (Conference, Webinar, etc.) |
| `sessions` | array | List of session objects |
| `overall_metrics` | object | Event-level metrics |

## 📄 Output

### Console Output

- Real-time processing updates
- Verification status messages
- Analysis results summary
- File generation confirmations


### Markdown Report

Automatically generated file includes:

- **Executive Summary**: Key findings overview
- **Detailed Analysis**: Complete AI analysis results
- **Event Data Summary**: Formatted event and session breakdowns
- **Strategic Recommendations**: Actionable improvement strategies
- **Implementation Roadmap**: Step-by-step guidance
- **Technical Details**: System and generation information


### File Naming Convention

Reports are saved with timestamps for easy organization and version tracking

## 💡 Examples

### Sample Events Included

The system comes with sample data for:

1. **Annual Tech Conference 2024** (Multi-session conference)
2. **Monthly Product Demo** (Single-session webinar)

### Expected Insights

- Participation rate comparisons
- Engagement drop-off analysis
- Session format effectiveness
- Audience interaction patterns
- Strategic improvement recommendations



## 📚 Dependencies

The system requires:

- **CrewAI**: Multi-agent AI framework
- **python-dotenv**: Environment variable management



