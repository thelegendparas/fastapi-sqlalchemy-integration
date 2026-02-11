#python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from db.session import get_db, check_db_health, init_db
from db import crud, models
from db.schemas import User, UserCreate, UserUpdate, UserProfile, UserProfileCreate

# Initialize database tables
init_db()

app = FastAPI(
    title="User Management API",
    description="FastAPI + SQLAlchemy integration with SQLite3",
    version="1.0.0"
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Check database health"""
    is_healthy = check_db_health()
    if not is_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable"
        )
    return {"status": "healthy", "database": "connected"}


# User endpoints
@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED, tags=["Users"])
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return crud.create_user(db=db, user=user)


@app.get("/users", response_model=List[User], tags=["Users"])
async def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all users with pagination"""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=User, tags=["Users"])
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@app.patch("/users/{user_id}", response_model=User, tags=["Users"])
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user"""
    db_user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user"""
    success = crud.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


# User Profile endpoints
@app.post("/users/{user_id}/profile", response_model=UserProfile, status_code=status.HTTP_201_CREATED, tags=["User Profiles"])
async def create_profile(user_id: int, profile: UserProfileCreate, db: Session = Depends(get_db)):
    """Create or update user profile"""
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db_profile = crud.create_user_profile(db=db, user_id=user_id, profile=profile)
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create profile"
        )
    return db_profile


@app.get("/users/{user_id}/profile", response_model=UserProfile, tags=["User Profiles"])
async def get_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile"""
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db_profile = crud.get_user_profile(db, user_id=user_id)
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return db_profile


@app.delete("/users/{user_id}/profile", status_code=status.HTTP_204_NO_CONTENT, tags=["User Profiles"])
async def delete_profile(user_id: int, db: Session = Depends(get_db)):
    """Delete user profile"""
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    success = crud.delete_user_profile(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)