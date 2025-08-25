# Automated Debate Coach

An AI-powered debate preparation system that helps users build stronger arguments, prepare rebuttals, and evaluate argument strength using a multi-agent approach with AutoGen.

## Features

- **Multi-Agent Architecture**: Specialized AI agents for research, argument generation, rebuttals, and evaluation
- **Local Fact Database**: SQLite database with curated facts across multiple topics
- **Intelligent Input Parsing**: Flexible input formats for topics and user arguments
- **Argument Strength Scoring**: AI-powered evaluation system (1-10 scale)
- **Comprehensive Debate Preparation**: Complete package including supporting arguments and counter-rebuttals

## System Architecture

### Agent Roles

| Agent | Responsibility | Tools |
|-------|---------------|-------|
| **ResearchAgent** | Queries local fact database for relevant evidence | `query_facts` tool |
| **ArgumentAgent** | Generates compelling supporting arguments | LLM reasoning |
| **RebuttalAgent** | Prepares counter-arguments to potential opposition | LLM reasoning |
| **EvaluatorAgent** | Scores argument strength based on multiple criteria | LLM evaluation |

### Evaluation Criteria
- **Evidence Quality & Relevance** (30%)
- **Logical Reasoning & Structure** (25%)
- **Persuasiveness & Clarity** (25%)
- **Rebuttal Preparedness** (20%)

## 🚀 Installation

### Prerequisites
- Python 3.8+
- OpenAI API key or Gemini API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd automated-debate-coach
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Install required packages**
   ```bash
   pip install autogen-agentchat autogen-ext python-dotenv sqlite3
   ```

### Dependencies

```txt
autogen-agentchat
autogen-ext[openai]
python-dotenv
asyncio
```

## 💡 Usage

### Basic Usage

```bash
python main.py
```

### Input Formats

The system accepts multiple input formats:

1. **Structured Format**
   ```
   topic: climate change, argument: sea levels are rising due to human activity
   ```

2. **Simple Format**
   ```
   climate change, sea levels are rising due to human activity
   ```

3. **Topic Only**
   ```
   climate change
   ```

### Example Session

```
Welcome to the Automated Debate Coach!
Enter your debate topic and argument in one of these formats:
1. 'topic: climate change, argument: sea levels are rising'
2. 'climate change, sea levels are rising due to human activity'  
3. Just the topic: 'climate change'

Enter your debate topic and argument: climate change, sea levels are rising due to human activity

Parsed - Topic: 'climate change', User Argument: 'sea levels are rising due to human activity'

🚀 Starting debate preparation for: climate change
Working with our team of specialist agents...

============================================================
DEBATE PREPARATION RESULTS
============================================================

Topic: climate change
Your Argument: sea levels are rising due to human activity

📊 RESEARCHED FACTS:
  • Sea levels have risen by 20 cm since 1900 due to melting ice caps and thermal expansion
  • Global sea level rise is accelerating, currently at 3.3 mm per year
  • Arctic sea ice has declined at a rate of 13% per decade since 1979

💪 SUPPORTING ARGUMENTS:
  • Historical data shows consistent sea level rise correlating with industrial activity
  • Thermal expansion of oceans due to warming provides measurable evidence
  • Accelerating rate indicates human influence beyond natural cycles

🛡️ PREPARED REBUTTALS:
  • Counter natural variation claims with acceleration data
  • Address measurement accuracy concerns with satellite verification
  • Respond to ice age cycle arguments with timing evidence

🎯 ARGUMENT STRENGTH SCORE: 8/10
============================================================
```

## 📊 Supported Topics

The system comes pre-loaded with facts for:

- **Climate Change**: Temperature data, sea levels, CO2 levels, ice cap data
- **Universal Healthcare**: Cost comparisons, life expectancy, coverage statistics
- **Artificial Intelligence**: Economic impact, job displacement/creation, bias issues
- **Renewable Energy**: Cost trends, capacity potential, current market share

### Adding New Topics

To add new topics to the fact database:

1. Edit the `facts_data` list in the `init_fact_db()` function
2. Add tuples in the format: `('topic_name', 'fact_statement')`
3. Run the script to initialize the new data

```python
facts_data.append(('new_topic', 'Your fact statement here'))
```

## 🔧 Configuration

### Model Configuration

The system uses Gemini 2.0 Flash by default. To change models:

```python
model_client = OpenAIChatCompletionClient(
    model="your-preferred-model",  # Change this
    api_key=api_key,
    model_info=ModelInfo(
        vision=False,
        function_calling=True,
        json_output=True,
        family="unknown",
        structured_output=True
    )
)
```

### Termination Conditions

Adjust conversation limits:

```python
max_messages_termination = MaxMessageTermination(max_messages=15)  # Adjust as needed
```

## 📈 Performance Tips

1. **Database Optimization**: Regularly update the fact database with current information
2. **Token Management**: Monitor API usage for cost optimization
3. **Fact Relevance**: Use specific topic keywords for better fact retrieval
4. **Input Clarity**: Provide clear, specific arguments for better results

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify your `.env` file has the correct API key
   - Check API key permissions and quotas

2. **Database Errors**
   - Ensure `facts.db` is created in the project directory
   - Check file permissions

3. **Agent Coordination Issues**
   - Verify all agents have proper system messages
   - Check termination conditions

4. **Empty Results**
   - Ensure proper input formatting
   - Check if topic exists in the database
   - Verify agent message parsing

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Acknowledgments

- Built with [Microsoft AutoGen](https://github.com/microsoft/autogen)
- Powered by Google Gemini API
- SQLite for local data storage


**Happy Debating! 🎭**