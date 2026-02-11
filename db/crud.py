from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import models
from .schemas import UserCreate, UserUpdate, UserProfileCreate
import hashlib
import secrets


def hash_password(password: str) -> str:
    """Hash password using SHA256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${password_hash.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    try:
        salt, hashed = password_hash.split('$')
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() == hashed
    except:
        return False


# User CRUD operations
def create_user(db: Session, user: UserCreate) -> models.User:
    """Create a new user with profile"""
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        password_hash=hash_password(user.password),
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise


def get_user(db: Session, user_id: int) -> models.User | None:
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    """Get user by email"""
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    """Get all users with pagination"""
    return db.query(models.User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> models.User | None:
    """Update user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        return None


def delete_user(db: Session, user_id: int) -> bool:
    """Delete user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True


# UserProfile CRUD operations
def create_user_profile(
    db: Session, user_id: int, profile: UserProfileCreate
) -> models.UserProfile | None:
    """Create or update user profile"""
    db_profile = db.query(models.UserProfile).filter(
        models.UserProfile.user_id == user_id
    ).first()

    if db_profile:
        for field, value in profile.model_dump(exclude_unset=True).items():
            setattr(db_profile, field, value)
    else:
        db_profile = models.UserProfile(user_id=user_id, **profile.model_dump())

    db.add(db_profile)
    try:
        db.commit()
        db.refresh(db_profile)
        return db_profile
    except IntegrityError:
        db.rollback()
        return None


def get_user_profile(db: Session, user_id: int) -> models.UserProfile | None:
    """Get user profile by user ID"""
    return db.query(models.UserProfile).filter(
        models.UserProfile.user_id == user_id
    ).first()


def delete_user_profile(db: Session, user_id: int) -> bool:
    """Delete user profile"""
    db_profile = get_user_profile(db, user_id)
    if not db_profile:
        return False
    db.delete(db_profile)
    db.commit()
    return True