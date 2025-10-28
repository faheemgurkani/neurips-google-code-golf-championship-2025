"""
Code Validator Module
Validates generated code using code_golf_utils.
"""

import ast
import copy
import json
import importlib.util
import os
import sys
import tempfile
import traceback
import numpy as np


class CodeValidator:
    """Validates Python code syntax and functionality."""
    
    @staticmethod
    def is_syntax_valid(code: str) -> bool:
        """
        Check if code has valid Python syntax.
        
        Args:
            code: Python code to validate
            
        Returns:
            True if syntax is valid, False otherwise
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            print(f"[Syntax Error] {e}")
            return False
    
    @staticmethod
    def passes_training_examples(task_data: dict, code: str) -> tuple[bool, str]:
        """
        Test if generated code passes training examples.
        
        Args:
            task_data: Dictionary with 'train' and 'test' examples
            code: Generated Python code
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Create temporary file with the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
                # Write the function to the file
                tmp.write(code)
                tmp_path = tmp.name
            
            # Import the module
            module_name = f"_temp_task_{hash(tmp_path) % 100000}"
            spec = importlib.util.spec_from_file_location(module_name, tmp_path)
            if spec is None:
                return False, "Could not create module spec"
            
            module = sys.modules[module_name] = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if function p exists
            if not hasattr(module, 'p'):
                os.remove(tmp_path)
                return False, "Function p() not found"
            
            program = getattr(module, 'p')
            if not callable(program):
                os.remove(tmp_path)
                return False, "p is not callable"
            
            # Test on train examples
            train_examples = task_data.get("train", [])
            num_correct = 0
            total = len(train_examples)
            
            for example in train_examples:
                try:
                    input_grid = copy.deepcopy(example["input"])
                    expected = example["output"]
                    
                    # Run the program
                    result = program(input_grid)
                    
                    # Compare results using numpy
                    result_np = np.array(result, dtype=int)
                    expected_np = np.array(expected, dtype=int)
                    
                    if np.array_equal(result_np, expected_np):
                        num_correct += 1
                    else:
                        print(f"[Validation] Mismatch in example")
                        
                except Exception as e:
                    print(f"[Validation Error] {e}")
                    pass
            
            # Clean up
            os.remove(tmp_path)
            
            success_rate = num_correct / total if total > 0 else 0
            passed = (num_correct == total)
            
            message = f"Passed {num_correct}/{total} train examples"
            
            return passed, message
            
        except Exception as e:
            print(f"[Validator Error] {e}\n{traceback.format_exc()}")
            return False, str(e)
    
    @staticmethod
    def validate_code_length(code: str, max_length: int = 10000) -> bool:
        """
        Check if code is within acceptable length limits.
        
        Args:
            code: Python code
            max_length: Maximum allowed length
            
        Returns:
            True if within limits
        """
        return len(code) <= max_length

