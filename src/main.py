import sys
import os
sys.path.insert(0, os.path.abspath('..'))  # Para imports relativos desde src/

import flet as ft
from views.main_view import MainView  # Importa la clase, no la función

def main(page: ft.Page):
    app = MainView(page)  # Instancia la clase
    app.build()  # Llama al método build

if __name__ == "__main__":
    ft.app(target=main)