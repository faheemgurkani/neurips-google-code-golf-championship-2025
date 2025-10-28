"""
Task Manager Module
Handles loading and managing task files from the data directory.
"""

import os
from typing import List


class TaskManager:
    """Manages task files and paths for the pipeline."""
    
    def __init__(self, data_dir: str, start: int = 1, end: int = 100):
        """
        Initialize TaskManager.
        
        Args:
            data_dir: Path to the data directory containing task files
            start: Starting task number (inclusive)
            end: Ending task number (inclusive)
        """
        self.data_dir = data_dir
        self.start = start
        self.end = end
        
    def get_task_paths(self) -> List[str]:
        """
        Get list of task file paths.
        
        Returns:
            List of file paths for tasks task{start:03d} through task{end:03d}
        """
        paths = []
        for tid in range(self.start, self.end + 1):
            task_path = os.path.join(self.data_dir, f"task{tid:03d}.json")
            if os.path.exists(task_path):
                paths.append(task_path)
            else:
                print(f"[WARNING] Task file not found: {task_path}")
        return paths
    
    def get_task_num_from_path(self, path: str) -> int:
        """
        Extract task number from file path.
        
        Args:
            path: Path to task file (e.g., .../task001.json)
            
        Returns:
            Task number as integer
        """
        import re
        match = re.search(r'task(\d+)\.json', path)
        if match:
            return int(match.group(1))
        raise ValueError(f"Could not extract task number from path: {path}")

