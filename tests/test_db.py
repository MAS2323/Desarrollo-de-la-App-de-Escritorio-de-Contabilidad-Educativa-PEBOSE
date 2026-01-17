from sqlalchemy.orm import Session
from src.models.base import SessionLocal, create_ingreso  # Ajusta imports

def test_create_ingreso():
    db = next(SessionLocal())
    create_ingreso(db, "Test", 1000)
    assert True  # Expande con asserts reales
    db.close()

if __name__ == "__main__":
    test_create_ingreso()