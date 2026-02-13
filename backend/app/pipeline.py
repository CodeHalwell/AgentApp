"""
Document Processing Pipeline - Orchestrates multi-agent workflow.
CODE REVIEW EXERCISE: This file contains intentional issues including a race condition.
"""
from typing import Any, Dict, List
import uuid
from datetime import datetime
from app.agents.classifier import ClassifierAgent
from app.agents.extractor import ExtractorAgent
from app.agents.router import RouterAgent

class DocumentPipeline:
    """
    Orchestrates the document processing pipeline using multiple agents.
    Uses activity/turn-based approach where each agent processes in sequence.
    """
    
    def __init__(self):
        self.classifier = ClassifierAgent()
        self.extractor = ExtractorAgent()
        self.router = RouterAgent()
        self.results = {}  # ISSUE 5: Race condition - not thread-safe!
        self.active_tasks = []  # ISSUE 5: Race condition - shared mutable state
    
    def process(self, text: str) -> Dict[str, Any]:
        """
        Process a document through the multi-agent pipeline.
        ISSUE 2: No error handling at pipeline level.
        ISSUE 5: Race condition when multiple requests modify shared state.
        """
        task_id = str(uuid.uuid4())
        
        # ISSUE 5: Race condition - multiple threads can modify active_tasks simultaneously
        self.active_tasks.append(task_id)
        
        # Turn 1: Classification
        classification_result = self.classifier.process(text)
        
        # Turn 2: Extraction
        extraction_result = self.extractor.process(
            text, 
            classification_result["category"]
        )
        
        # Turn 3: Routing
        routing_result = self.router.process(
            classification_result["category"],
            extraction_result["extracted_data"]
        )
        
        # Compile final result
        final_result = {
            "task_id": task_id,
            "classification": classification_result,
            "extraction": extraction_result,
            "routing": routing_result,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # ISSUE 5: Race condition - multiple threads accessing results dict
        self.results[task_id] = final_result
        
        # ISSUE 5: Race condition - unsafe removal from list
        self.active_tasks.remove(task_id)
        
        return final_result
    
    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        # ISSUE 5: Race condition - reading from shared mutable state
        return {
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.results),
            "agents": {
                "classifier": "active",
                "extractor": "active",
                "router": "active"
            }
        }
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """Get all agent logs."""
        all_logs = []
        all_logs.extend(self.classifier.get_logs())
        all_logs.extend(self.extractor.get_logs())
        all_logs.extend(self.router.get_logs())
        return all_logs
    
    def get_result(self, task_id: str) -> Any:  # ISSUE 3: Poor types - using Any
        """Get result by task ID."""
        # ISSUE 2: No error handling - KeyError if task_id doesn't exist
        # ISSUE 5: Race condition - concurrent access to results dict
        return self.results[task_id]
