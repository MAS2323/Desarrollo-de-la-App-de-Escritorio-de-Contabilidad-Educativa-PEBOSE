from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class Ingreso(Base):
    __tablename__ = "ingresos"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=True)  # Esta columna causa el error si falta
    concepto = Column(String(200), nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    categoria = Column(String(50), default='Matrícula')
    
    persona = relationship("Persona", back_populates="ingresos")
    last_sync = Column(DateTime, nullable=True)