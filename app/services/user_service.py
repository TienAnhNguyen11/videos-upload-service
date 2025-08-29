from sqlalchemy.orm import Session
from app.models.models import User
from app.schemas.schemas import UserCreate
from app.services.base_service import BaseService
from app.utils.password import get_password_hash, verify_password
from typing import Optional


class UserService(BaseService[User]):
    """Service class for User operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, User)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create new user with hashed password"""
        hashed_password = get_password_hash(user_data.password)
        return self.create(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = self.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def validate_data(self, data: UserCreate) -> bool:
        """Validate user data"""
        if not data.username or len(data.username) < 3:
            return False
        if not data.email or '@' not in data.email:
            return False
        if not data.password or len(data.password) < 6:
            return False
        return True
    
    def is_username_taken(self, username: str) -> bool:
        """Check if username is already taken"""
        return self.get_by_username(username) is not None
    
    def is_email_taken(self, email: str) -> bool:
        """Check if email is already taken"""
        return self.get_by_email(email) is not None
