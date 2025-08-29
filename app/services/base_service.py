from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import Generic, TypeVar, Type, Optional, List, Any
from app.core.database import Base

T = TypeVar('T', bound=Base)


class BaseService(Generic[T], ABC):
    """Base service class for all services"""
    
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination"""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, **kwargs) -> T:
        """Create new entity"""
        entity = self.model(**kwargs)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update entity by ID"""
        entity = self.get_by_id(id)
        if not entity:
            return None
        
        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def delete(self, id: int) -> bool:
        """Delete entity by ID"""
        entity = self.get_by_id(id)
        if entity:
            self.db.delete(entity)
            self.db.commit()
            return True
        return False
    
    @abstractmethod
    def validate_data(self, data: Any) -> bool:
        """Validate input data"""
        pass
