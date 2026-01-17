import requests
from datetime import datetime
from sqlalchemy.orm import Session
from models.ingreso import Ingreso  # Fix: Import específico desde ingreso.py
from models.gasto import Gasto  # Fix: Import específico desde gasto.py
from models.base import engine  # Para sync local
from utils.helpers import is_online
from utils.config import API_URL

def sincronizar_datos(db: Session):
    if not is_online():
        print("Sin conexión. Quedando en modo offline.")
        return False

    try:
        # Envía cambios no sincronizados (Ingresos pendientes)
        pendientes_ing = db.query(Ingreso).filter(Ingreso.last_sync == None).all()
        for ing in pendientes_ing:
            response = requests.post(f"{API_URL}/ingresos", json={
                'id': ing.id, 'concepto': ing.concepto, 'monto': ing.monto,
                'fecha': ing.fecha.isoformat(), 'categoria': ing.categoria, 'persona_id': ing.persona_id
            })
            if response.status_code == 200:
                ing.last_sync = datetime.utcnow()
        db.commit()

        # Envía cambios no sincronizados (Gastos pendientes)
        pendientes_gas = db.query(Gasto).filter(Gasto.last_sync == None).all()
        for gas in pendientes_gas:
            response = requests.post(f"{API_URL}/gastos", json={
                'id': gas.id, 'concepto': gas.concepto, 'monto': gas.monto,
                'fecha': gas.fecha.isoformat(), 'categoria': gas.categoria, 'persona_id': gas.persona_id
            })
            if response.status_code == 200:
                gas.last_sync = datetime.utcnow()
        db.commit()

        # Recibe cambios de cloud (GET)
        response = requests.get(f"{API_URL}/sync")
        if response.status_code == 200:
            print("Datos sincronizados desde cloud.")

        print("Sincronización completada exitosamente.")
        return True
    except Exception as e:
        print(f"Error en sync: {e}")
        return False