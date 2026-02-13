"""
Main FastAPI application entry point.
CODE REVIEW EXERCISE: This file contains intentional issues for review.
"""
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Any
import json

from app.agents.classifier import ClassifierAgent
from app.agents.extractor import ExtractorAgent
from app.agents.router import RouterAgent
from app.pipeline import DocumentPipeline

app = FastAPI(title="Agent Document Processing API")

# ISSUE 1: Security - Overly permissive CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should be restricted to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = DocumentPipeline()

@app.get("/")
async def root():
    return {"message": "Agent Document Processing API"}

@app.post("/process")
async def process_document(file: UploadFile = File(...)) -> Any:  # ISSUE 3: Poor types - using Any
    """
    Process a document through the multi-agent pipeline.
    ISSUE 2: No error handling - missing try-catch blocks
    """
    # ISSUE 2: No error handling for file operations
    content = await file.read()
    text = content.decode('utf-8')  # Could fail with binary files
    
    # ISSUE 4: Security - No input validation on file size or content
    result = pipeline.process(text)
    
    return result

@app.get("/status")
async def get_status() -> dict:  # Better typing but inconsistent
    """Get current pipeline status."""
    # ISSUE 2: No error handling
    status = pipeline.get_status()
    return status

@app.get("/logs")
async def get_logs():  # ISSUE 3: Missing return type annotation
    """Get agent logs."""
    # ISSUE 2: No error handling for log retrieval
    logs = pipeline.get_logs()
    return logs

@app.get("/results/{task_id}")
async def get_result(task_id: str):  # ISSUE 3: Missing return type annotation
    """Get classification result by task ID."""
    # ISSUE 4: Security - No input validation on task_id (SQL injection risk if using DB)
    result = pipeline.get_result(task_id)
    return result
