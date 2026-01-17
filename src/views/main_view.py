import flet as ft
from services.sync_service import sincronizar_datos
from sqlalchemy.orm import Session
from models.base import SessionLocal
from .ingreso_view import IngresoView
from .reporte_view import ReporteView
from .registro_view import RegistroView

class MainView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "PEBOSE Contabilidad"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = ft.colors.BLUE_50
        self.db = SessionLocal()
        self.current_view = None
        self.home_view = None

    def build(self):
        # Logo y título para home
        logo = ft.Image(src="../assets/logo_pebose.png", width=80, height=80)
        titulo = ft.Text("Colegio Privado PEBOSE - Gestión Financiera", size=24, weight=ft.FontWeight.BOLD)

        # Botón sync
        def sync_click(e):
            sincronizar_datos(self.db)
            self.page.snack_bar = ft.SnackBar(ft.Text("Sync ejecutado"), bgcolor=ft.colors.GREEN)
            self.page.snack_bar.open = True
            self.page.update()

        btn_sync = ft.ElevatedButton("Sincronizar Datos", on_click=sync_click)

        # Home view: Envuelve Column en lista para controls, con scroll
        home_column = ft.Column(
            [
                ft.Row([logo, titulo], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                ft.Text("Bienvenido a la Contabilidad PEBOSE", size=16),
                ft.ElevatedButton("Ir a Ingresos/Gastos", on_click=lambda _: self.page.go("/ingresos")),
                ft.ElevatedButton("Ir a Reportes", on_click=lambda _: self.page.go("/reportes")),
                ft.ElevatedButton("Registro de Personas", on_click=lambda _: self.page.go("/registro")),
                btn_sync,
                ft.Text("Fecha: 17/01/2026", size=12, color=ft.colors.GREY_700)
            ],
            scroll=ft.ScrollMode.AUTO,  # Scroll automático en home
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.home_view = ft.View(
            "/home",
            controls=[home_column],  # Fix: Lista con Column!
            vertical_alignment=ft.MainAxisAlignment.CENTER
        )

        # Función de cambio de ruta (con scroll en sub-vistas)
        def route_change(route):
            self.page.views.clear()
            if self.page.route == "/ingresos":
                self.current_view = IngresoView(self.page, self.db)
                self.current_view.build()
                self.current_view.page_view.scroll = ft.ScrollMode.AUTO
                self.page.views.append(self.current_view.page_view)
            elif self.page.route == "/reportes":
                self.current_view = ReporteView(self.page, self.db)
                self.current_view.build()
                self.current_view.page_view.scroll = ft.ScrollMode.AUTO
                self.page.views.append(self.current_view.page_view)
            elif self.page.route == "/registro":
                self.current_view = RegistroView(self.page, self.db)
                self.current_view.build()
                self.current_view.page_view.scroll = ft.ScrollMode.AUTO
                self.page.views.append(self.current_view.page_view)
            else:  # Default: /home
                self.page.views.append(self.home_view)
                self.page.snack_bar = ft.SnackBar(ft.Text("Navegando a Home"), bgcolor=ft.colors.BLUE)
                self.page.snack_bar.open = True
            self.page.update()

        self.page.on_route_change = route_change
        self.page.route = "/home"
        route_change("/home")