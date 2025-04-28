from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL connection configuration (XAMPP defaults)
DATABASE_URL = "mysql+pymysql://root:@localhost/rumourcheck"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(5000))
    is_fake = Column(Boolean)
    confidence_fake = Column(Float)
    confidence_true = Column(Float)
    created_at = Column(DateTime, server_default='CURRENT_TIMESTAMP')

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Call this function when your application starts
create_tables()