import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import flet as ft
from sqlalchemy.orm import sessionmaker  # Para tipado

# Importa TODOS los modelos ANTES de init_db para registrar tablas
from models.base import init_db
from models.persona import Persona, NivelEducativo
from models.ingreso import Ingreso
from models.gasto import Gasto

from views.main_view import MainView

def main(page: ft.Page):
    # Inicializa DB y obtiene sessionmaker
    sessionmaker = init_db()
    
    # Crea una Session binded (Fix UnboundExecutionError)
    db = sessionmaker()
    
    app = MainView(page, db)  # Pasa db: Session binded
    app.build()

if __name__ == "__main__":
    ft.app(target=main)