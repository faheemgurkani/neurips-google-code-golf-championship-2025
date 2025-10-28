"""
Prompt Builder Module
Constructs prompts for LLM code generation.
"""

import json
from typing import List, Dict


INITIAL_PROMPT_TEMPLATE = """You are an expert at solving abstract reasoning challenges (ARC tasks) using pattern recognition.

CRITICAL: First analyze the examples carefully before coding:

1. **Dimension Analysis**: 
   - What are input dimensions? What are output dimensions?
   - Is output = input × N? Is it a tiling/replication pattern?
   - Example: 3×3 input → 9×9 output means 3× scaling

2. **Pattern Discovery**:
   - Compare ALL training examples - what's consistent across them?
   - Look at zeros vs non-zeros - different behaviors?
   - Is the input used as: (a) data to copy, (b) a mask/template, (c) coordinates?

3. **Tiling Patterns**:
   - If output is M×N times larger, each input cell might control an M×N block
   - CRITICAL: Does each block contain: (a) the input cell value REPEATED, or (b) the ENTIRE INPUT GRID COPIED?
   - Check: Do zero cells behave differently than non-zero cells?
   - Example: If input cell[i][j]=0 → block might be all zeros. If input cell[i][j]!=0 → block might be THE FULL INPUT replicated!

TRAIN EXAMPLES:
{train_examples}

TEST EXAMPLES (for validation):
{test_examples}

Now write a Python function `def p(g):` that implements the discovered pattern.

Requirements:
- Input `g`: list of lists of integers (0-9)
- Return: transformed grid (same format)
- Use ONLY Python standard library (no imports unless critical: collections, itertools, copy)
- Must work for ALL examples

Write ONLY Python code - no markdown, no explanations."""


REFINEMENT_PROMPT_TEMPLATE = """You are an expert at solving abstract reasoning challenges (ARC tasks). Your previous solution FAILED validation.

PREVIOUS ATTEMPT (FAILED):
```python
{previous_code}
```

VALIDATION ERROR:
{error_message}

TRAIN EXAMPLES (Your solution must pass ALL of these):
{train_examples}

TEST EXAMPLES (for pattern understanding):
{test_examples}

ANALYSIS OF FAILURE:
Your previous code didn't match the expected outputs. Carefully analyze:
1. What pattern did you miss? Compare your output vs expected output
2. Are you handling ALL cases correctly (zeros, non-zeros, edge cases)?
3. Is the transformation applied correctly to EVERY training example?
4. Did you misunderstand the grid transformation rule?

THINK STEP-BY-STEP:
- Re-examine the input→output transformation in each example
- Identify what's different between your approach and the actual pattern
- Consider: tiling, replication, masking, conditional logic, spatial relationships

Now write a CORRECTED Python function `def p(g):` that fixes the errors.

Requirements:
- Must pass ALL training examples
- Input `g`: list of lists of integers (0-9)
- Return: transformed grid (same format)
- Use ONLY Python standard library

Write ONLY Python code - no markdown, no explanations."""


class PromptBuilder:
    """Builds prompts for LLM code generation."""
    
    @staticmethod
    def build_prompt(
        task_id: int,
        train_examples: List[Dict],
        test_examples: List[Dict],
        previous_code: str = None,
        error_message: str = None
    ) -> str:
        """
        Build a prompt for code generation.
        
        Args:
            task_id: Task identifier
            train_examples: List of training examples with input/output pairs
            test_examples: List of test examples (for pattern understanding)
            previous_code: Failed code from previous attempt (for refinement)
            error_message: Error message from previous attempt
            
        Returns:
            Formatted prompt string
        """
        # Format train examples
        train_formatted = json.dumps(train_examples, indent=2)
        
        # Format test examples (limit to first 3 to save tokens)
        test_formatted = json.dumps(test_examples[:3], indent=2) if test_examples else "[]"
        
        # Use refinement prompt if previous attempt exists
        if previous_code and error_message:
            return REFINEMENT_PROMPT_TEMPLATE.format(
                previous_code=previous_code,
                error_message=error_message,
                train_examples=train_formatted,
                test_examples=test_formatted
            )
        else:
            # Initial attempt - use standard prompt
            return INITIAL_PROMPT_TEMPLATE.format(
                train_examples=train_formatted,
                test_examples=test_formatted
            )

