import os
import logging
import requests
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from dotenv import load_dotenv
from datetime import datetime
from enum import Enum
from prometheus_client import Counter, Histogram, start_http_server, CollectorRegistry

load_dotenv()


# Load environment variables from .env file
load_dotenv()

# Initialize Logging Configuration
logging.basicConfig(level=logging.INFO)

# FastAPI Initialization
app = FastAPI(title="Advanced Prompt Engineering System")

# CORS middleware setup (for frontend-backend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus Metrics Setup
registry = CollectorRegistry()
REQUESTS_COUNTER = Counter('requests_total', 'Total API Requests', registry=registry)
RESPONSE_LATENCY = Histogram('response_latency_seconds', 'Response latency', registry=registry)

@app.on_event("startup")
def startup_event():
    start_http_server(8001, registry=registry)
    logging.info("Prometheus metrics server started on port 8001")

AUTHORIZED_API_KEYS = set(os.getenv("AUTHORIZED_API_KEYS", "").split(","))

def authenticate(api_key: str = Header(..., alias="X-API-Key")):
    if api_key not in AUTHORIZED_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

def sanitize_input(text: str) -> str:
    return text.translate(str.maketrans("", "", "<>{}[]()\\/|$%^&*;"))

class Domain(str, Enum):
    Research = "Research"
    Marketing = "Marketing"
    Legal = "Legal"
    Healthcare = "Healthcare"
    Education = "Education"
    Finance = "Finance"
    Software = "Software"
    CustomerService = "CustomerService"
    Story = "Story"

class Style(str, Enum):
    Innovation = "Innovation"
    Research = "Research"
    Implementation = "Implementation"
    Coding = "Coding"
    Analysis = "Analysis"
    Debugging = "Debugging"
    Reasoning = "Reasoning"
    Brainstorming = "Brainstorming"

class ResponseLength(str, Enum):
    Short = "Short"
    Detailed = "Detailed"

class PromptRequest(BaseModel):
    prompt: str
    domain: Domain
    style: Style
    response_length: ResponseLength

    @validator('prompt')
    def sanitize(cls, v):
        sanitized_prompt = sanitize_input(v)
        if len(sanitized_prompt) > 1000:
            raise ValueError("Prompt exceeds 1000 characters")
        return sanitized_prompt

DEEPSEEK_API_URL=os.getenv("DEEPSEEK_API_URL","https://api.deepseek.com/v1/chat/completions")
DEEPSEEK_API_KEY=os.getenv("DEEPSEEK_API_KEY")

def call_deepseek(prompt:str)->str:
  headers={"Authorization":f"Bearer {DEEPSEEK_API_KEY}"}
  payload={
      "model":"deepseek-chat",
      "messages":[{"role":"user","content":prompt}],
      "temperature":0.7,
      "top_p":0.9,
      "max_tokens":1500,
      "n":1}
  response=requests.post(DEEPSEEK_API_URL,json=payload,headers=headers)
  if response.status_code!=200:
      logging.error(f"DeepSeek API Error:{response.text}")
      raise HTTPException(status_code=503,detail="DeepSeek API unavailable")
  data=response.json()
  return data["choices"][0]["message"]["content"].strip()

class PromptOptimizer:

  DOMAIN_LOGIC={
      Domain.Research:"You are an expert researcher. Use adaptive thinking to explore multiple research methodologies systematically. Provide step-by-step reasoning (Chain-of-Thought) and clearly branch out possible research paths (Tree-of-Thought).",
      Domain.Marketing:"You are a seasoned marketing strategist. Employ adaptive thinking to explore innovative marketing strategies. Clearly outline your reasoning process (Chain-of-Thought) and explore multiple creative paths (Tree-of-Thought).",
      Domain.Legal:"You are a meticulous legal analyst. Utilize adaptive thinking to dissect complex legal scenarios. Explain your reasoning clearly step-by-step (CoT) and branch out potential legal interpretations (ToT).",
      Domain.Healthcare:"You are a healthcare systems architect. Use adaptive thinking to propose innovative healthcare solutions. Provide structured reasoning (CoT) and explore multiple solution pathways (ToT).",
      Domain.Education:"You are an educational technologist. Apply adaptive thinking to design personalized educational experiences. Clearly outline your thought process step-by-step (CoT) and explore various educational strategies (ToT).",
      Domain.Finance:"You are a financial analyst. Employ adaptive thinking to analyze complex financial scenarios deeply. Provide rigorous logical reasoning (CoT) and branch out multiple financial strategies (ToT).",
      Domain.Software:"You are a software architect. Utilize adaptive thinking for optimized software solutions. Clearly explain your coding logic step-by-step (CoT) and explore multiple architectural approaches (ToT).",
      Domain.CustomerService:"You are a customer service strategist. Employ adaptive thinking to craft empathetic interactions. Provide clear reasoning behind each interaction step-by-step (CoT) and explore diverse customer engagement methods (ToT).",
      Domain.Story:"You are a master storyteller. Utilize adaptive thinking to create captivating narratives with deep character development. Clearly outline plot progression step-by-step (CoT) and explore multiple narrative branches and possibilities (ToT)."
  }

  STYLE_LOGIC={
      Style.Innovation:"Encourage groundbreaking ideas with radical creativity and curiosity-driven exploration.",
      Style.Research:"Provide rigorous research methodologies with evidence-based insights supported by credible sources.",
      Style.Implementation:"Outline clear actionable implementation steps with timelines and resources.",
      Style.Coding:"Generate clean code with detailed explanations of logic behind every decision.",
      Style.Analysis:"Perform deep analytical reasoning supported by data-driven evidence.",
      Style.Debugging:"Explain debugging clearly step-by-step with detailed examples of common pitfalls.",
      Style.Reasoning:"Provide logical reasoning step-by-step clearly outlining each decision-making point.",
      Style.Brainstorming:"Generate creative ideas from minimal seed words that ignite curiosity and purpose-driven action."
  }

  def generate_prompt(self,data:PromptRequest)->str:
      
      base=self.DOMAIN_LOGIC[data.domain]
      style=self.STYLE_LOGIC[data.style]

      prompt=f"""Enhance this prompt using advanced adaptive thinking techniques including Chain-of-Thought and Tree-of-Thought methodologies.

Domain Context:
{base}

Prompt Style Instructions:
{style}

User Input:
{data.prompt}

The output should be {data.response_length.value.lower()}, highly structured with clearly actionable steps or ideas.

Provide the enhanced prompt explicitly as a new prompt ready to feed into an LLM."""

      return prompt

optimizer=PromptOptimizer()

@app.post("/enhance")
async def enhance(request:PromptRequest,api_key:str=Depends(authenticate)):
   REQUESTS_COUNTER.inc()
   start_time=datetime.now()

   enhanced_prompt=optimizer.generate_prompt(request)
   enhanced_response=call_deepseek(enhanced_prompt)

   elapsed_time=(datetime.now()-start_time).total_seconds()
   RESPONSE_LATENCY.observe(elapsed_time)

   return{
       'original_prompt':request.prompt,
       'enhanced_prompt':enhanced_response,
       'timestamp':datetime.utcnow().isoformat(),
       'latency_seconds':elapsed_time}

