from sqlalchemy import Column, Integer, String, Enum as SQLEnum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime
import enum

class NivelEducativo(str, enum.Enum):
    """Enum reajustado sin acentos para PEBOSE (compatibilidad DB)."""
    GUARDERIA = "Guarderia"
    PREScolar = "Prescolar"
    PRIMARIA = "Primaria"
    SEXTO_PRIMARIA = "Sexto Primaria"
    ESBA = "Esba"
    BACHILLERATO = "Bachillerato"

class Persona(Base):
    __tablename__ = "personas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'Estudiante', 'Profesor', 'Empleado'
    nivel_educativo = Column(SQLEnum(NivelEducativo), nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones bidireccionales
    ingresos = relationship("Ingreso", back_populates="persona")
    gastos = relationship("Gasto", back_populates="persona")