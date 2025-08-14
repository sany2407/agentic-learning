import re
from crewai.tools import BaseTool
from typing import Type, Dict, Any
from pydantic import BaseModel, Field


class LaTeXValidatorToolInput(BaseModel):
    """Input schema for LaTeXValidatorTool."""
    latex_content: str = Field(..., description="The LaTeX document content to validate.")


class LaTeXValidatorTool(BaseTool):
    name: str = "LaTeX Validator"
    description: str = "Validates LaTeX syntax and identifies common formatting errors"
    args_schema: Type[BaseModel] = LaTeXValidatorToolInput

    def _run(self, latex_content: str) -> Dict[str, Any]:
        """
        Validates LaTeX document and returns detailed error analysis
        """
        errors = []
        
        # Check for basic document structure
        if not re.search(r'\\documentclass', latex_content):
            errors.append({
                'type': 'missing_documentclass',
                'message': 'Missing \\documentclass declaration',
                'line': 1,
                'severity': 'critical'
            })
        
        # Check for document environment
        if not re.search(r'\\begin\{document\}', latex_content):
            errors.append({
                'type': 'missing_begin_document',
                'message': 'Missing \\begin{document}',
                'severity': 'critical'
            })
        
        if not re.search(r'\\end\{document\}', latex_content):
            errors.append({
                'type': 'missing_end_document',
                'message': 'Missing \\end{document}',
                'severity': 'critical'
            })
        
        # Check for unmatched braces
        brace_count = latex_content.count('{') - latex_content.count('}')
        if brace_count != 0:
            errors.append({
                'type': 'unmatched_braces',
                'message': f'Unmatched braces: {abs(brace_count)} {"opening" if brace_count > 0 else "closing"} brace(s)',
                'severity': 'high'
            })
        
        # Check for unmatched environments
        begin_pattern = r'\\begin\{([^}]+)\}'
        end_pattern = r'\\end\{([^}]+)\}'
        
        begins = re.findall(begin_pattern, latex_content)
        ends = re.findall(end_pattern, latex_content)
        
        for env in begins:
            if env not in ends:
                errors.append({
                    'type': 'unclosed_environment',
                    'message': f'Unclosed environment: {env}',
                    'severity': 'high'
                })
        
        # Check for unmatched brackets and parentheses
        bracket_count = latex_content.count('[') - latex_content.count(']')
        if bracket_count != 0:
            errors.append({
                'type': 'unmatched_brackets',
                'message': f'Unmatched brackets: {abs(bracket_count)} {"opening" if bracket_count > 0 else "closing"} bracket(s)',
                'severity': 'medium'
            })
        
        # Check for common undefined commands
        undefined_commands = []
        command_pattern = r'\\([a-zA-Z]+)'
        commands = re.findall(command_pattern, latex_content)
        
        # Comprehensive list of common LaTeX commands
        common_commands = [
            'documentclass', 'begin', 'end', 'title', 'author', 'date', 'maketitle',
            'section', 'subsection', 'subsubsection', 'textbf', 'textit', 'usepackage', 
            'newpage', 'tableofcontents', 'label', 'ref', 'cite', 'bibliography', 'item',
            'chapter', 'paragraph', 'subparagraph', 'emph', 'underline', 'footnote',
            'includegraphics', 'caption', 'centering', 'left', 'right', 'textcolor',
            'newline', 'linebreak', 'pagebreak', 'clearpage', 'LaTeX', 'TeX'
        ]
        
        for cmd in commands:
            if cmd not in common_commands and len(cmd) > 1:
                undefined_commands.append(cmd)
        
        if undefined_commands:
            errors.append({
                'type': 'potentially_undefined_commands',
                'message': f'Potentially undefined commands: {", ".join(set(undefined_commands))}',
                'severity': 'medium'
            })
        
        # Check for missing packages for certain commands
        content_lower = latex_content.lower()
        if '\\includegraphics' in content_lower and '\\usepackage{graphicx}' not in content_lower:
            errors.append({
                'type': 'missing_package',
                'message': 'Command \\includegraphics requires \\usepackage{graphicx}',
                'severity': 'high'
            })
        
        return {
            'is_valid': len(errors) == 0,
            'error_count': len(errors),
            'errors': errors,
            'analysis_summary': f'Found {len(errors)} potential issues in the LaTeX document'
        }
