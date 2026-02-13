"""
Classifier Agent - Classifies documents by type.
CODE REVIEW EXERCISE: This file contains intentional issues.
"""
from typing import Any, Dict
from app.agents.base import AgentBase

class ClassifierAgent(AgentBase):
    """Agent that classifies documents into categories."""
    
    def __init__(self):
        super().__init__("classifier")
        self.categories = ["invoice", "receipt", "contract", "report", "other"]
    
    def process(self, text: str) -> Dict[str, Any]:  # ISSUE 3: Should use proper response model
        """
        Classify the document based on its content.
        ISSUE 2: No error handling for processing failures.
        """
        self.log(f"Classifying document with {len(text)} characters")
        
        # ISSUE 2: No error handling - what if text is None or empty?
        text_lower = text.lower()
        
        # Simple keyword-based classification (simplified for exercise)
        category = "other"
        confidence = 0.5
        
        if "invoice" in text_lower or "bill" in text_lower:
            category = "invoice"
            confidence = 0.85
        elif "receipt" in text_lower:
            category = "receipt"
            confidence = 0.80
        elif "contract" in text_lower or "agreement" in text_lower:
            category = "contract"
            confidence = 0.90
        elif "report" in text_lower:
            category = "report"
            confidence = 0.75
        
        result = {
            "category": category,
            "confidence": confidence,
            "agent": self.name
        }
        
        self.log(f"Classified as {category} with confidence {confidence}")
        return result
