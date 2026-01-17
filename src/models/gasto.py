from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class Gasto(Base):
    __tablename__ = "gastos"
    __table_args__ = {'extend_existing': True}  # Fix: Evita conflictos
    
    id = Column(Integer, primary_key=True, index=True)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=True)
    concepto = Column(String(200), nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    categoria = Column(String(50), default='Salarios')
    
    persona = relationship("Persona", back_populates="gastos")
    last_sync = Column(DateTime, nullable=True)