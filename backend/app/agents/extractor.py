"""
Extractor Agent - Extracts key information from documents.
CODE REVIEW EXERCISE: This file contains intentional issues.
"""
from typing import Any, Dict, List
import re
from app.agents.base import AgentBase

class ExtractorAgent(AgentBase):
    """Agent that extracts key information from documents."""
    
    def __init__(self):
        super().__init__("extractor")
    
    def process(self, text: str, category: str) -> Dict[str, Any]:
        """
        Extract relevant information based on document category.
        ISSUE 2: No error handling for regex or extraction failures.
        """
        self.log(f"Extracting data from {category} document")
        
        extracted_data = {}
        
        # ISSUE 2: No error handling for regex operations
        # ISSUE 4: Security - Regex without input validation (ReDoS risk)
        if category == "invoice":
            # Extract invoice number
            invoice_match = re.search(r'invoice[:\s#]+(\w+)', text, re.IGNORECASE)
            if invoice_match:
                extracted_data["invoice_number"] = invoice_match.group(1)
            
            # Extract amounts (simplified)
            amount_matches = re.findall(r'\$(\d+\.?\d*)', text)
            extracted_data["amounts"] = amount_matches
        
        elif category == "receipt":
            # Extract date
            date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})', text)
            if date_match:
                extracted_data["date"] = date_match.group(1)
            
            # Extract total
            total_match = re.search(r'total[:\s]+\$?(\d+\.?\d*)', text, re.IGNORECASE)
            if total_match:
                extracted_data["total"] = total_match.group(1)
        
        elif category == "contract":
            # Extract parties
            party_matches = re.findall(r'between\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
            extracted_data["parties"] = party_matches[:2]  # First two matches
        
        self.log(f"Extracted {len(extracted_data)} fields")
        
        return {
            "extracted_data": extracted_data,
            "agent": self.name
        }
