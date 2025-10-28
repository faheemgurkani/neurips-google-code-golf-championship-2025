"""
Progress Tracker Module
Tracks and logs progress of task generation.
"""

import csv
import os
from datetime import datetime
from typing import Optional


class ProgressTracker:
    """Tracks progress and logs results to CSV."""
    
    def __init__(self, log_file: str = "logs/progress.csv"):
        """
        Initialize ProgressTracker.
        
        Args:
            log_file: Path to log file
        """
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Create log file with headers if it doesn't exist
        if not os.path.exists(log_file):
            with open(log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'task_id', 'status', 'code_length', 
                    'validation_passed', 'api_calls', 'details'
                ])
    
    def log(
        self,
        task_id: int,
        status: str,
        code_length: int = 0,
        validation_passed: bool = False,
        details: str = ""
    ):
        """
        Log an event to the progress file.
        
        Args:
            task_id: Task identifier
            status: Status of the task (e.g., 'validated_success', 'syntax_error', etc.)
            code_length: Length of generated code
            validation_passed: Whether validation passed
            details: Additional details
        """
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                task_id,
                status,
                code_length,
                validation_passed,
                details
            ])
    
    def get_stats(self) -> dict:
        """
        Get statistics about completed tasks.
        
        Returns:
            Dictionary with statistics
        """
        if not os.path.exists(self.log_file):
            return {}
        
        stats = {
            'total': 0,
            'success': 0,
            'failed_syntax': 0,
            'failed_validation': 0,
            'failed_exception': 0
        }
        
        with open(self.log_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stats['total'] += 1
                status = row['status']
                
                if 'success' in status.lower():
                    stats['success'] += 1
                elif 'syntax_error' in status.lower():
                    stats['failed_syntax'] += 1
                elif 'validation' in status.lower() and 'fail' in status.lower():
                    stats['failed_validation'] += 1
                elif 'exception' in status.lower():
                    stats['failed_exception'] += 1
        
        return stats

