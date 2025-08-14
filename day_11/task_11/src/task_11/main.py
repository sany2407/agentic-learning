#!/usr/bin/env python
import warnings
from datetime import datetime
from crew import LaTeXCorrectionCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def main():
    """
    Run the LaTeX Document Correction System.
    """
    # Example LaTeX document from requirements
    example_latex = r"""\documentclass{article}
\begin{document}
Hello World
\end{document}"""
    
    inputs = {
        'latex_content': example_latex,
        'current_year': str(datetime.now().year)
    }
    
    try:
        print("🚀 LaTeX Document Correction System")
        print("=" * 50)
        print("📝 Processing LaTeX document...")
        print("-" * 50)
        
        result = LaTeXCorrectionCrew().crew().kickoff(inputs=inputs)
        
        print("-" * 50)
        print("✅ Processing complete!")
        print("\n📊 Results:")
        print(result)
        
        print(f"\n📄 Full report saved as: latex_correction_report.md")
        print("\n🎉 LaTeX document has been analyzed and corrected successfully!")
        
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

if __name__ == "__main__":
    main()
