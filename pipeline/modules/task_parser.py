"""
Task Parser Module
Parses task JSON files and extracts training/test data.
"""

import json
from typing import List, Dict, Any, Tuple


class TaskParser:
    """Parses task JSON files to extract input/output examples."""
    
    @staticmethod
    def load_task(file_path: str) -> Dict[str, Any]:
        """
        Load task data from JSON file.
        
        Args:
            file_path: Path to task JSON file
            
        Returns:
            Dictionary containing train, test, and arc-gen examples
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    
    @staticmethod
    def get_train_test(task_data: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
        """
        Extract train and test examples from task data.
        
        Args:
            task_data: Task data dictionary
            
        Returns:
            Tuple of (train_examples, test_examples)
        """
        train = task_data.get("train", [])
        test = task_data.get("test", [])
        return train, test
    
    @staticmethod
    def format_example(example: Dict) -> str:
        """
        Format an example for display in prompts.
        
        Args:
            example: Dictionary with 'input' and 'output' keys
            
        Returns:
            Formatted string representation
        """
        input_grid = example.get("input", [])
        output_grid = example.get("output", [])
        return f"Input: {input_grid}\nOutput: {output_grid}"

