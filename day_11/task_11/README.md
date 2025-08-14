# LaTeX Document Correction System

A sophisticated multi-agent system built with CrewAI that analyzes and corrects LaTeX documents using AI-powered agents.

## 🚀 Features

- **Multi-Agent Architecture**: Uses three specialized agents working together
- **Comprehensive Analysis**: Identifies syntax errors, formatting issues, and structural problems
- **Intelligent Correction**: Automatically fixes identified issues while preserving document intent
- **Custom Validation Tool**: Built-in LaTeX syntax validator with detailed error reporting
- **Sequential Processing**: Analysis → Correction workflow for optimal results

## 🏗️ System Architecture

### Agents

1. **Manager Agent**
   - Oversees the entire analysis and correction process
   - Ensures quality and comprehensive error resolution
   - Coordinates between analysis and correction teams

2. **Document Analyzer Agent**
   - Identifies syntax and formatting errors
   - Uses custom LaTeXValidatorTool for systematic error detection
   - Provides detailed analysis with severity classifications

3. **Document Corrector Agent**
   - Fixes identified errors while maintaining original intent
   - Ensures document compilability and best practices
   - Preserves content and formatting intentions

### Custom Tools

- **LaTeXValidatorTool**: Custom tool for LaTeX syntax validation
  - Checks document structure (documentclass, begin/end document)
  - Validates brace, bracket, and environment matching
  - Identifies potentially undefined commands
  - Detects missing package requirements

## 📋 Requirements

- Python 3.8+
- CrewAI framework
- Google Gemini API key (or other supported LLM provider)
- Internet connection for AI model access

## 🛠️ Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install crewai
   ```

3. **Set up your API key**:
   - Get a Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Set your API key as an environment variable:
     ```bash
     export GEMINI_API_KEY=your_actual_gemini_api_key_here
     ```
   - Or create a `.env` file in the project root with:
     ```
     GEMINI_API_KEY=your_actual_gemini_api_key_here
     ```

## 🎯 Usage

### Basic Usage

Run the system with the included example:

```bash
cd task_11/src/task_11
python main.py
```

### Custom LaTeX Document

To process your own LaTeX document, modify the `example_latex` variable in the `main()` function:

```python
# Replace the example_latex content with your document
example_latex = r"""\documentclass{article}
\begin{document}
Your LaTeX content here
\end{document}"""
```

### Programmatic Usage

```python
from latest_ai_development.crew import LaTeXCorrectionCrew

# Your LaTeX content
latex_content = r"""\documentclass{article}
\begin{document}
Hello World
\end{document}"""

# Process the document
result = LaTeXCorrectionCrew().crew().kickoff(inputs={'latex_content': latex_content})
```

## 📊 Output

The system generates:

1. **Console Output**: Real-time processing status and results summary
2. **Markdown Report**: Comprehensive analysis and correction report saved to `latex_correction_report.md`
3. **Structured Results**: Python dictionary with analysis and corrected document

### Report Contents

- **Executive Summary**: Overall document health assessment
- **Original Document**: Input LaTeX content
- **Analysis Report**: Detailed error analysis with severity classifications
- **Corrected Document**: Fixed LaTeX code ready for compilation
- **Results Summary**: Processing statistics and metadata

## 🔍 Example Analysis

The system can identify and fix various LaTeX issues:

- **Critical Errors**: Missing documentclass, unclosed environments
- **Syntax Issues**: Unmatched braces, brackets, parentheses
- **Package Problems**: Missing usepackage declarations
- **Structural Issues**: Improper sectioning, formatting inconsistencies
- **Best Practice Violations**: Non-standard command usage

## 🎨 Example Input/Output

### Input (with errors):
```latex
\documentclass{article}
\begin{document}
\section{Introduction}
\begin{itemize}
\item First item
\item Second item
% Missing \end{itemize}

\section{Mathematics}
\[
x^2 + y^2 = z^2
\]

\end{document}
```

### Output (corrected):
```latex
\documentclass{article}
\usepackage{amsmath}

\begin{document}
\section{Introduction}
\begin{itemize}
\item First item
\item Second item
\end{itemize}

\section{Mathematics}
\[
x^2 + y^2 = z^2
\]

\end{document}
```

## 🔧 Configuration

### Agent Settings

The system uses three specialized agents with optimized parameters:

- **Manager Agent**: Oversees with delegation capabilities
- **Document Analyzer**: Uses LaTeXValidatorTool for validation
- **Document Corrector**: Focuses on error correction and optimization

### Customization

You can modify agent behaviors, validation rules, and processing parameters in the YAML configuration files:
- `config/agents.yaml` - Agent configurations
- `config/tasks.yaml` - Task configurations
- `tools/custom_tool.py` - Custom validation tool

## 🚨 Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your environment variable contains a valid API key
2. **Import Errors**: Install all dependencies with `pip install crewai`
3. **Network Issues**: Check your internet connection for AI model access
4. **Memory Issues**: Large documents may require more processing time

### Error Messages

- `GEMINI_API_KEY environment variable is required`: Set up your API key
- Import errors: Install missing dependencies

## 📈 Performance

- **Processing Time**: Typically 30-60 seconds for standard documents
- **Document Size**: Handles documents up to 4000 tokens effectively
- **Error Detection**: Comprehensive coverage of common LaTeX issues
- **Correction Quality**: High accuracy with content preservation


**Built with CrewAI** - Advanced Multi-Agent Systems for Complex Tasks
