import requests
from typing import Dict, List, Any, Optional
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class LLMClientError(Exception):
    """Custom exception for LLM client errors"""
    pass

class LLMClient:
    def __init__(self, base_url: str = "https://api.mistral.ai/v1", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        reraise=True
    )
    def chat_completion(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        api_key: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send a request to the Mistral API with retry logic"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        try:
            start_time = time.time()
            response = requests.post(
                url, 
                headers=headers, 
                json=data, 
                timeout=self.timeout
            )
            latency = time.time() - start_time
            
            logger.info(f"LLM API call completed in {latency:.2f}s with status {response.status_code}")
            
            if response.status_code != 200:
                error_msg = f"LLM API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise LLMClientError(error_msg)
                
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error("LLM API request timed out")
            raise LLMClientError("Request to LLM API timed out")
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM API request failed: {str(e)}")
            raise LLMClientError(f"Request to LLM API failed: {str(e)}")
    
    def extract_response(self, api_response: Dict[str, Any]) -> str:
        """Extract the response content from the API response"""
        try:
            return api_response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract response from API result: {api_response}")
            raise LLMClientError(f"Invalid response format from LLM API: {str(e)}")# llm_client.py
"""
This is the llm_client.py file
"""

