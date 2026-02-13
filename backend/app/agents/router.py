"""
Router Agent - Routes documents to appropriate handlers.
CODE REVIEW EXERCISE: This file contains intentional issues.
"""
from typing import Any, Dict
from app.agents.base import AgentBase

class RouterAgent(AgentBase):
    """Agent that routes documents to appropriate downstream systems."""
    
    def __init__(self):
        super().__init__("router")
        self.routing_rules = {
            "invoice": "accounting_system",
            "receipt": "expense_system",
            "contract": "legal_system",
            "report": "document_management",
            "other": "manual_review"
        }
    
    def process(self, category: str, extracted_data: Dict) -> Dict[str, Any]:
        """
        Route the document to the appropriate system.
        ISSUE 2: No error handling for routing failures.
        """
        self.log(f"Routing {category} document")
        
        # ISSUE 2: No error handling - what if category not in routing_rules?
        destination = self.routing_rules[category]  # KeyError risk!
        
        # ISSUE 4: Security - No validation of extracted_data contents
        routing_result = {
            "destination": destination,
            "category": category,
            "data": extracted_data,  # Passing data without sanitization
            "agent": self.name,
            "status": "routed"
        }
        
        self.log(f"Routed to {destination}")
        return routing_result
