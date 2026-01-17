import flet as ft
from services.db_service import create_ingreso, get_ingresos, create_gasto, get_gastos, update_ingreso, delete_ingreso, update_gasto, delete_gasto
from services.persona_service import get_personas_filtro, insertar_datos_prueba, NivelEducativo
from sqlalchemy.orm import Session
from models.persona import Persona
from models.ingreso import Ingreso
from models.gasto import Gasto

class IngresoView:
    def __init__(self, page: ft.Page, db: Session):
        self.page = page
        self.db = db
        self.page_view = ft.View("/ingresos", controls=[])  # Fix: Crea page_view en __init__
        self.tabla_ingresos = None
        self.tabla_gastos = None
        self.dropdown_persona = None
        self.filtro_persona = None
        insertar_datos_prueba(self.db)
    
    def cargar_personas_dropdown(self, e):
        filtro = self.filtro_persona.value or ""
        personas = get_personas_filtro(self.db, filtro)
        self.dropdown_persona.options = [
            ft.dropdown.Option(str(p.id), f"{p.nombre} {p.apellidos} ({p.tipo} - {p.nivel_educativo.value})")
            for p in personas
        ]
        self.page.update()

    def build(self):
        # Controles de filtro
        self.filtro_persona = ft.TextField(
            label="Filtrar por Nombre/Apellidos", 
            on_change=self.cargar_personas_dropdown
        )
        self.dropdown_persona = ft.Dropdown(
            label="Seleccionar Persona",
            options=[],
            width=300
        )
        self.cargar_personas_dropdown(None)

        # Formularios de ingresos
        desc_ing = ft.TextField(label="Descripción (ej. Matrícula Enero)")
        monto_ing = ft.TextField(label="Monto", keyboard_type=ft.KeyboardType.NUMBER)
        cat_educativa_ing = ft.Dropdown(
            options=[ft.dropdown.Option(n.value) for n in NivelEducativo],
            label="Categoría Educativa (Ingreso)"
        )

        # Formularios de gastos
        desc_gas = ft.TextField(label="Descripción (ej. Salario Enero)")
        monto_gas = ft.TextField(label="Monto", keyboard_type=ft.KeyboardType.NUMBER)
        cat_educativa_gas = ft.Dropdown(
            options=[ft.dropdown.Option(n.value) for n in NivelEducativo],
            label="Categoría Educativa (Gasto)"
        )

        # Tablas
        self.tabla_ingresos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Monto (FCFA)")), ft.DataColumn(ft.Text("Persona")),
                ft.DataColumn(ft.Text("Fecha")), ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Acciones"))
            ],
            rows=[]
        )

        self.tabla_gastos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Monto (FCFA)")), ft.DataColumn(ft.Text("Persona")),
                ft.DataColumn(ft.Text("Fecha")), ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Acciones"))
            ],
            rows=[]
        )

        # Funciones de eventos
        def agregar_ingreso(e):
            if not desc_ing.value or not monto_ing.value:
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Completa descripción y monto"), bgcolor=ft.colors.RED))
                return
            persona_id = int(self.dropdown_persona.value) if self.dropdown_persona.value else None
            create_ingreso(self.db, desc_ing.value, float(monto_ing.value), cat_educativa_ing.value, persona_id)  
            self.cargar_ingresos()

        def agregar_gasto(e):
            if not desc_gas.value or not monto_gas.value:
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Completa descripción y monto"), bgcolor=ft.colors.RED))
                return
            persona_id = int(self.dropdown_persona.value) if self.dropdown_persona.value else None
            create_gasto(self.db, desc_gas.value, float(monto_gas.value), cat_educativa_gas.value, persona_id)
            desc_gas.value = monto_gas.value = cat_educativa_gas.value = ""
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Gasto agregado"), bgcolor=ft.colors.GREEN))
            self.cargar_gastos()

        # Cargas iniciales
        self.cargar_ingresos()
        self.cargar_gastos()

        # Layout completo
        layout = ft.Column(
            [
                ft.Text("Gestión de Ingresos y Gastos - PEBOSE", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("Filtro de Personas:", size=16),
                ft.Row([self.filtro_persona, self.dropdown_persona]),
                ft.Divider(),
                ft.Text("Ingresos:", size=16),
                ft.Row([desc_ing, monto_ing, cat_educativa_ing]),
                ft.ElevatedButton("Agregar Ingreso", on_click=agregar_ingreso),
                self.tabla_ingresos,
                ft.Divider(),
                ft.Text("Gastos:", size=16),
                ft.Row([desc_gas, monto_gas, cat_educativa_gas]),
                ft.ElevatedButton("Agregar Gasto", on_click=agregar_gasto),
                self.tabla_gastos,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=10
        )

        # Asigna a page_view.controls (Fix AttributeError)
        self.page_view.controls = [layout]
        self.page_view.scroll = ft.ScrollMode.AUTO

    def cargar_ingresos(self):
        ingresos = get_ingresos(self.db)
        self.tabla_ingresos.rows.clear()
        for ing in ingresos:
            persona_nombre = f"{ing.persona.nombre} {ing.persona.apellidos}" if ing.persona else "General"
            btn_edit = ft.IconButton(ft.icons.EDIT, on_click=lambda e, i=ing.id: self.edit_ingreso(i))
            btn_delete = ft.IconButton(ft.icons.DELETE, on_click=lambda e, i=ing.id: self.delete_ingreso(i))
            self.tabla_ingresos.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(ing.id))),
                ft.DataCell(ft.Text(ing.concepto)),
                ft.DataCell(ft.Text(f"{ing.monto:.2f}")),
                ft.DataCell(ft.Text(persona_nombre)),
                ft.DataCell(ft.Text(ing.fecha.strftime("%d/%m/%Y"))),
                ft.DataCell(ft.Text(ing.categoria)),
                ft.DataCell(ft.Row([btn_edit, btn_delete]))
            ]))
        self.page.update()

    def cargar_gastos(self):
        gastos = get_gastos(self.db)
        self.tabla_gastos.rows.clear()
        for gas in gastos:
            persona_nombre = f"{gas.persona.nombre} {gas.persona.apellidos}" if gas.persona else "General"
            btn_edit = ft.IconButton(ft.icons.EDIT, on_click=lambda e, g=gas.id: self.edit_gasto(g))
            btn_delete = ft.IconButton(ft.icons.DELETE, on_click=lambda e, g=gas.id: self.delete_gasto(g))
            self.tabla_gastos.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(gas.id))),
                ft.DataCell(ft.Text(gas.concepto)),
                ft.DataCell(ft.Text(f"{gas.monto:.2f}")),
                ft.DataCell(ft.Text(persona_nombre)),
                ft.DataCell(ft.Text(gas.fecha.strftime("%d/%m/%Y"))),
                ft.DataCell(ft.Text(gas.categoria)),
                ft.DataCell(ft.Row([btn_edit, btn_delete]))
            ]))
        self.page.update()

    def edit_ingreso(self, id):
        ing = self.db.query(Ingreso).filter(Ingreso.id == id).first()
        if ing:
            desc_edit = ft.TextField(value=ing.concepto)
            monto_edit = ft.TextField(value=str(ing.monto), keyboard_type=ft.KeyboardType.NUMBER)
            cat_edit = ft.Dropdown(value=ing.categoria, options=[ft.dropdown.Option("Matrícula"), ft.dropdown.Option("Cuota")])
            persona_edit = ft.Dropdown(value=str(ing.persona_id) if ing.persona_id else None, options=self.dropdown_persona.options)
            dialog = ft.AlertDialog(
                title=ft.Text("Editar Ingreso"),
                content=ft.Column([desc_edit, monto_edit, cat_edit, persona_edit], scroll=ft.ScrollMode.AUTO),
                actions=[ft.ElevatedButton("Guardar", on_click=lambda e: self.save_edit_ingreso(id, desc_edit.value, float(monto_edit.value), cat_edit.value, int(persona_edit.value) if persona_edit.value else None)), ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog))]
            )
            self.page.open(dialog)

    def save_edit_ingreso(self, id, concepto, monto, cat, persona_id):
        update_ingreso(self.db, id, concepto, monto, cat, persona_id)
        self.page.close(self.page.dialog)
        self.page.show_snack_bar(ft.SnackBar(ft.Text("Ingreso actualizado"), bgcolor=ft.colors.GREEN))
        self.cargar_ingresos()

    def delete_ingreso(self, id):
        def confirm_delete(e):
            delete_ingreso(self.db, id)
            self.page.close(dialog)
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Ingreso eliminado"), bgcolor=ft.colors.ORANGE))
            self.cargar_ingresos()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar"),
            content=ft.Text("¿Eliminar este ingreso?"),
            actions=[ft.ElevatedButton("Sí", on_click=confirm_delete), ft.TextButton("No", on_click=lambda e: self.page.close(dialog))]
        )
        self.page.open(dialog)

    # Métodos para gastos (similares)
    def edit_gasto(self, id):
        gas = self.db.query(Gasto).filter(Gasto.id == id).first()
        if gas:
            desc_edit = ft.TextField(value=gas.concepto)
            monto_edit = ft.TextField(value=str(gas.monto), keyboard_type=ft.KeyboardType.NUMBER)
            cat_edit = ft.Dropdown(value=gas.categoria, options=[ft.dropdown.Option("Salarios"), ft.dropdown.Option("Suministros")])
            persona_edit = ft.Dropdown(value=str(gas.persona_id) if gas.persona_id else None, options=self.dropdown_persona.options)
            dialog = ft.AlertDialog(
                title=ft.Text("Editar Gasto"),
                content=ft.Column([desc_edit, monto_edit, cat_edit, persona_edit], scroll=ft.ScrollMode.AUTO),
                actions=[ft.ElevatedButton("Guardar", on_click=lambda e: self.save_edit_gasto(id, desc_edit.value, float(monto_edit.value), cat_edit.value, int(persona_edit.value) if persona_edit.value else None)), ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog))]
            )
            self.page.open(dialog)

    def save_edit_gasto(self, id, desc, monto, cat, persona_id):
        update_gasto(self.db, id, desc, monto, cat, persona_id)
        self.page.close(self.page.dialog)
        self.page.show_snack_bar(ft.SnackBar(ft.Text("Gasto actualizado"), bgcolor=ft.colors.GREEN))
        self.cargar_gastos()

    def delete_gasto(self, id):
        def confirm_delete(e):
            delete_gasto(self.db, id)
            self.page.close(dialog)
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Gasto eliminado"), bgcolor=ft.colors.ORANGE))
            self.cargar_gastos()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar"),
            content=ft.Text("¿Eliminar este gasto?"),
            actions=[ft.ElevatedButton("Sí", on_click=confirm_delete), ft.TextButton("No", on_click=lambda e: self.page.close(dialog))]
        )
        self.page.open(dialog)