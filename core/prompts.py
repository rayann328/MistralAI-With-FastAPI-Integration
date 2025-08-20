import json
from pathlib import Path
from typing import Dict, List

class PromptBuilder:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.prompts_dir.mkdir(exist_ok=True)
        self.load_prompts()
    
    def load_prompts(self):
        # Default prompts that can be overridden by files
        self.prompts = {
            "role": "You are a friendly, precise cultural assistant for quick, factual guidance",
            "task": "Answer cultural questions clearly and briefly. Prioritize accuracy, define terms, and add one actionable tip when helpful",
            "constraints": "Do not fabricate references. If unsure, say so briefly. Avoid policy, medical, or legal advice. Keep answers under 200 words when possible",
            "style": "Tone: warm, concise, non-patronizing. Use simple sentences and neutral vocabulary.",
            "output_format": "Answer using this structure:\n1) Direct answer (2-4 sentences)\n2) Optional bullets (max 3)\n3) One follow-up question on user intent"
        }
        
        # Load prompts from files if they exist
        for prompt_key in self.prompts.keys():
            prompt_file = self.prompts_dir / f"{prompt_key}.txt"
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    self.prompts[prompt_key] = f.read().strip()
    
    def build_system_prompt(self, memory: List[str] = None, locale: str = "en-US") -> str:
        system_prompt = f"{self.prompts['role']}\n\nTask:\n{self.prompts['task']}\n\nConstraints:\n{self.prompts['constraints']}\n\nStyle:\n{self.prompts['style']}\n\nOutput format:\n{self.prompts['output_format']}"
        
        if memory:
            mem_text = "Conversation memory:\n-" + "\n-".join(memory)
            system_prompt += f"\n\n{mem_text}"
        
        # Add localization note if not default
        if locale != "en-US":
            system_prompt += f"\n\nNote: Respond in a culturally appropriate way for {locale}."
        
        return system_prompt
    
    def update_prompt(self, key: str, content: str):
        if key in self.prompts:
            self.prompts[key] = content
            # Save to file
            prompt_file = self.prompts_dir / f"{key}.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(content)# prompts.py
"""
This is the prompts.py file
"""

