"""
File Writer Module
Saves validated code to files.
"""

import os
from typing import Optional


class FileWriter:
    """Writes validated code to output directory."""
    
    def __init__(self, output_dir: str):
        """
        Initialize FileWriter.
        
        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def save_code(self, task_id: int, code: str) -> str:
        """
        Save code to file.
        
        Args:
            task_id: Task identifier
            code: Python code to save
            
        Returns:
            Path to saved file
        """
        filename = f"task{task_id:03d}.py"
        file_path = os.path.join(self.output_dir, filename)
        
        with open(file_path, 'w') as f:
            f.write(code)
        
        print(f"[✓] Saved validated solution for task {task_id:03d} ({len(code)} bytes)")
        return file_path
    
    def file_exists(self, task_id: int) -> bool:
        """
        Check if solution file already exists.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if file exists
        """
        filename = f"task{task_id:03d}.py"
        file_path = os.path.join(self.output_dir, filename)
        return os.path.exists(file_path)

