from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.models import User, ScheduledTest
from app.schemas.schemas import ScheduledTest as ScheduledTestSchema, ScheduledTestCreate

router = APIRouter()


@router.post("/", response_model=ScheduledTestSchema)
def create_scheduled_test(
    test: ScheduledTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new scheduled test"""
    db_test = ScheduledTest(
        **test.dict(),
        company_id=current_user.company_id
    )
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    
    return db_test


@router.get("/", response_model=List[ScheduledTestSchema])
def list_scheduled_tests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List scheduled tests for the current user's company"""
    tests = db.query(ScheduledTest).filter(
        ScheduledTest.company_id == current_user.company_id
    ).offset(skip).limit(limit).all()
    
    return tests


@router.get("/{test_id}", response_model=ScheduledTestSchema)
def get_scheduled_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific scheduled test"""
    test = db.query(ScheduledTest).filter(ScheduledTest.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled test not found"
        )
    
    # Verify user belongs to the same company
    if test.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this scheduled test"
        )
    
    return test


@router.put("/{test_id}", response_model=ScheduledTestSchema)
def update_scheduled_test(
    test_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a scheduled test (toggle active status)"""
    test = db.query(ScheduledTest).filter(ScheduledTest.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled test not found"
        )
    
    # Verify user belongs to the same company
    if test.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this scheduled test"
        )
    
    test.is_active = is_active
    db.commit()
    db.refresh(test)
    
    return test
