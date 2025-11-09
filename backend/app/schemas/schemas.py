from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


# Company Schemas
class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class CompanyCreate(CompanyBase):
    pass


class Company(CompanyBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    company_id: int


class User(UserBase):
    id: int
    company_id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Topic Schemas
class TopicBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class TopicCreate(TopicBase):
    company_id: int


class Topic(TopicBase):
    id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# LLM Query Schemas
class LLMQueryCreate(BaseModel):
    prompt: str = Field(..., min_length=1)
    llm_provider: str = Field(..., pattern="^(anthropic|openai|google)$")
    model_name: Optional[str] = None
    topic_id: Optional[int] = None


class LLMQueryResponse(BaseModel):
    id: int
    prompt: str
    response: Optional[str] = None
    llm_provider: str
    model_name: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None
    latency_ms: Optional[int] = None
    created_at: datetime
    topic_id: Optional[int] = None
    
    class Config:
        from_attributes = True


# Evaluation Schemas
class EvaluationCreate(BaseModel):
    llm_query_id: int
    evaluation_type: str = Field(..., pattern="^(sentiment|accuracy|clarity)$")


class Evaluation(BaseModel):
    id: int
    llm_query_id: int
    evaluation_type: str
    score: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Scheduled Test Schemas
class ScheduledTestCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    prompt_template: str = Field(..., min_length=1)
    llm_providers: List[str]
    topic_id: Optional[int] = None
    cron_expression: str = Field(..., pattern=r'^[\d\*\-\,\/\s]+$')
    evaluation_types: Optional[List[str]] = None


class ScheduledTest(BaseModel):
    id: int
    name: str
    prompt_template: str
    llm_providers: List[str]
    topic_id: Optional[int] = None
    company_id: int
    cron_expression: str
    is_active: bool
    evaluation_types: Optional[List[str]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
