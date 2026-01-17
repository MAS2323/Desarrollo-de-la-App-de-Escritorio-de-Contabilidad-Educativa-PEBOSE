from sqlalchemy.orm import Session
from models.base import Persona, NivelEducativo
from typing import List

def create_persona(db: Session, nombre: str, apellidos: str, tipo: str, nivel: str):
    nuevo = Persona(nombre=nombre, apellidos=apellidos, tipo=tipo, nivel_educativo=NivelEducativo(nivel))
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def get_personas(db: Session, tipo: str = None, nivel: str = None, skip: int = 0, limit: int = 50) -> List[Persona]:
    query = db.query(Persona)
    if tipo:
        query = query.filter(Persona.tipo == tipo)
    if nivel:
        query = query.filter(Persona.nivel_educativo == NivelEducativo(nivel))
    return query.order_by(Persona.apellidos).offset(skip).limit(limit).all()

def get_personas_filtro(db: Session, filtro: str = "") -> List[Persona]:
    return db.query(Persona).filter(
        Persona.nombre.ilike(f"%{filtro}%") | Persona.apellidos.ilike(f"%{filtro}%")
    ).all()

def update_persona(db: Session, persona_id: int, nombre: str = None, apellidos: str = None, tipo: str = None, nivel: str = None):
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if persona:
        if nombre: persona.nombre = nombre
        if apellidos: persona.apellidos = apellidos
        if tipo: persona.tipo = tipo
        if nivel: persona.nivel_educativo = NivelEducativo(nivel)
        db.commit()
        db.refresh(persona)
    return persona

def delete_persona(db: Session, persona_id: int):
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if persona:
        db.delete(persona)
        db.commit()
    return persona

# Datos de prueba
def insertar_datos_prueba(db: Session):
    if db.query(Persona).count() == 0:
        pruebas = [
            ("Juan", "Pérez García", "Estudiante", "Primaria"),
            ("María", "López Nguema", "Estudiante", "Secundaria"),
            ("Ana", "Mba Obiang", "Estudiante", "Guardería de Infantes"),
            ("Pedro", "Sánchez Malabo", "Profesor", "Formación Profesional"),
            ("Luis", "Fernández Elo", "Profesor", "Preescolar")
        ]
        for nom, ape, tip, niv in pruebas:
            create_persona(db, nom, ape, tip, niv)
        print("Datos de prueba insertados para PEBOSE.")