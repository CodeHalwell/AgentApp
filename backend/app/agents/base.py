"""
Agent base class and shared utilities.
CODE REVIEW EXERCISE: This file contains intentional issues.
"""
from typing import Any, Dict, Optional
from datetime import datetime

class AgentBase:
    """Base class for all agents in the pipeline."""
    
    def __init__(self, name: str):
        self.name = name
        self.logs = []  # ISSUE 3: Poor types - should be List[Dict[str, Any]]
        self.state = {}  # ISSUE 3: Poor types - should have proper type hints
    
    def log(self, message: str, level: str = "info"):
        """Log a message from this agent."""
        log_entry = {
            "agent": self.name,
            "message": message,
            "level": level,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logs.append(log_entry)
    
    def get_logs(self) -> Any:  # ISSUE 3: Poor types - using Any
        """Get all logs from this agent."""
        return self.logs
    
    def process(self, input_data: Any) -> Any:  # ISSUE 3: Poor types - using Any
        """Process input data. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement process method")
