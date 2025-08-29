#!/usr/bin/env python3
"""
Database initialization script
Creates tables and optionally creates an admin user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.models.models import Base
from app.services.user_service import UserService
from app.schemas.schemas import UserCreate


def init_database():
    """Initialize database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def create_admin_user():
    """Create admin user if it doesn't exist"""
    db = SessionLocal()
    try:
        user_service = UserService(db)
        
        # Check if admin user already exists
        admin_user = user_service.get_by_username("admin")
        if admin_user:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin_data = UserCreate(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        
        if user_service.validate_data(admin_data):
            admin_user = user_service.create_user(admin_data)
            print(f"Admin user created successfully: {admin_user.username}")
        else:
            print("Invalid admin user data!")
            
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()


def main():
    """Main function"""
    print("Initializing Video Upload Service Database...")
    
    # Initialize database tables
    init_database()
    
    # Create admin user
    create_admin_user()
    
    print("Database initialization completed!")


if __name__ == "__main__":
    main()
