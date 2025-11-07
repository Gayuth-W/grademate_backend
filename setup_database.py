#!/usr/bin/env python3
"""
Database setup script for GradeMate backend
Run this script to initialize your database with the required tables
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.config import settings
from app.database import init_database
from app import models

def setup_database():
    """Initialize the database with all required tables"""
    try:
        print("🚀 Setting up GradeMate database...")
        print(f"📊 Database URL: {settings.database_url}")
        
        # Initialize database
        init_database()
        
        print("✅ Database setup completed successfully!")
        print("\n📋 Created tables:")
        print("   - marking_schemes")
        print("   - answer_sheets") 
        print("   - grading_results")
        print("   - grading_sessions")
        
        print("\n🎉 Your database is ready for GradeMate!")
        
    except SQLAlchemyError as e:
        print(f"❌ Database setup failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Check your DATABASE_URL in environment variables")
        print("   2. Ensure your database server is running")
        print("   3. Verify your database credentials")
        print("   4. Make sure the database exists")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

def test_connection():
    """Test database connection"""
    try:
        print("🔍 Testing database connection...")
        engine = create_engine(settings.database_url)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🎓 GradeMate Database Setup")
    print("=" * 40)
    
    # Test connection first
    if not test_connection():
        print("\n❌ Cannot proceed without database connection")
        sys.exit(1)
    
    # Setup database
    setup_database()
