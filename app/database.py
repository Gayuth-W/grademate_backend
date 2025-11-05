from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from .config import settings
from .models import Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.database_url,
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database with tables"""
    try:
        create_tables()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False
