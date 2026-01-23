from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from enum import Enum
from typing import List
from models.persona import Persona, NivelEducativo  # Importa enum del model
from models.ingreso import Ingreso
from models.gasto import Gasto
from services.db_service import create_ingreso  # Fix: Import para pagos de prueba
from datetime import datetime

def create_persona(db: Session, nombre: str, apellidos: str, tipo: str, nivel: str):
    """Crea persona con validación de nivel educativo."""
    try:
        # Validación de nivel (usa enum del model sin acentos)
        if nivel not in [n.value for n in NivelEducativo]:
            raise ValueError(f"Nivel '{nivel}' no válido. Usa: {[n.value for n in NivelEducativo]}")
        nuevo = Persona(nombre=nombre, apellidos=apellidos, tipo=tipo, nivel_educativo=nivel)  # Pasa string directo
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
    except IntegrityError:
        db.rollback()
        raise ValueError("Persona ya existe o datos inválidos")

def get_personas(db: Session, skip: int = 0, limit: int = 10) -> List[Persona]:
    return db.query(Persona).order_by(Persona.apellidos).offset(skip).limit(limit).all()

def get_personas_filtro(db: Session, filtro: str = "") -> List[Persona]:
    query = db.query(Persona)
    if filtro:
        query = query.filter(
            Persona.nombre.contains(filtro) | Persona.apellidos.contains(filtro)
        )
    return query.all()

def update_persona(db: Session, persona_id: int, nombre: str = None, apellidos: str = None, tipo: str = None, nivel: str = None):
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if persona:
        if nombre: persona.nombre = nombre
        if apellidos: persona.apellidos = apellidos
        if tipo: persona.tipo = tipo
        if nivel:
            if nivel not in [n.value for n in NivelEducativo]:
                raise ValueError(f"Nivel '{nivel}' no válido")
            persona.nivel_educativo = nivel  # Pasa string directo
        db.commit()
        db.refresh(persona)
    return persona

def delete_persona(db: Session, persona_id: int):
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if persona:
        # Elimina ingresos/gastos vinculados (cascade)
        db.query(Ingreso).filter(Ingreso.persona_id == persona_id).delete()
        db.query(Gasto).filter(Gasto.persona_id == persona_id).delete()
        db.delete(persona)
        db.commit()
    return persona

def calcular_monto_pago(nivel: str, tipo_pago: str, opcion_mensual: str = None) -> float:
    """Calcula monto automático basado en nivel y tipo de pago para PEBOSE."""
    montos = {
        'Guarderia': {
            'Matricula': [75000, 100000, 130000],  # Opciones mensuales (sin acentos)
            'APA': 0,  # Asumiendo APA no aplica o ajusta
            'Uniforme regular': 0,
            'Uniforme de deporte': 0
        },
        'Prescolar': {
            'Matricula': 130000,  # Anual
            'APA': 0,
            'Uniforme regular': 20000,
            'Uniforme de deporte': 20000
        },
        'Primaria': {
            'Matricula': 120000,  # Anual
            'APA': 0,
            'Uniforme regular': 25000,
            'Uniforme de deporte': 25000
        },
        'Sexto Primaria': {
            'Matricula': 180000,  # Anual
            'APA': 0,
            'Uniforme regular': 25000,
            'Uniforme de deporte': 25000
        },
        'Esba': {
            'Matricula': 195000,  # Anual
            'APA': 0,
            'Uniforme regular': 45000,
            'Uniforme de deporte': 45000
        },
        'Bachillerato': {
            'Matricula': 195000,  # Anual (asumiendo igual a ESBA)
            'APA': 0,
            'Uniforme regular': 45000,
            'Uniforme de deporte': 45000
        }
    }
    if nivel in montos and tipo_pago in montos[nivel]:
        monto = montos[nivel][tipo_pago]
        if isinstance(monto, list) and opcion_mensual:  # Guarderia
            return monto[int(opcion_mensual) - 1]  # 1=75k, 2=100k, 3=130k
        return monto if monto > 0 else 0.0
    return 0.0  # Default si no coincide

def insertar_datos_prueba(db: Session):
    """Inserta datos de prueba reajustados para PEBOSE con nuevos niveles (sin acentos)."""
    if db.query(Persona).count() == 0:
        # Niveles reajustados: Guarderia, Prescolar, Primaria, Esba, Bachillerato
        niveles = ['Guarderia', 'Prescolar', 'Primaria', 'Esba', 'Bachillerato']
        tipos = ['Estudiante', 'Profesor']
        datos_prueba = [
            ("Juan", "López", tipos[0], niveles[0]),  # Guarderia
            ("María", "García", tipos[0], niveles[0]),  # Guarderia
            ("Pedro", "Martínez", tipos[0], niveles[1]),  # Prescolar
            ("Ana", "Rodríguez", tipos[0], niveles[1]),  # Prescolar
            ("Carlos", "Sánchez", tipos[0], niveles[2]),  # Primaria
            ("Luis", "Hernández", tipos[0], niveles[2]),  # Primaria
            ("Sofía", "González", tipos[0], niveles[3]),  # Esba
            ("Diego", "Pérez", tipos[0], niveles[3]),  # Esba
            ("Laura", "Ramírez", tipos[0], niveles[4]),  # Bachillerato
            ("Miguel", "Torres", tipos[1], niveles[2]),  # Profesor Primaria
        ]
        for nom, ape, tip, niv in datos_prueba:
            try:
                create_persona(db, nom, ape, tip, niv)
            except ValueError as ve:
                print(f"Error en datos de prueba: {ve}")
        
        # Pagos de prueba reajustados (sin acentos)
        personas = db.query(Persona).all()
        if personas:
            # Matrícula Guarderia (opción 1: 75k)
            create_ingreso(db, "Matricula Guarderia", 75000, "Matricula", personas[0].id)
            # Matrícula Prescolar
            create_ingreso(db, "Matricula Prescolar", 130000, "Matricula", personas[2].id)
            # Uniforme Primaria
            create_ingreso(db, "Uniforme Primaria", 25000, "Uniforme regular", personas[4].id)
            # Matrícula Esba
            create_ingreso(db, "Matricula Esba", 195000, "Matricula", personas[6].id)
            # APA Bachillerato (asumiendo 0 o ajusta)
            create_ingreso(db, "APA Bachillerato", 0, "APA", personas[8].id)
        
        db.commit()
        print("Datos de prueba insertados para PEBOSE.")