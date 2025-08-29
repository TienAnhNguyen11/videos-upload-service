from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import User
from app.schemas.schemas import TokenData, Token
from app.services.user_service import UserService


class AuthService:
    """Service class for Authentication operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        return self.user_service.authenticate_user(username, password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify JWT token and return token data"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return TokenData(username=username)
        except JWTError:
            return None
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token"""
        token_data = self.verify_token(token)
        if token_data is None:
            return None
        
        user = self.user_service.get_by_username(token_data.username)
        return user
    
    def login(self, username: str, password: str) -> Optional[Token]:
        """Login user and return access token"""
        user = self.authenticate_user(username, password)
        if not user:
            return None
        
        access_token_expires = timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        access_token = self.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")
    
    def register(self, username: str, email: str, password: str) -> Optional[User]:
        """Register new user"""
        from app.schemas.schemas import UserCreate
        
        # Check if username or email already exists
        if self.user_service.is_username_taken(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        if self.user_service.is_email_taken(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user data
        user_data = UserCreate(username=username, email=email, password=password)
        
        # Validate user data
        if not self.user_service.validate_data(user_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user data"
            )
        
        # Create user
        return self.user_service.create_user(user_data)
    
    def refresh_token(self, token: str) -> Optional[Token]:
        """Refresh access token"""
        token_data = self.verify_token(token)
        if token_data is None:
            return None
        
        user = self.user_service.get_by_username(token_data.username)
        if user is None:
            return None
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")
    
    def validate_token_format(self, token: str) -> bool:
        """Validate token format"""
        if not token or not token.startswith("Bearer "):
            return False
        return True
    
    def extract_token(self, authorization: str) -> str:
        """Extract token from Authorization header"""
        if not self.validate_token_format(authorization):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return authorization.split(" ")[1]
