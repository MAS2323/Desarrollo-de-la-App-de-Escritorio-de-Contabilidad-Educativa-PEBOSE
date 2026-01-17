import flet as ft
from services.persona_service import create_persona, get_personas, update_persona, delete_persona, NivelEducativo
from sqlalchemy.orm import Session
from models.persona import Persona

class RegistroView:
    def __init__(self, page: ft.Page, db: Session):
        self.page = page
        self.db = db
        self.page_view = ft.View("/registro", controls=[])  # Fix: Crea page_view en __init__

    def build(self):
        self.tabla_personas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Apellidos")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Nivel Educativo")),
                ft.DataColumn(ft.Text("Acciones"))
            ],
            rows=[]
        )

        # Formulario
        nombre_field = ft.TextField(label="Nombre")
        apellidos_field = ft.TextField(label="Apellidos")
        tipo_dropdown = ft.Dropdown(
            label="Tipo",
            options=[ft.dropdown.Option("Estudiante"), ft.dropdown.Option("Profesor"), ft.dropdown.Option("Empleado")],
            width=200
        )
        nivel_dropdown = ft.Dropdown(
            label="Nivel Educativo",
            options=[ft.dropdown.Option(n.value) for n in NivelEducativo],
            width=250
        )

        def agregar_persona(e):
            if not all([nombre_field.value, apellidos_field.value, tipo_dropdown.value, nivel_dropdown.value]):
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Completa todos los campos"), bgcolor=ft.colors.RED))
                return
            create_persona(self.db, nombre_field.value, apellidos_field.value, tipo_dropdown.value, nivel_dropdown.value)
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Persona registrada"), bgcolor=ft.colors.GREEN))
            nombre_field.value = apellidos_field.value = ""
            tipo_dropdown.value = nivel_dropdown.value = None
            self.cargar_personas()

        btn_agregar = ft.ElevatedButton("Registrar Persona", on_click=agregar_persona)
        
        # Cargar datos iniciales
        self.cargar_personas()

        # Layout completo
        layout = ft.Column(
            [
                ft.Text("Registro de Personas - PEBOSE", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("Formulario de Registro:", size=16),
                ft.Row([nombre_field, apellidos_field]),
                ft.Row([tipo_dropdown, nivel_dropdown]),
                btn_agregar,
                ft.Divider(),
                ft.Text("Personas Registradas:", size=16),
                self.tabla_personas,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=20
        )

        # Asigna a page_view.controls (Fix AttributeError)
        self.page_view.controls = [layout]
        self.page_view.scroll = ft.ScrollMode.AUTO

    def cargar_personas(self):
        personas = get_personas(self.db)
        self.tabla_personas.rows.clear()
        for p in personas:
            btn_edit = ft.IconButton(ft.icons.EDIT, on_click=lambda e, pid=p.id: self.edit_persona(pid))
            btn_delete = ft.IconButton(ft.icons.DELETE, on_click=lambda e, pid=p.id: self.delete_persona(pid))
            self.tabla_personas.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(p.id))),
                ft.DataCell(ft.Text(p.nombre)),
                ft.DataCell(ft.Text(p.apellidos)),
                ft.DataCell(ft.Text(p.tipo)),
                ft.DataCell(ft.Text(p.nivel_educativo.value)),
                ft.DataCell(ft.Row([btn_edit, btn_delete]))
            ]))
        self.page.update()

    def edit_persona(self, pid):
        p = self.db.query(Persona).filter(Persona.id == pid).first()
        if p:
            nombre_edit = ft.TextField(value=p.nombre)
            apellidos_edit = ft.TextField(value=p.apellidos)
            tipo_edit = ft.Dropdown(value=p.tipo, options=[ft.dropdown.Option("Estudiante"), ft.dropdown.Option("Profesor"), ft.dropdown.Option("Empleado")])
            nivel_edit = ft.Dropdown(value=p.nivel_educativo.value, options=[ft.dropdown.Option(n.value) for n in NivelEducativo])
            
            def guardar(e):
                update_persona(self.db, pid, nombre_edit.value, apellidos_edit.value, tipo_edit.value, nivel_edit.value)
                self.page.close(dialog)
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Persona actualizada"), bgcolor=ft.colors.GREEN))
                self.cargar_personas()
            
            dialog = ft.AlertDialog(
                title=ft.Text("Editar Persona"),
                content=ft.Column([nombre_edit, apellidos_edit, tipo_edit, nivel_edit], scroll=ft.ScrollMode.AUTO),
                actions=[ft.ElevatedButton("Guardar", on_click=guardar), ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog))]
            )
            self.page.open(dialog)

    def delete_persona(self, pid):
        def confirmar(e):
            delete_persona(self.db, pid)
            self.page.close(dialog)
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Persona eliminada"), bgcolor=ft.colors.ORANGE))
            self.cargar_personas()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar"),
            content=ft.Text("¿Eliminar esta persona? (Afectará registros vinculados)"),
            actions=[ft.ElevatedButton("Sí", on_click=confirmar), ft.TextButton("No", on_click=lambda e: self.page.close(dialog))]
        )
        self.page.open(dialog)