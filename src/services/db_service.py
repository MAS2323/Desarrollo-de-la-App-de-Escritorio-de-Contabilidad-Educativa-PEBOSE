from sqlalchemy.orm import Session
from models.ingreso import Ingreso
from models.gasto import Gasto
from typing import List

def create_ingreso(db: Session, concepto: str, monto: float, categoria: str = 'Matrícula', persona_id: int = None):
    nuevo = Ingreso(concepto=concepto, monto=monto, categoria=categoria, persona_id=persona_id)  # Fix: concepto en lugar de descripcion
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    nuevo.last_sync = None
    db.commit()
    return nuevo

def get_ingresos(db: Session, skip: int = 0, limit: int = 10) -> List[Ingreso]:
    return db.query(Ingreso).order_by(Ingreso.fecha.desc()).offset(skip).limit(limit).all()

def update_ingreso(db: Session, ingreso_id: int, concepto: str = None, monto: float = None, categoria: str = None, persona_id: int = None):
    ingreso = db.query(Ingreso).filter(Ingreso.id == ingreso_id).first()
    if ingreso:
        if concepto: ingreso.concepto = concepto  # Fix: concepto en lugar de descripcion
        if monto: ingreso.monto = monto
        if categoria: ingreso.categoria = categoria
        if persona_id: ingreso.persona_id = persona_id
        db.commit()
        db.refresh(ingreso)
    return ingreso

def delete_ingreso(db: Session, ingreso_id: int):
    ingreso = db.query(Ingreso).filter(Ingreso.id == ingreso_id).first()
    if ingreso:
        db.delete(ingreso)
        db.commit()
    return ingreso

def create_gasto(db: Session, concepto: str, monto: float, categoria: str = 'Salarios', persona_id: int = None):
    nuevo = Gasto(concepto=concepto, monto=monto, categoria=categoria, persona_id=persona_id)  # Fix: concepto en lugar de descripcion
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    nuevo.last_sync = None
    db.commit()
    return nuevo

def get_gastos(db: Session, skip: int = 0, limit: int = 10) -> List[Gasto]:
    return db.query(Gasto).order_by(Gasto.fecha.desc()).offset(skip).limit(limit).all()

def update_gasto(db: Session, gasto_id: int, concepto: str = None, monto: float = None, categoria: str = None, persona_id: int = None):
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()
    if gasto:
        if concepto: gasto.concepto = concepto  # Fix: concepto en lugar de descripcion
        if monto: gasto.monto = monto
        if categoria: gasto.categoria = categoria
        if persona_id: gasto.persona_id = persona_id
        db.commit()
        db.refresh(gasto)
    return gasto

def delete_gasto(db: Session, gasto_id: int):
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()
    if gasto:
        db.delete(gasto)
        db.commit()
    return gasto