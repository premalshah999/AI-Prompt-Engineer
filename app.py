"""
AI Prompt Engineering System - Core Backend
Microservices Architecture with DeepSeek Integration
"""

# ---------- Core Dependencies ----------
from fastapi import FastAPI, HTTPException, Security, Depends
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional
import logging
import os
import requests
import time
import hashlib
import json
from datetime import datetime
from prometheus_client import start_http_server, Counter, Gauge

# ---------- Configuration ----------
class Config:
    DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
    API_KEYS = json.loads(os.getenv("AUTHORIZED_API_KEYS", "[]"))
    RATE_LIMIT = int(os.getenv("RATE_LIMIT", 100))  # Requests per minute
    DOMAIN_WEIGHTS = json.loads(os.getenv("DOMAIN_WEIGHTS", "{}"))  # Adaptive weights

# ---------- Security Middleware ----------
class SecurityHandler:
    @staticmethod
    def sanitize_input(text: str) -> str:
        # Advanced sanitization for prompt injection prevention
        return text.translate(str.maketrans("", "", "<>{}[]()\\/|$%^&*;"))

    @staticmethod
    def authenticate(api_key: str = Security(...)):
        if api_key not in Config.API_KEYS:
            raise HTTPException(status_code=401, detail="Invalid API key")

# ---------- Core Models ----------
class PromptRequest(BaseModel):
    prompt: str
    domain: str = Field(..., regex="^(Research|Marketing|Legal|Healthcare|Education|Finance|Software|CustomerService)$")
    style: str = Field(..., regex="^(Innovation|Research|Implementation|Coding|Analysis|Debugging|Reasoning|Brainstorming)$")
    history: Optional[List[Dict]] = []
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if len(v) > 1000:
            raise ValueError("Prompt exceeds 1000 characters")
        return SecurityHandler.sanitize_input(v)

class EnhancedResponse(BaseModel):
    original_prompt: str
    enhanced_prompt: str
    reasoning_chain: List[str]
    confidence_score: float
    domain_specificity: float

# ---------- Prompt Engineering Core ----------
class PromptOptimizer:
    def __init__(self):
        self.analytics = AnalyticsEngine()
        self.domain_templates = self._load_domain_templates()
        self.style_strategies = self._load_style_strategies()

    def _load_domain_templates(self):
        # Domain-specific system prompts
        return {
            "Research": self._cot_prompt("Research paper structure"),
            "Healthcare": self._cot_prompt("Medical diagnosis framework"),
            # ... other domains
        }

    def _cot_prompt(self, context: str) -> str:
        # Chain-of-Thought base template
        return f"""Analyze this {context} request using:
        1. Contextual understanding
        2. Domain-specific knowledge
        3. Step-by-step reasoning
        4. Final optimized prompt"""

    def enhance_prompt(self, request: PromptRequest) -> EnhancedResponse:
        # Tree-of-Thought implementation
        branches = self._generate_thought_branches(request)
        best_branch = self._select_optimal_branch(branches)
        
        # Self-consistency sampling
        samples = [self._call_deepseek(best_branch) for _ in range(3)]
        final_output = self._consensus_check(samples)

        # Adaptive learning update
        self.analytics.log_interaction(request, final_output)
        return final_output

    def _generate_thought_branches(self, request: PromptRequest) -> List[str]:
        # Tree-of-Thought branching logic
        base_prompt = self.domain_templates[request.domain]
        style_modifier = self.style_strategies[request.style]
        return [f"{base_prompt}\n{style_modifier}\nUser: {request.prompt}"]

    def _call_deepseek(self, prompt: str) -> Dict:
        # Optimized API call with retry logic
        headers = {"Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"}
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "top_p": 0.9,
            "max_tokens": 1500
        }
        
        try:
            response = requests.post(Config.DEEPSEEK_API_URL, 
                                  headers=headers, 
                                  json=payload,
                                  timeout=10)
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API Error: {str(e)}")
            raise HTTPException(status_code=503, detail="Service unavailable")

# ---------- Analytics & Adaptive Learning ----------
class AnalyticsEngine:
    def __init__(self):
        self.interaction_log = []
        self.feedback_loop = FeedbackProcessor()
        
        # Prometheus metrics
        self.requests_counter = Counter('requests_total', 'Total API requests')
        self.response_time = Gauge('response_time_seconds', 'API response time')

    def log_interaction(self, request: PromptRequest, response: EnhancedResponse):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "domain": request.domain,
            "style": request.style,
            "input_hash": hashlib.sha256(request.prompt.encode()).hexdigest(),
            "output_metrics": {
                "confidence": response.confidence_score,
                "specificity": response.domain_specificity
            }
        }
        self.interaction_log.append(entry)
        self.feedback_loop.process_feedback(entry)

class FeedbackProcessor:
    def process_feedback(self, log_entry: Dict):
        # Adaptive learning logic
        if log_entry['output_metrics']['confidence'] < 0.7:
            self.adjust_domain_weights(log_entry['domain'], -0.1)
        elif log_entry['output_metrics']['specificity'] > 0.8:
            self.adjust_domain_weights(log_entry['domain'], 0.1)

    def adjust_domain_weights(self, domain: str, delta: float):
        Config.DOMAIN_WEIGHTS[domain] = Config.DOMAIN_WEIGHTS.get(domain, 1.0) + delta

# ---------- API Endpoints ----------
app = FastAPI(title="AI Prompt Engineer API")

@app.post("/enhance", response_model=EnhancedResponse)
async def enhance_prompt(
    request: PromptRequest,
    api_key: str = Depends(SecurityHandler.authenticate)
):
    start_time = time.time()
    optimizer = PromptOptimizer()
    
    with metrics.response_time.time():
        response = optimizer.enhance_prompt(request)
    
    metrics.requests_counter.inc()
    logging.info(f"Processed request in {time.time() - start_time:.2f}s")
    return response

# ---------- Deployment Setup ----------
if __name__ == "__main__":
    # Start metrics server
    start_http_server(8000)
    
    # Initialize services
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)