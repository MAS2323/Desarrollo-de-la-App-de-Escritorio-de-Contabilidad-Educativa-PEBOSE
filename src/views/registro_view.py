import flet as ft
from students_teachers.persona_service import create_persona, get_personas, update_persona, delete_persona, NivelEducativo
from sqlalchemy.orm import Session

class RegistroView:
    def __init__(self, page: ft.Page, db: Session):
        self.page = page
        self.db = db
        self.page_view = ft.View("/registro", controls=[])

    def build(self):
        titulo = ft.Text("Registro de Personas - PEBOSE", size=20, weight=ft.FontWeight.BOLD)

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
                self.page.snack_bar = ft.SnackBar(ft.Text("Completa todos los campos"), bgcolor=ft.colors.RED)
                self.page.snack_bar.open = True
                self.page.update()
                return
            create_persona(self.db, nombre_field.value, apellidos_field.value, tipo_dropdown.value, nivel_dropdown.value)
            self.page.snack_bar = ft.SnackBar(ft.Text("Persona registrada"), bgcolor=ft.colors.GREEN)
            self.page.snack_bar.open = True
            self.page.update()
            nombre_field.value = apellidos_field.value = ""
            tipo_dropdown.value = nivel_dropdown.value = None
            cargar_personas(None)

        btn_agregar = ft.ElevatedButton("Registrar Persona", on_click=agregar_persona)

        tabla_personas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Apellidos")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Nivel Educativo")),
                ft.DataColumn(ft.Text("Acciones"))
            ],
            rows=[]  # Fix: Sin horizontal_scrollbar
        )

        def cargar_personas(e):
            personas = get_personas(self.db)
            tabla_personas.rows.clear()
            for p in personas:
                btn_edit = ft.IconButton(ft.icons.EDIT, on_click=lambda _, pid=p.id: self.edit_persona(pid))
                btn_delete = ft.IconButton(ft.icons.DELETE, on_click=lambda _, pid=p.id: self.delete_persona(pid))
                tabla_personas.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(p.id))),
                    ft.DataCell(ft.Text(p.nombre)),
                    ft.DataCell(ft.Text(p.apellidos)),
                    ft.DataCell(ft.Text(p.tipo)),
                    ft.DataCell(ft.Text(p.nivel_educativo.value)),
                    ft.DataCell(ft.Row([btn_edit, btn_delete]))
                ]))
            self.page.update()

        def edit_persona(self, id):
            p = self.db.query(Persona).filter(Persona.id == id).first()
            if p:
                nombre_edit = ft.TextField(value=p.nombre)
                apellidos_edit = ft.TextField(value=p.apellidos)
                tipo_edit = ft.Dropdown(value=p.tipo, options=[ft.dropdown.Option("Estudiante"), ft.dropdown.Option("Profesor"), ft.dropdown.Option("Empleado")])
                nivel_edit = ft.Dropdown(value=p.nivel_educativo.value, options=[ft.dropdown.Option(n.value) for n in NivelEducativo])
                dialog = ft.AlertDialog(
                    title=ft.Text("Editar Persona"),
                    content=ft.Column([nombre_edit, apellidos_edit, tipo_edit, nivel_edit], scroll=ft.ScrollMode.AUTO),
                    actions=[ft.ElevatedButton("Guardar", on_click=lambda e: self.save_edit_persona(id, nombre_edit.value, apellidos_edit.value, tipo_edit.value, nivel_edit.value)), ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog))]
                )
                self.page.open(dialog)

        def save_edit_persona(self, id, nombre, apellidos, tipo, nivel):
            update_persona(self.db, id, nombre, apellidos, tipo, nivel)
            self.page.close(self.page.dialog)
            self.page.snack_bar = ft.SnackBar(ft.Text("Persona actualizada"), bgcolor=ft.colors.GREEN)
            self.page.snack_bar.open = True
            self.page.update()
            cargar_personas(None)

        def delete_persona(self, id):
            dialog = ft.AlertDialog(
                title=ft.Text("Confirmar"),
                content=ft.Text("¿Eliminar esta persona? (Afectará registros vinculados)"),
                actions=[ft.ElevatedButton("Sí", on_click=lambda e: self.confirm_delete_persona(id)), ft.TextButton("No", on_click=lambda e: self.page.close(dialog))]
            )
            self.page.open(dialog)

        def confirm_delete_persona(self, id):
            delete_persona(self.db, id)
            self.page.close(self.page.dialog)
            self.page.snack_bar = ft.SnackBar(ft.Text("Persona eliminada"), bgcolor=ft.colors.ORANGE)
            self.page.snack_bar.open = True
            self.page.update()
            cargar_personas(None)

        layout_column = ft.Column(
            [
                titulo,
                ft.Divider(),
                ft.Text("Formulario de Registro:", size=16),
                ft.Row([nombre_field, apellidos_field]),
                ft.Row([tipo_dropdown, nivel_dropdown]),
                btn_agregar,
                ft.Divider(),
                ft.Text("Personas Registradas:", size=16),
                tabla_personas,
                ft.Divider(),
                ft.ElevatedButton("Volver al Home", on_click=lambda _: self.page.go("/home"))
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=20
        )
        self.page_view.controls = [layout_column]
        self.page_view.scroll = ft.ScrollMode.AUTO

        cargar_personas(None)