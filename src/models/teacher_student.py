from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
from models.base import Base
import enum

class NivelEducativo(str, enum.Enum):
    PRIMARIA = "Primaria"
    SECUNDARIA = "Secundaria"
    UNIVERSIDAD = "Universidad"
    POSGRADO = "Posgrado"

class Persona(Base):
    __tablename__ = "personas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # Estudiante, Profesor, Empleado
    nivel_educativo = Column(SQLEnum(NivelEducativo))
    
    ingresos = relationship("Ingreso", back_populates="persona")
    gastos = relationship("Gasto", back_populates="persona")