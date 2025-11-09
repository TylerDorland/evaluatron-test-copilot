from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.models import User, Evaluation as EvaluationModel, LLMQuery
from app.schemas.schemas import Evaluation as EvaluationSchema, EvaluationCreate
from app.services.evaluation_service import EvaluationService

router = APIRouter()
evaluation_service = EvaluationService()


@router.post("/", response_model=EvaluationSchema)
def create_evaluation(
    evaluation: EvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create and run an evaluation on an LLM query"""
    # Get the LLM query
    query = db.query(LLMQuery).filter(LLMQuery.id == evaluation.llm_query_id).first()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Verify user belongs to the same company
    if query.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to evaluate this query"
        )
    
    # Check if query has a response
    if not query.response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot evaluate query without a response"
        )
    
    # Run the evaluation
    try:
        result = evaluation_service.evaluate(query.response, evaluation.evaluation_type)
        
        # Create evaluation record
        db_evaluation = EvaluationModel(
            llm_query_id=evaluation.llm_query_id,
            evaluation_type=evaluation.evaluation_type,
            score=result["score"],
            details=result["details"]
        )
        db.add(db_evaluation)
        db.commit()
        db.refresh(db_evaluation)
        
        return db_evaluation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/query/{query_id}", response_model=List[EvaluationSchema])
def get_query_evaluations(
    query_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all evaluations for a specific query"""
    # Get the query
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
            detail="Not authorized to view evaluations for this query"
        )
    
    evaluations = db.query(EvaluationModel).filter(
        EvaluationModel.llm_query_id == query_id
    ).all()
    
    return evaluations


@router.get("/{evaluation_id}", response_model=EvaluationSchema)
def get_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific evaluation"""
    evaluation = db.query(EvaluationModel).filter(
        EvaluationModel.id == evaluation_id
    ).first()
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )
    
    # Verify user belongs to the same company
    query = db.query(LLMQuery).filter(LLMQuery.id == evaluation.llm_query_id).first()
    if query.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this evaluation"
        )
    
    return evaluation
