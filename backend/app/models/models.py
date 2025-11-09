from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    users = relationship("User", back_populates="company")
    topics = relationship("Topic", back_populates="company")
    llm_queries = relationship("LLMQuery", back_populates="company")


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    company = relationship("Company", back_populates="users")
    llm_queries = relationship("LLMQuery", back_populates="user")


class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    company = relationship("Company", back_populates="topics")
    llm_queries = relationship("LLMQuery", back_populates="topic")


class LLMQuery(Base):
    __tablename__ = "llm_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text)
    llm_provider = Column(String(50), nullable=False)  # anthropic, openai, google
    model_name = Column(String(100))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    status = Column(String(50), default="pending")  # pending, completed, failed
    error_message = Column(Text)
    tokens_used = Column(Integer)
    latency_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="llm_queries")
    company = relationship("Company", back_populates="llm_queries")
    topic = relationship("Topic", back_populates="llm_queries")
    evaluations = relationship("Evaluation", back_populates="llm_query")


class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    llm_query_id = Column(Integer, ForeignKey("llm_queries.id"), nullable=False)
    evaluation_type = Column(String(50), nullable=False)  # sentiment, accuracy, clarity
    score = Column(Float)
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    llm_query = relationship("LLMQuery", back_populates="evaluations")


class ScheduledTest(Base):
    __tablename__ = "scheduled_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    prompt_template = Column(Text, nullable=False)
    llm_providers = Column(JSON, nullable=False)  # List of providers to test
    topic_id = Column(Integer, ForeignKey("topics.id"))
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    cron_expression = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    evaluation_types = Column(JSON)  # List of evaluation types to run
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    topic = relationship("Topic")
