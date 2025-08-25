# Working Marketing Campaign Tracker

A simple AI-powered tool for analyzing marketing campaigns using AutoGen agents and the Google Gemini model. This application extracts key metrics from campaign descriptions, calculates performance KPIs (like CTR, ROI, and conversion rates), provides insights, and offers optimization recommendations. It supports both structured analysis and streaming console output.

## Features

- **Metric Extraction**: Uses regex to parse campaign data for metrics such as sent, opened, clicked, views, conversions, shares, and spend.
- **KPI Calculation**: Computes key performance indicators including CTR, Open Rate, Conversion Rate, ROI (assuming $25 per conversion), and Cost per Conversion.
- **Channel Identification**: Automatically categorizes campaigns into channels like Email, Social Media, Content Marketing, or Other.
- **AI-Powered Insights**: Leverages an AutoGen AssistantAgent to analyze campaigns, provide performance insights, and suggest optimizations.
- **Structured and Streaming Modes**: Run analyses in a simple structured format or stream results to the console.
- **Custom Campaigns**: Analyze sample data or input your own campaign descriptions.

## Requirements

- Python 3.8+
- Google Gemini API Key (for the AI model)

## Installation

1. Create and activate a virtual environment (recommended):

```
python -m venv venv
source venv/bin/activate # On Unix/macOS
venv\Scripts\activate # On Windows
```

2. Install the required packages:
```
pip install -U "autogen-agentchat" "autogen-ext[openai]"
```


## Configuration

- Replace the `API_KEY` in the `main()` function with your actual Google Gemini API key:

```
API_KEY = "your_gemini_api_key_here"
```


Note: The code uses `OpenAIChatCompletionClient` but is configured for Gemini models. Ensure your API key is for Google AI Studio.

## Usage

Run the script:
```
python main.py
```

You will be prompted with a menu:
- **1. Run sample campaign analysis**: Analyzes predefined sample campaigns and displays structured results followed by streaming analysis.
- **2. Enter custom campaigns**: Input your own campaign descriptions (type 'done' to finish) and get analyzed results.
- **3. Exit**: Quit the application.

### Sample Output

When running option 1, the script will:
- Print sample campaigns.
- Perform a simple analysis and format the results (including breakdowns, top performers, and recommendations).
- Stream a detailed analysis to the console.

## Valid Campaign Formats

Campaign descriptions should include metrics in a natural language format. Examples:
- "Email newsletter: 5000 sent, 1200 opened, 89 clicked, 12 conversions"
- "Google Ads: 10000 views, 234 clicked, $500 spent, 15 conversions"
- "Instagram story: 2500 views, 125 clicked, $75 spent, 8 conversions"
- "Blog article: 800 views, 45 shares, 23 clicked, 2 conversions"
- "Facebook video ad: 3000 views, 180 clicked, $200 spent, 18 conversions"

The tool uses regex to extract numbers, so ensure metrics are phrased similarly (e.g., "X sent", "$Y spent").

## How It Works

1. **Tool Setup**: An async tool (`analyze_campaign`) extracts metrics and calculates KPIs for a single campaign.
2. **Agent Configuration**: An `AssistantAgent` is created with the tool and a system message to guide analysis.
3. **Analysis Modes**:
   - **Simple Analysis**: Runs the agent on the task, extracts JSON results, and formats them.
   - **Streaming Analysis**: Uses `Console` to stream the agent's thought process and outputs.
4. **Extraction and Formatting**: Parses agent responses to structure metrics, KPIs, top performers, and recommendations.

