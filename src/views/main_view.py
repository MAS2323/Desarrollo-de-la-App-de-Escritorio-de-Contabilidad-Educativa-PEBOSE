import flet as ft
from datetime import datetime
from sqlalchemy.orm import Session
from .ingreso_view import IngresoView
from .reporte_view import ReporteView
from .registro_view import RegistroView
from services.sync_service import sincronizar_datos


class MainView:
    def __init__(self, page: ft.Page, db: Session):
        self.page = page
        self.db = db
        self.page.title = "PEBOSE Contabilidad"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_bgcolor = ft.colors.TRANSPARENT

        # Inicializar vistas internas
        self.ingreso_view = IngresoView(page, db)
        self.reporte_view = ReporteView(page, db)
        self.registro_view = RegistroView(page, db)

        # Contenedor principal que cambiará según la pestaña/ruta
        self.body_container = ft.Container(expand=True, alignment=ft.alignment.top_center)

        # Construir la interfaz
        self.build()

    def build(self):
        # AppBar fija
        self.appbar = ft.AppBar(
            leading=ft.IconButton(
                ft.icons.HOME,
                on_click=lambda _: self.navigate_to("/home"),
                tooltip="Volver al Menú Principal"
            ),
            title=ft.Text("PEBOSE Contabilidad", size=16, weight=ft.FontWeight.BOLD),
            center_title=True,
            bgcolor=ft.colors.BLUE_800,
            actions=[
                ft.IconButton(
                    ft.icons.SYNC,
                    on_click=lambda _: self.sync_click(),
                    tooltip="Sincronizar Datos"
                )
            ]
        )

        # Tabs fijas - REPORTES MOVIDO A LA ÚLTIMA POSICIÓN
        self.tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Home"),
                ft.Tab(text="Ingresos/Gastos"),
                ft.Tab(text="Registro Personas"),
                ft.Tab(text="Reportes"),
            ],
            on_change=self.on_tab_change,
            expand=False
        )

        # Vista Home
        home_content = ft.Column(
            [
                ft.Text("Bienvenido a la Contabilidad PEBOSE", size=40, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=ft.colors.BLUE_900),
                ft.Divider(),
                ft.Text("Selecciona una pestaña para navegar.", size=16, text_align=ft.TextAlign.CENTER),
                ft.Text(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", size=12, color=ft.colors.GREY_700, text_align=ft.TextAlign.CENTER),
                ft.ElevatedButton("Sincronizar Datos", on_click=lambda _: self.sync_click())
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )

        home_container = ft.Container(
            content=home_content,
            image_src="assets/background_pebose.jpg",
            image_fit=ft.ImageFit.COVER,
            image_repeat=ft.ImageRepeat.NO_REPEAT,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[
                    ft.colors.with_opacity(0.7, ft.colors.WHITE),
                    ft.colors.with_opacity(0.7, ft.colors.BLUE_50)
                ]
            ),
            expand=True
        )

        self.home_view = home_container

        # Layout principal: AppBar + Tabs + Contenido dinámico
        main_layout = ft.Column(
            controls=[
                self.tabs,
                self.body_container
            ],
            expand=True
        )

        # Vista única
        self.page_view = ft.View(
            route="/",
            appbar=self.appbar,
            controls=[main_layout],
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH
        )

        # Configurar página
        self.page.views.clear()
        self.page.views.append(self.page_view)
        self.page.on_route_change = self.route_change
        self.page.go("/home")  # Inicia en home

    def on_tab_change(self, e):
        """Maneja el cambio de pestaña"""
        index = e.control.selected_index
        routes = ["/home", "/ingresos", "/registro", "/reportes"]
        if index < len(routes):
            self.page.go(routes[index])

    def navigate_to(self, route: str):
        """Navega a una ruta sin depender del evento"""
        self.page.go(route)

    def route_change(self, e: ft.RouteChangeEvent):
        """Actualiza el contenido según la ruta"""
        route = e.route
        self.update_appbar_title(route)
        self.update_tab_selection(route)
        self.update_body_content(route)

    def update_appbar_title(self, route: str):
        titles = {
            "/home": "Home",
            "/ingresos": "Ingresos/Gastos",
            "/registro": "Registro Personas",
            "/reportes": "Reportes"
        }
        self.appbar.title = ft.Text(
            titles.get(route, "PEBOSE Contabilidad"),
            size=16,
            weight=ft.FontWeight.BOLD
        )

    def update_tab_selection(self, route: str):
        route_to_index = {
            "/home": 0,
            "/ingresos": 1,
            "/registro": 2,
            "/reportes": 3
        }
        index = route_to_index.get(route, 0)
        self.tabs.selected_index = index

    def update_body_content(self, route: str):
        if route == "/home":
            self.body_container.content = self.home_view
        elif route == "/ingresos":
            # Asegurarse de que el contenido de ingreso esté construido
            if not self.ingreso_view.page_view.controls:
                self.ingreso_view.build()
            self.body_container.content = self.ingreso_view.page_view.controls[0]
        elif route == "/registro":
            if not self.registro_view.page_view.controls:
                self.registro_view.build()
            self.body_container.content = self.registro_view.page_view.controls[0]
        elif route == "/reportes":
            if not self.reporte_view.page_view.controls:
                self.reporte_view.build()
            self.body_container.content = self.reporte_view.page_view.controls[0]
        else:
            self.body_container.content = self.home_view

        self.page.update()

    def sync_click(self):
        sincronizar_datos(self.db)
        self.page.snack_bar = ft.SnackBar(
            ft.Text("Datos sincronizados"),
            bgcolor=ft.colors.GREEN
        )
        self.page.snack_bar.open = True
        self.page.update()