import flet as ft
from sqlalchemy.orm import Session  # Para tipado
from .ingreso_view import IngresoView
from .reporte_view import ReporteView
from .registro_view import RegistroView
from services.sync_service import sincronizar_datos

class MainView:
    def __init__(self, page: ft.Page, db: Session):  # Recibe db: Session binded
        self.page = page
        self.page.title = "PEBOSE Contabilidad"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.transition = None  # Desactiva transiciones
        self.page.window_bgcolor = ft.colors.TRANSPARENT  # Fix: Permite imagen de fondo
        self.db = db  # Usa db binded (Session con .query())
        self.current_view = None
        self.home_view = None

    def build(self):
        # Función para crear AppBar persistente
        def create_appbar(current_route):
            btn_home = ft.IconButton(ft.icons.HOME, on_click=lambda _: self.page.go("/home"), tooltip="Volver al Menú Principal")
            btn_sync = ft.IconButton(ft.icons.SYNC, on_click=lambda _: self.sync_click(), tooltip="Sincronizar Datos")
            title_text = "Home" if current_route == "/home" else "Ingresos/Gastos" if current_route == "/ingresos" else "Reportes" if current_route == "/reportes" else "Registro Personas" if current_route == "/registro" else "PEBOSE Contabilidad"

            return ft.AppBar(
                leading=btn_home,
                title=ft.Text(title_text, size=16, weight=ft.FontWeight.BOLD),
                center_title=True,
                bgcolor=ft.colors.BLUE_800,
                actions=[btn_sync]
            )

        # Pestañas comunes
        def create_tabs():
            def on_tab_change(e):
                if e.control.selected_index == 0:
                    self.page.go("/home")
                elif e.control.selected_index == 1:
                    self.page.go("/ingresos")
                elif e.control.selected_index == 2:
                    self.page.go("/reportes")
                elif e.control.selected_index == 3:
                    self.page.go("/registro")

            return ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(text="Home"),
                    ft.Tab(text="Ingresos/Gastos"),
                    ft.Tab(text="Reportes"),
                    ft.Tab(text="Registro Personas"),
                ],
                on_change=on_tab_change,
                expand=1
            )

        # Home content envuelto en Container con fondo de imagen
        home_column = ft.Column(
            [
                ft.Text("Bienvenido a la Contabilidad PEBOSE", size=40, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=ft.colors.BLUE_900),
                ft.Divider(),
                ft.Text("Selecciona una pestaña para navegar.", size=16, text_align=ft.TextAlign.CENTER),
                ft.Text("Fecha: 17/01/2026", size=12, color=ft.colors.GREY_700, text_align=ft.TextAlign.CENTER),
                ft.ElevatedButton("Sincronizar Datos", on_click=lambda _: self.sync_click())
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Container con imagen de fondo para home
        home_container = ft.Container(
            content=home_column,
            image_src="assets/background_pebose.jpg",  # Reemplaza con tu imagen
            image_fit=ft.ImageFit.COVER,  # Escala para cubrir
            image_repeat=ft.ImageRepeat.NO_REPEAT,
            gradient=ft.LinearGradient(  # Opacidad ligera para legibilidad
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.colors.with_opacity(0.7, ft.colors.WHITE), ft.colors.with_opacity(0.7, ft.colors.BLUE_50)]
            ),
            expand=True
        )

        self.home_view = ft.View(
            "/home",
            appbar=create_appbar("/home"),
            controls=[create_tabs(), home_container],
            vertical_alignment=ft.MainAxisAlignment.CENTER
        )

        # Función de cambio de route (aplica fondo a sub-vistas)
        def route_change(route):
            self.page.views.clear()
            appbar = create_appbar(route)
            tabs = create_tabs()

            if self.page.route == "/ingresos":
                self.current_view = IngresoView(self.page, self.db)
                self.current_view.build()
                self.current_view.page_view.appbar = appbar
                self.current_view.page_view.controls = [tabs] + self.current_view.page_view.controls
                # Agrega fondo a la vista
                self.current_view.page_view.bgcolor = ft.Image(
                    src="assets/background_pebose.jpg",
                    fit=ft.ImageFit.COVER,
                    repeat=ft.ImageRepeat.NO_REPEAT
                )
                self.page.views.append(self.current_view.page_view)
            elif self.page.route == "/reportes":
                self.current_view = ReporteView(self.page, self.db)
                self.current_view.build()
                self.current_view.page_view.appbar = appbar
                self.current_view.page_view.controls = [tabs] + self.current_view.page_view.controls
                self.current_view.page_view.bgcolor = ft.Image(
                    src="assets/background_pebose.jpg",
                    fit=ft.ImageFit.COVER,
                    repeat=ft.ImageRepeat.NO_REPEAT
                )
                self.page.views.append(self.current_view.page_view)
            elif self.page.route == "/registro":
                self.current_view = RegistroView(self.page, self.db)
                self.current_view.build()
                self.current_view.page_view.appbar = appbar
                self.current_view.page_view.controls = [tabs] + self.current_view.page_view.controls
                self.current_view.page_view.bgcolor = ft.Image(
                    src="assets/background_pebose.jpg",
                    fit=ft.ImageFit.COVER,
                    repeat=ft.ImageRepeat.NO_REPEAT
                )
                self.page.views.append(self.current_view.page_view)
            else:  # Home
                self.page.views.append(self.home_view)
            self.page.update()

        self.page.on_route_change = route_change
        self.page.route = "/home"
        route_change("/home")

    def sync_click(self):
        sincronizar_datos(self.db)
        self.page.snack_bar = ft.SnackBar(ft.Text("Datos sincronizados"), bgcolor=ft.colors.GREEN)
        self.page.snack_bar.open = True
        self.page.update()