from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from typing import Dict, Any

from schemas import ChatRequest, ChatResponse, ErrorResponse, HealthCheck
from services.llm_client import LLMClient, LLMClientError
from core.guardrails import GuardRails
from core.prompts import PromptBuilder
from core.history import HistoryStore
from config.settings import get_settings, Settings

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
settings = get_settings()

# Initialize components
llm_client = LLMClient(timeout=settings.request_timeout)
guardrails = GuardRails()
prompt_builder = PromptBuilder()
history_store = HistoryStore(max_size=settings.history_size)

@router.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(status="healthy", version=settings.app_version)

@router.post("/v1/chat", response_model=ChatResponse)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def chat_with_mistral(
    request: Request,
    chat_request: ChatRequest
):
    try:
        # Generate session ID if not provided
        session_id = chat_request.session_id or history_store.generate_session_id()
        
        # Sanitize input
        sanitized_question = guardrails.sanitize_input(chat_request.question)
        
        # Check if question is about cultural topics
        is_cultural, error_msg = guardrails.is_cultural_topic(sanitized_question)
        if not is_cultural:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ErrorResponse(
                    code=400,
                    message=error_msg,
                    details={"topic": "non-cultural"}
                ).dict()
            )
        
        # Get conversation history
        history_messages = history_store.get_conversation_history(session_id)
        
        # Build system prompt with memory and localization
        memory_texts = [msg["content"] for msg in history_messages if msg["role"] == "user"]
        system_prompt = prompt_builder.build_system_prompt(
            memory=memory_texts, 
            locale=chat_request.locale
        )
        
        # Prepare messages for the LLM
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history_messages)
        messages.append({"role": "user", "content": sanitized_question})
        
        # Get API key from header (not from user input)
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required in X-API-Key header"
            )
        
        # Call LLM
        response = llm_client.chat_completion(
            model=settings.mistral_model,
            messages=messages,
            api_key=api_key
        )
        
        # Extract and process response
        reply = llm_client.extract_response(response)
        reply = guardrails.enforce_output_length(reply)
        
        # Store conversation history
        history_store.add_message(session_id, "user", sanitized_question)
        history_store.add_message(session_id, "assistant", reply)
        
        return ChatResponse(response=reply, session_id=session_id)
        
    except LLMClientError as e:
        logger.error(f"LLM client error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/v1/history/{session_id}")
async def clear_history(session_id: str):
    if history_store.clear_history(session_id):
        return {"message": "History cleared successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

# Rate limiting error handler
@router.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=ErrorResponse(
            code=429,
            message="Rate limit exceeded",
            details={"retry_after": f"{exc.retry_after} seconds"}
        ).dict()
    )# routes.py
"""
This is the routes.py file
"""

