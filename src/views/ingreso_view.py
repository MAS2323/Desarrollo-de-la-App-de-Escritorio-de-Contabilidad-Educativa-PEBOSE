import flet as ft
import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from services.db_service import create_ingreso, get_ingresos, create_gasto, get_gastos, update_ingreso, delete_ingreso, update_gasto, delete_gasto
from services.persona_service import get_personas_filtro, insertar_datos_prueba, NivelEducativo, calcular_monto_pago
from sqlalchemy.orm import Session
from models.persona import Persona
from models.ingreso import Ingreso
from models.gasto import Gasto

class IngresoView:
    def __init__(self, page: ft.Page, db: Session):
        self.page = page
        self.db = db
        self.page_view = ft.View("/ingresos", controls=[])
        self.tabla_ingresos = None
        self.tabla_gastos = None
        self.dropdown_persona = None
        self.filtro_persona = None
        self.dropdown_tipo_pago = None
        self.dropdown_opcion_mensual = None
        self.btn_generar_factura = None
        self.monto_ing = None
        insertar_datos_prueba(self.db)
   
    def generar_factura_pdf(self, persona: Persona, tipo_pago: str) -> str:
        """Genera PDF factura para el estudiante y tipo de pago."""
        try:
            monto = calcular_monto_pago(persona.nivel_educativo.value, tipo_pago)
            fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
            filename = f"factura_{persona.nombre}_{persona.apellidos}_{tipo_pago}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            pdf_path = Path("reports") / filename
            pdf_path.parent.mkdir(exist_ok=True)
           
            c = canvas.Canvas(str(pdf_path), pagesize=letter)
            y = 750
           
            # Header PEBOSE
            c.drawString(100, y, "PEBOSE CONTABILIDAD - FACTURA DE PAGO")
            y -= 30
            c.drawString(100, y, f"Estudiante: {persona.nombre} {persona.apellidos}")
            y -= 20
            c.drawString(100, y, f"Nivel Educativo: {persona.nivel_educativo.value}")
            y -= 20
            c.drawString(100, y, f"Tipo de Pago: {tipo_pago}")
            y -= 20
            c.drawString(100, y, f"Monto: {monto:,.2f} FCFA")
            y -= 20
            c.drawString(100, y, f"Fecha de Emisión: {fecha_actual}")
            y -= 40
            c.drawString(100, y, "Gracias por su pago. ¡Bienvenido a PEBOSE!")
            y -= 20
            c.drawString(100, y, "Firma: ________________________")
           
            c.save()
            return str(pdf_path)
        except Exception as ex:
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Error al generar factura: {ex}"), bgcolor=ft.colors.RED))
            return None

    def imprimir_factura(self, pdf_path: str):
        """Imprime PDF directamente (Windows)."""
        try:
            os.startfile(pdf_path, "print")
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Factura enviada a impresión"), bgcolor=ft.colors.GREEN))
        except Exception as ex:
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Error al imprimir: {ex}"), bgcolor=ft.colors.RED))

    def on_tipo_pago_change(self, e):
        """Auto-llena monto basado en persona, nivel y tipo pago."""
        if self.dropdown_persona.value:
            persona = self.db.query(Persona).filter(Persona.id == int(self.dropdown_persona.value)).first()
            if persona:
                nivel = persona.nivel_educativo.value
                tipo_pago = self.dropdown_tipo_pago.value
                opcion = self.dropdown_opcion_mensual.value if self.dropdown_opcion_mensual.visible else None
                monto = calcular_monto_pago(nivel, tipo_pago, opcion)
                if monto > 0:
                    self.monto_ing.value = str(monto)
                    self.page.update()
                else:
                    self.page.show_snack_bar(ft.SnackBar(ft.Text("Monto no calculable para este tipo"), bgcolor=ft.colors.ORANGE))

    def toggle_opcion_mensual(self, e):
        """Muestra/oculta opciones mensuales para Guardería."""
        if self.dropdown_persona.value:
            persona = self.db.query(Persona).filter(Persona.id == int(self.dropdown_persona.value)).first()
            if persona and persona.nivel_educativo.value == 'Guarderia' and self.dropdown_tipo_pago.value == 'Matricula':
                self.dropdown_opcion_mensual.visible = True
            else:
                self.dropdown_opcion_mensual.visible = False
            self.page.update()

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
            width=300,
            on_change=self.toggle_opcion_mensual
        )
        self.cargar_personas_dropdown(None)

        # Dropdown para tipo de matrícula/pago
        self.dropdown_tipo_pago = ft.Dropdown(
            label="Tipo de Matrícula/Pago",
            options=[
                ft.dropdown.Option("Matricula"),
                ft.dropdown.Option("APA"),
                ft.dropdown.Option("Uniforme regular"),
                ft.dropdown.Option("Uniforme de deporte")
            ],
            on_change=lambda e: (self.on_tipo_pago_change(e), self.toggle_opcion_mensual(e))
        )

        # Para Guardería: Opciones mensuales
        self.dropdown_opcion_mensual = ft.Dropdown(
            label="Opción Mensual (solo Guardería Matrícula)",
            options=[
                ft.dropdown.Option("1", "75,000 FCFA"),
                ft.dropdown.Option("2", "100,000 FCFA"),
                ft.dropdown.Option("3", "130,000 FCFA")
            ],
            visible=False,
            on_change=self.on_tipo_pago_change
        )

        # Formularios de ingresos (con auto-monto)
        desc_ing = ft.TextField(label="Descripción (ej. Matrícula Enero)")
        self.monto_ing = ft.TextField(label="Monto (auto-calculado)", keyboard_type=ft.KeyboardType.NUMBER)
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

        # CREAR BOTÓN AQUÍ (antes del layout, fuera de las listas)
        def generar_factura_click(e):
            if not self.dropdown_persona.value or not self.dropdown_tipo_pago.value:
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Selecciona estudiante y tipo de pago"), bgcolor=ft.colors.RED))
                return
            persona = self.db.query(Persona).filter(Persona.id == int(self.dropdown_persona.value)).first()
            if persona:
                pdf_path = self.generar_factura_pdf(persona, self.dropdown_tipo_pago.value)
                if pdf_path:
                    self.imprimir_factura(pdf_path)

        self.btn_generar_factura = ft.ElevatedButton(
            "Generar Factura", 
            on_click=generar_factura_click, 
            disabled=True
        )

        # Tablas
        self.tabla_ingresos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Monto (FCFA)")), ft.DataColumn(ft.Text("Tipo Pago")),
                ft.DataColumn(ft.Text("Persona")), ft.DataColumn(ft.Text("Nivel Educativo")),
                ft.DataColumn(ft.Text("Fecha")), ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Acciones"))
            ],
            rows=[]
        )

        self.tabla_gastos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Monto (FCFA)")), ft.DataColumn(ft.Text("Persona")),
                ft.DataColumn(ft.Text("Nivel Educativo")),
                ft.DataColumn(ft.Text("Fecha")), ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Acciones"))
            ],
            rows=[]
        )

        # Funciones de eventos
        def agregar_ingreso(e):
            if not desc_ing.value or not self.monto_ing.value or self.monto_ing.value == '0':
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Completa descripción, tipo de pago y verifica monto"), bgcolor=ft.colors.RED))
                return
            try:
                persona_id = int(self.dropdown_persona.value) if self.dropdown_persona.value else None
                tipo_pago = self.dropdown_tipo_pago.value or cat_educativa_ing.value
                create_ingreso(self.db, desc_ing.value, float(self.monto_ing.value), tipo_pago, persona_id)
                desc_ing.value = self.monto_ing.value = self.dropdown_tipo_pago.value = cat_educativa_ing.value = ""
                self.dropdown_opcion_mensual.visible = False
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Ingreso agregado"), bgcolor=ft.colors.GREEN))
                self.cargar_ingresos()
            except ValueError as ve:
                self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Error en monto: {ve}"), bgcolor=ft.colors.RED))

        def agregar_gasto(e):
            if not desc_gas.value or not monto_gas.value:
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Completa descripción y monto"), bgcolor=ft.colors.RED))
                return
            try:
                persona_id = int(self.dropdown_persona.value) if self.dropdown_persona.value else None
                create_gasto(self.db, desc_gas.value, float(monto_gas.value), cat_educativa_gas.value, persona_id)
                desc_gas.value = monto_gas.value = cat_educativa_gas.value = ""
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Gasto agregado"), bgcolor=ft.colors.GREEN))
                self.cargar_gastos()
            except ValueError as ve:
                self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Error en monto: {ve}"), bgcolor=ft.colors.RED))

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
                ft.Row([desc_ing, self.dropdown_tipo_pago, self.dropdown_opcion_mensual, self.monto_ing, cat_educativa_ing]),
                ft.Row([
                    ft.ElevatedButton("Agregar Ingreso", on_click=agregar_ingreso),
                    self.btn_generar_factura  # Referencia al botón ya creado
                ]),
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

        # Habilita botón factura al cambiar selección
        def enable_factura(e):
            self.btn_generar_factura.disabled = not (self.dropdown_persona.value and self.dropdown_tipo_pago.value)
            self.page.update()
            
        self.dropdown_persona.on_change = lambda e: (self.toggle_opcion_mensual(e), enable_factura(e))
        self.dropdown_tipo_pago.on_change = lambda e: (self.on_tipo_pago_change(e), self.toggle_opcion_mensual(e), enable_factura(e))

        self.page_view.controls = [layout]
        self.page_view.scroll = ft.ScrollMode.AUTO

    def cargar_ingresos(self):
        ingresos = get_ingresos(self.db)
        self.tabla_ingresos.rows.clear()
        for ing in ingresos:
            persona_nombre = f"{ing.persona.nombre} {ing.persona.apellidos}" if ing.persona else "General"
            nivel_educativo = ing.persona.nivel_educativo.value if ing.persona else "General"
            btn_edit = ft.IconButton(ft.icons.EDIT, on_click=lambda e, i=ing.id: self.edit_ingreso(i))
            btn_delete = ft.IconButton(ft.icons.DELETE, on_click=lambda e, i=ing.id: self.delete_ingreso(i))
            self.tabla_ingresos.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(ing.id))),
                ft.DataCell(ft.Text(ing.concepto)),
                ft.DataCell(ft.Text(f"{ing.monto:.2f}")),
                ft.DataCell(ft.Text(ing.categoria)),
                ft.DataCell(ft.Text(persona_nombre)),
                ft.DataCell(ft.Text(nivel_educativo)),
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
            nivel_educativo = gas.persona.nivel_educativo.value if gas.persona else "General"
            btn_edit = ft.IconButton(ft.icons.EDIT, on_click=lambda e, g=gas.id: self.edit_gasto(g))
            btn_delete = ft.IconButton(ft.icons.DELETE, on_click=lambda e, g=gas.id: self.delete_gasto(g))
            self.tabla_gastos.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(gas.id))),
                ft.DataCell(ft.Text(gas.concepto)),
                ft.DataCell(ft.Text(f"{gas.monto:.2f}")),
                ft.DataCell(ft.Text(persona_nombre)),
                ft.DataCell(ft.Text(nivel_educativo)),
                ft.DataCell(ft.Text(gas.fecha.strftime("%d/%m/%Y"))),
                ft.DataCell(ft.Text(gas.categoria)),
                ft.DataCell(ft.Row([btn_edit, btn_delete]))
            ]))
        self.page.update()

    def edit_ingreso(self, id):
        ing = self.db.query(Ingreso).filter(Ingreso.id == id).first()
        if ing:
            # Implementar diálogo de edición aquí
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Editar ingreso {id} - por implementar"), bgcolor=ft.colors.BLUE))

    def delete_ingreso(self, id):
        try:
            delete_ingreso(self.db, id)
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Ingreso eliminado"), bgcolor=ft.colors.GREEN))
            self.cargar_ingresos()
        except Exception as ex:
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"), bgcolor=ft.colors.RED))

    def edit_gasto(self, id):
        gas = self.db.query(Gasto).filter(Gasto.id == id).first()
        if gas:
            # Implementar diálogo de edición aquí
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Editar gasto {id} - por implementar"), bgcolor=ft.colors.BLUE))

    def delete_gasto(self, id):
        try:
            delete_gasto(self.db, id)
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Gasto eliminado"), bgcolor=ft.colors.GREEN))
            self.cargar_gastos()
        except Exception as ex:
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"), bgcolor=ft.colors.RED))