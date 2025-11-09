from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import anthropic
import openai
import google.generativeai as genai
from app.core.config import settings


class BaseLLMClient(ABC):
    """Base class for LLM clients"""
    
    @abstractmethod
    async def query(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Query the LLM and return response with metadata"""
        pass


class AnthropicClient(BaseLLMClient):
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.default_model = "claude-3-sonnet-20240229"
    
    async def query(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        try:
            model_name = model or self.default_model
            response = self.client.messages.create(
                model=model_name,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            return {
                "response": response.content[0].text,
                "model_name": model_name,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "latency_ms": latency_ms,
                "status": "completed",
                "error_message": None
            }
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return {
                "response": None,
                "model_name": model or self.default_model,
                "tokens_used": None,
                "latency_ms": latency_ms,
                "status": "failed",
                "error_message": str(e)
            }


class OpenAIClient(BaseLLMClient):
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.default_model = "gpt-3.5-turbo"
    
    async def query(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        try:
            model_name = model or self.default_model
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            return {
                "response": response.choices[0].message.content,
                "model_name": model_name,
                "tokens_used": response.usage.total_tokens,
                "latency_ms": latency_ms,
                "status": "completed",
                "error_message": None
            }
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return {
                "response": None,
                "model_name": model or self.default_model,
                "tokens_used": None,
                "latency_ms": latency_ms,
                "status": "failed",
                "error_message": str(e)
            }


class GoogleClient(BaseLLMClient):
    def __init__(self):
        genai.configure(api_key=settings.google_api_key)
        self.default_model = "gemini-pro"
    
    async def query(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        try:
            model_name = model or self.default_model
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            return {
                "response": response.text,
                "model_name": model_name,
                "tokens_used": None,  # Google doesn't provide token count easily
                "latency_ms": latency_ms,
                "status": "completed",
                "error_message": None
            }
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return {
                "response": None,
                "model_name": model or self.default_model,
                "tokens_used": None,
                "latency_ms": latency_ms,
                "status": "failed",
                "error_message": str(e)
            }


class LLMClientFactory:
    """Factory to create LLM clients"""
    
    @staticmethod
    def get_client(provider: str) -> BaseLLMClient:
        clients = {
            "anthropic": AnthropicClient,
            "openai": OpenAIClient,
            "google": GoogleClient
        }
        
        client_class = clients.get(provider.lower())
        if not client_class:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        
        return client_class()
