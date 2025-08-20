import re
from typing import Optional, Tuple
from functools import lru_cache

class GuardRails:
    def __init__(self):
        self.culture_keywords = [
            "culture", "cultural", "art", "arts", "music", "literature", "tradition", 
            "heritage", "festival", "custom", "society", "language", "dance", 
            "ritual", "belief", "museum", "history", "film", "painting", 
            "architecture", "sculpture", "folklore", "mythology", "religion",
            "philosophy", "anthropology", "archaeology", "ethnic", "national identity"
        ]
        
        # More sophisticated patterns for cultural topics
        self.culture_patterns = [
            r"(cultural|artistic|historical|traditional).*(practice|aspect|significance|context)",
            r"(work|piece) of (art|literature|music)",
            r"(historical|cultural) (event|period|figure|monument)",
            r"(traditional|folk) (dance|music|costume|craft)",
            r"^(how|what|when|where|why).*(culture|art|history|tradition)"
        ]
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        # Remove potentially harmful characters but preserve cultural content
        text = re.sub(r'[<>{}[\]$`\\]', '', text)
        # Limit length to prevent abuse
        return text[:2000]
    
    def is_cultural_topic(self, text: str) -> Tuple[bool, Optional[str]]:
        """Check if the question is about cultural topics using multiple approaches"""
        text_lower = text.lower()
        
        # 1. Keyword matching (basic but fast)
        if any(keyword in text_lower for keyword in self.culture_keywords):
            return True, None
        
        # 2. Pattern matching for more complex cultural references
        for pattern in self.culture_patterns:
            if re.search(pattern, text_lower):
                return True, None
        
        # 3. If none of the above, it's likely not a cultural topic
        error_msg = (
            "This assistant only answers culture-related questions. "
            "Please rephrase your question to focus on arts, traditions, heritage, "
            "history, or any other cultural topics."
        )
        return False, error_msg
    
    def enforce_output_length(self, text: str, max_words: int = 200) -> str:
        """Ensure response doesn't exceed word limit"""
        words = text.split()
        if len(words) > max_words:
            # Find a good stopping point near the limit
            truncated = " ".join(words[:max_words])
            # Try to end at a sentence boundary
            last_period = truncated.rfind('.')
            last_question = truncated.rfind('?')
            last_exclamation = truncated.rfind('!')
            
            end_pos = max(last_period, last_question, last_exclamation)
            if end_pos > 0:
                return truncated[:end_pos+1] + " [Response truncated due to length]"
            else:
                return truncated + "... [Response truncated due to length]"
        return text# guardrails.py
"""
This is the guardrails.py file
"""

