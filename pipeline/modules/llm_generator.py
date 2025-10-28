"""
LLM Code Generator Module
Generates code using Groq API.
"""

import os
import time
from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class LLMCodeGenerator:
    """Generates Python code using LLM via Groq API."""
    
    def __init__(
        self,
        model: str = "openai/gpt-oss-20b",
        temperature: float = 0.1,
        max_tokens: int = 8000
    ):
        """
        Initialize LLM Code Generator.
        
        Args:
            model: Groq model name to use
            temperature: Temperature for generation (0.0-1.0, lower = more deterministic)
            max_tokens: Maximum tokens to generate
        """
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_calls = 0
        
    def generate(self, prompt: str) -> str:
        """
        Generate code from prompt using LLM.
        
        Args:
            prompt: Input prompt for code generation
            
        Returns:
            Generated code as string
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Add rate limiting delay
            if self.api_calls > 0:
                time.sleep(1)  # Small delay between calls
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Python code golf expert specializing in grid transformations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            self.api_calls += 1
            raw_output = response.choices[0].message.content
            
            print(f"[LLM] API call #{self.api_calls} completed")
            return raw_output
            
        except Exception as e:
            print(f"[LLM Error] {e}")
            raise

