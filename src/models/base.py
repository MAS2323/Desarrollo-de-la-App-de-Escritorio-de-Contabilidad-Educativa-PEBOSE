from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
import enum

Base = declarative_base()

class NivelEducativo(enum.Enum):
    GUARDERIA_INFANTES = "Guardería de Infantes"
    PREESCOLAR = "Preescolar"
    PRIMARIA = "Primaria"
    SECUNDARIA = "Secundaria"
    FORMACION_PROFESIONAL = "Formación Profesional"

class Persona(Base):
    __tablename__ = 'personas'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'Estudiante' o 'Profesor'
    nivel_educativo = Column(Enum(NivelEducativo), nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    # Relaciones backref
    ingresos = relationship("Ingreso", back_populates="persona")
    gastos = relationship("Gasto", back_populates="persona")

class Ingreso(Base):
    __tablename__ = 'ingresos'
    id = Column(Integer, primary_key=True)
    descripcion = Column(String(200), nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    categoria = Column(String(50), default='Matrícula')
    persona_id = Column(Integer, ForeignKey('personas.id'), nullable=True)
    persona = relationship("Persona", back_populates="ingresos")
    last_sync = Column(DateTime, nullable=True)

class Gasto(Base):
    __tablename__ = 'gastos'
    id = Column(Integer, primary_key=True)
    descripcion = Column(String(200), nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    categoria = Column(String(50), default='Salarios')
    persona_id = Column(Integer, ForeignKey('personas.id'), nullable=True)
    persona = relationship("Persona", back_populates="gastos")
    last_sync = Column(DateTime, nullable=True)

# Path DB
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../db_local.sqlite'))
engine = create_engine(f'sqlite:///{db_path}', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()