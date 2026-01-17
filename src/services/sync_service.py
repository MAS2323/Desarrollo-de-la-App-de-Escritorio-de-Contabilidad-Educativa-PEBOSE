import requests
from datetime import datetime
from sqlalchemy.orm import Session
from models.base import Ingreso, Gasto
from utils.helpers import is_online
from utils.config import API_URL

def sincronizar_datos(db: Session):
    if not is_online():
        print("Sin conexión. Quedando en modo offline.")
        return False

    try:
        # Envía cambios no sincronizados (ej. Ingresos pendientes)
        pendientes_ing = db.query(Ingreso).filter(Ingreso.last_sync == None).all()
        for ing in pendientes_ing:
            # Simula POST a cloud (reemplaza con tu API real)
            response = requests.post(f"{API_URL}/ingresos", json={
                'id': ing.id, 'descripcion': ing.descripcion, 'monto': ing.monto,
                'fecha': ing.fecha.isoformat(), 'categoria': ing.categoria
            })
            if response.status_code == 200:
                ing.last_sync = datetime.utcnow()
        db.commit()

        # Similar para GET (recibe cambios de cloud)
        response = requests.get(f"{API_URL}/sync")
        if response.status_code == 200:
            # Procesa datos recibidos (ej. merge simple)
            print("Datos sincronizados desde cloud.")

        print("Sincronización completada exitosamente.")
        return True
    except Exception as e:
        print(f"Error en sync: {e}")
        return False