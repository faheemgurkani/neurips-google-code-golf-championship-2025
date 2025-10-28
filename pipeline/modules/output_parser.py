"""
Output Parser Module
Extracts clean Python code from LLM output.
"""

import re
from typing import Optional


class OutputParser:
    """Parses and cleans LLM output to extract Python code."""
    
    @staticmethod
    def extract_code(raw_output: str) -> str:
        """
        Extract Python code from raw LLM output.
        
        Args:
            raw_output: Raw output from LLM
            
        Returns:
            Cleaned Python code
        """
        # Try to extract code from markdown blocks first
        python_block_match = re.findall(r'```python(.*?)```', raw_output, re.DOTALL)
        if python_block_match:
            code = python_block_match[0].strip()
        else:
            # Try generic code blocks
            code_block_match = re.findall(r'```(.*?)```', raw_output, re.DOTALL)
            if code_block_match:
                code = code_block_match[0].strip()
                # Remove language identifier if present
                code = re.sub(r'^python\s*', '', code, flags=re.MULTILINE)
            else:
                # If no code blocks, assume the whole thing is code (trimmed)
                code = raw_output.strip()
        
        # Ensure the code has a function definition
        if 'def p(g)' not in code and 'def p(g:)' not in code:
            # Try to find a function definition and use it as is
            code = code.strip()
        
        return code.strip()
    
    @staticmethod
    def extract_function_body(code: str) -> Optional[str]:
        """
        Extract just the function definition and body.
        
        Args:
            code: Full code string
            
        Returns:
            Function definition with body
        """
        # Look for def p(g) pattern
        pattern = r'(def\s+p\s*\([^)]*\):.*)'
        match = re.search(pattern, code, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

