from sqlalchemy import Column, Integer, String, Enum as SQLEnum, ForeignKey, DateTime  # Fix: Import DateTime
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime  # Fix: Import datetime para utcnow
import enum

class NivelEducativo(str, enum.Enum):
    GUARDERIA_INFANTES = "Guardería de Infantes"
    PREESCOLAR = "Preescolar"
    PRIMARIA = "Primaria"
    SECUNDARIA = "Secundaria"
    FORMACION_PROFESIONAL = "Formación Profesional"
    UNIVERSIDAD = "Universidad"
    POSGRADO = "Posgrado"

class Persona(Base):
    __tablename__ = "personas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'Estudiante', 'Profesor', 'Empleado'
    nivel_educativo = Column(SQLEnum(NivelEducativo), nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)  # Fix: Ahora DateTime y datetime importados
    
    # Relaciones bidireccionales
    ingresos = relationship("Ingreso", back_populates="persona")
    gastos = relationship("Gasto", back_populates="persona")