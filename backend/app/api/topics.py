from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.models import User, Topic
from app.schemas.schemas import Topic as TopicSchema, TopicCreate

router = APIRouter()


@router.post("/", response_model=TopicSchema)
def create_topic(
    topic: TopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new topic"""
    # Verify user belongs to the company
    if current_user.company_id != topic.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create topics for this company"
        )
    
    db_topic = Topic(**topic.dict())
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    
    return db_topic


@router.get("/", response_model=List[TopicSchema])
def list_topics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List topics for the current user's company"""
    topics = db.query(Topic).filter(
        Topic.company_id == current_user.company_id
    ).offset(skip).limit(limit).all()
    
    return topics


@router.get("/{topic_id}", response_model=TopicSchema)
def get_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific topic"""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Verify user belongs to the same company
    if topic.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this topic"
        )
    
    return topic
