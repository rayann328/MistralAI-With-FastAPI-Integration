from pydantic import BaseModel, Field, constr
from typing import Optional, List, Dict, Any
from enum import Enum

class ModelName(str, Enum):
    MISTRAL_TINY = "mistral-tiny"
    MISTRAL_SMALL = "mistral-small"
    MISTRAL_MEDIUM = "mistral-medium"

class ChatRequest(BaseModel):
    question: constr(max_length=1000) = Field(..., description="User question")
    session_id: Optional[str] = Field(None, description="Session identifier")
    locale: Optional[str] = Field("en-US", description="User locale for i18n")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Assistant response")
    session_id: Optional[str] = Field(None, description="Session identifier")

class ErrorResponse(BaseModel):
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

class HealthCheck(BaseModel):
    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")# schemas.py
"""
This is the schemas.py file
"""

