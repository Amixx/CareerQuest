import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class JobListing(Base):
    __tablename__ = 'job_listings'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255))
    location = Column(String(255))
    salary_min = Column(Float)
    salary_max = Column(Float)
    description = Column(Text)
    requirements = Column(Text)
    responsibilities = Column(Text)
    benefits = Column(Text)
    deadline = Column(String(50))
    teamwork_preference = Column(Float)
    work_environment = Column(Float)
    learning_opportunity = Column(Float)
    company_size = Column(Float)
    remote_preference = Column(Float)
    career_growth = Column(Float)
    project_type = Column(Float)
    experience_required = Column(Float)
    stress_level = Column(Float)
    creativity_required = Column(Float)
    job_category = Column(String(100))
    url = Column(String(500), unique=True)
    scraped_at = Column(DateTime, default=datetime.datetime.now)

def init_db():
    """Initialize the database and create tables if they don't exist"""
    db_path = os.path.join(os.path.dirname(__file__), 'job_listings.db')
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """Create a session for database operations"""
    engine = init_db()
    Session = sessionmaker(bind=engine)
    return Session()
