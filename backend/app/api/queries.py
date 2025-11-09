from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.models import User, LLMQuery, Topic
from app.schemas.schemas import LLMQueryCreate, LLMQueryResponse
from app.services.llm_clients import LLMClientFactory

router = APIRouter()


@router.post("/", response_model=LLMQueryResponse)
async def create_query(
    query: LLMQueryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create and execute an LLM query"""
    # Verify topic belongs to user's company if provided
    if query.topic_id:
        topic = db.query(Topic).filter(Topic.id == query.topic_id).first()
        if not topic or topic.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Topic not found or not authorized"
            )
    
    # Create the query record
    db_query = LLMQuery(
        prompt=query.prompt,
        llm_provider=query.llm_provider,
        model_name=query.model_name,
        user_id=current_user.id,
        company_id=current_user.company_id,
        topic_id=query.topic_id,
        status="pending"
    )
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    
    # Execute the query
    try:
        client = LLMClientFactory.get_client(query.llm_provider)
        result = await client.query(query.prompt, query.model_name)
        
        # Update the query with results
        db_query.response = result["response"]
        db_query.model_name = result["model_name"]
        db_query.tokens_used = result["tokens_used"]
        db_query.latency_ms = result["latency_ms"]
        db_query.status = result["status"]
        db_query.error_message = result["error_message"]
        
        db.commit()
        db.refresh(db_query)
        
    except Exception as e:
        db_query.status = "failed"
        db_query.error_message = str(e)
        db.commit()
        db.refresh(db_query)
    
    return db_query


@router.get("/", response_model=List[LLMQueryResponse])
def list_queries(
    skip: int = 0,
    limit: int = 100,
    topic_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List queries for the current user's company"""
    query = db.query(LLMQuery).filter(LLMQuery.company_id == current_user.company_id)
    
    if topic_id:
        query = query.filter(LLMQuery.topic_id == topic_id)
    
    queries = query.order_by(LLMQuery.created_at.desc()).offset(skip).limit(limit).all()
    
    return queries


@router.get("/{query_id}", response_model=LLMQueryResponse)
def get_query(
    query_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific query"""
    query = db.query(LLMQuery).filter(LLMQuery.id == query_id).first()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Verify user belongs to the same company
    if query.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this query"
        )
    
    return query
