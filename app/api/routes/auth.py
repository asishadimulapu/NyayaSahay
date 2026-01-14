# Indian Law RAG Chatbot - Authentication Routes
"""
User authentication endpoints for registration and login.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.crud import UserCRUD
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.utils.auth import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        UserResponse: Created user profile
        
    Raises:
        HTTPException: 400 if email already registered
    """
    # Check if user already exists
    existing_user = UserCRUD.get_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = UserCRUD.create(db, user_data)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Token:
    """
    Authenticate user and return JWT token.
    
    Args:
        credentials: Login credentials (email + password)
        db: Database session
        
    Returns:
        Token: JWT access token
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Authenticate user
    user = UserCRUD.authenticate(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Create JWT token
    access_token = create_access_token(subject=user.id)
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    db: Session = Depends(get_db),
    user = Depends(lambda: None)  # Placeholder, will use proper dependency
) -> UserResponse:
    """
    Get current user's profile.
    Requires authentication.
    """
    from app.api.dependencies import get_current_user
    # This would need proper integration - placeholder for now
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint under development"
    )
