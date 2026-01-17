from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os  # Para path absoluto

Base = declarative_base()
engine = None
SessionLocal = None

def init_db():
    """Initialize database - call this ONCE from main.py after importing all models"""
    global engine, SessionLocal
    
    # Path absoluto para evitar problemas relativos
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../db_local.sqlite'))
    print(f"Path de DB: {db_path}")  # Debug: Verifica path
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    
    # Recreación forzada para desarrollo (borra y crea tablas)
    Base.metadata.drop_all(engine)  # Fix: Borra tablas existentes
    Base.metadata.create_all(engine)  # Crea con esquema nuevo (incluye persona_id)
    
    SessionLocal = sessionmaker(bind=engine)
    
    return SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()