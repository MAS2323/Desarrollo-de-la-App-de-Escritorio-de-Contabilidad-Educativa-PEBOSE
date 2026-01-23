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
        self.page_view = ft.View("/ingresos", controls=[])
        self.tabla_ingresos = None
        self.tabla_gastos = None
        self.dropdown_persona = None
        self.filtro_persona = None
        self.dropdown_tipo_pago = None  # Nuevo: Para tipos de pagos
        self.dropdown_opcion_mensual = None  # Para opciones en Guardería
        insertar_datos_prueba(self.db)
    
    def calcular_monto(self, nivel: str, tipo_pago: str, opcion_mensual: str = None) -> float:
        """Calcula monto automático basado en nivel y tipo de pago."""
        montos = {
            'Guardería': {'Matrícula': [75000, 100000, 130000]},  # Opciones mensuales
            'Prescolar': {'Matrícula': 130000, 'Uniforme regular': 20000, 'Uniforme de deporte': 20000},
            'Primaria': {'Matrícula': 120000, 'Uniforme regular': 25000, 'Uniforme de deporte': 25000},
            'Sexto Primaria': {'Matrícula': 180000, 'Uniforme regular': 25000, 'Uniforme de deporte': 25000},
            'ESBA': {'Matrícula': 195000, 'Uniforme regular': 45000, 'Uniforme de deporte': 45000},
            'Bachillerato': {'Matrícula': 195000, 'Uniforme regular': 45000, 'Uniforme de deporte': 45000}  # Asumiendo igual a ESBA
        }
        if nivel in montos and tipo_pago in montos[nivel]:
            monto = montos[nivel][tipo_pago]
            if isinstance(monto, list) and opcion_mensual:  # Guardería
                return monto[int(opcion_mensual) - 1]  # 1=75k, 2=100k, 3=130k
            return monto
        return 0.0  # Default si no coincide

    def cargar_personas_dropdown(self, e):
        filtro = self.filtro_persona.value or ""
        personas = get_personas_filtro(self.db, filtro)
        self.dropdown_persona.options = [
            ft.dropdown.Option(str(p.id), f"{p.nombre} {p.apellidos} ({p.tipo} - {p.nivel_educativo.value})")
            for p in personas
        ]
        self.page.update()

    def on_tipo_pago_change(self, e):
        # Auto-llena monto basado en nivel y tipo
        if self.dropdown_persona.value:
            persona = self.db.query(Persona).filter(Persona.id == int(self.dropdown_persona.value)).first()
            if persona:
                nivel = persona.nivel_educativo.value
                tipo_pago = self.dropdown_tipo_pago.value
                monto = self.calcular_monto(nivel, tipo_pago)
                if monto > 0:
                    self.monto_ing.value = str(monto)  # Asume monto_ing para ingresos; ajusta para gastos si necesario
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

        # Nuevo: Dropdown para tipos de pagos
        self.dropdown_tipo_pago = ft.Dropdown(
            label="Tipo de Pago",
            options=[
                ft.dropdown.Option("Matrícula"),
                ft.dropdown.Option("APA"),
                ft.dropdown.Option("Uniforme regular"),
                ft.dropdown.Option("Uniforme de deporte")
            ],
            on_change=self.on_tipo_pago_change  # Auto-llena monto
        )

        # Para Guardería: Opciones mensuales
        self.dropdown_opcion_mensual = ft.Dropdown(
            label="Opción Mensual (solo Guardería)",
            options=[
                ft.dropdown.Option("1", "75,000 FCFA"),
                ft.dropdown.Option("2", "100,000 FCFA"),
                ft.dropdown.Option("3", "130,000 FCFA")
            ],
            visible=False  # Solo visible si nivel es Guardería
        )

        # Formularios de ingresos (agregado dropdown tipo pago y auto-monto)
        desc_ing = ft.TextField(label="Descripción (ej. Matrícula Enero)")
        self.monto_ing = ft.TextField(label="Monto (auto-calculado)", keyboard_type=ft.KeyboardType.NUMBER)
        cat_educativa_ing = ft.Dropdown(
            options=[ft.dropdown.Option(n.value) for n in NivelEducativo],
            label="Categoría Educativa (Ingreso)"
        )

        # Formularios de gastos (similar)
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

        # Funciones de eventos (mejoradas con validación y auto-monto)
        def agregar_ingreso(e):
            if not desc_ing.value or not self.monto_ing.value or self.monto_ing.value == '0':
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Completa descripción, tipo de pago y verifica monto"), bgcolor=ft.colors.RED))
                return
            try:
                persona_id = int(self.dropdown_persona.value) if self.dropdown_persona.value else None
                create_ingreso(self.db, desc_ing.value, float(self.monto_ing.value), self.dropdown_tipo_pago.value, persona_id)
                desc_ing.value = self.monto_ing.value = self.dropdown_tipo_pago.value = ""  # Reset campos
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
                desc_gas.value = monto_gas.value = cat_educativa_gas.value = ""  # Reset campos
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Gasto agregado"), bgcolor=ft.colors.GREEN))
                self.cargar_gastos()
            except ValueError as ve:
                self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Error en monto: {ve}"), bgcolor=ft.colors.RED))

        # Cargas iniciales
        self.cargar_ingresos()
        self.cargar_gastos()

        # Layout completo (agregado dropdown tipo pago)
        layout = ft.Column(
            [
                ft.Text("Gestión de Ingresos y Gastos - PEBOSE", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("Filtro de Personas:", size=16),
                ft.Row([self.filtro_persona, self.dropdown_persona]),
                ft.Divider(),
                ft.Text("Ingresos:", size=16),
                ft.Row([desc_ing, self.dropdown_tipo_pago, self.dropdown_opcion_mensual, self.monto_ing, cat_educativa_ing]),
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

        # Asigna a page_view.controls
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
            # Fix: Define dialog ANTES de actions para evitar UnboundLocalError
            dialog = ft.AlertDialog(
                title=ft.Text("Editar Ingreso"),
                content=ft.Column([desc_edit, monto_edit, cat_edit, persona_edit], scroll=ft.ScrollMode.AUTO),
                actions=[
                    ft.ElevatedButton("Guardar", on_click=lambda e, dlg=dialog: self.save_edit_ingreso(id, desc_edit.value, float(monto_edit.value), cat_edit.value, int(persona_edit.value) if persona_edit.value else None, dlg)),
                    ft.TextButton("Cancelar", on_click=lambda e, dlg=dialog: self.page.close(dlg))
                ]
            )
            self.page.open(dialog)

    def save_edit_ingreso(self, id, concepto, monto, cat, persona_id, dlg):
        try:
            update_ingreso(self.db, id, concepto, monto, cat, persona_id)
            dlg.open = False  # Fix: Cierra el dialog específico con closure
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Ingreso actualizado"), bgcolor=ft.colors.GREEN))
            self.cargar_ingresos()
        except Exception as ex:
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"), bgcolor=ft.colors.RED))

    def delete_ingreso(self, id):
        # Fix: Define dialog ANTES de actions
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar"),
            content=ft.Text("¿Eliminar este ingreso?"),
            actions=[
                ft.ElevatedButton("Sí", on_click=lambda e, dlg=dialog: self.confirm_delete_ingreso(id, dlg)),
                ft.TextButton("No", on_click=lambda e, dlg=dialog: self.page.close(dlg))
            ]
        )
        self.page.open(dialog)

    def confirm_delete_ingreso(self, id, dlg):
        try:
            delete_ingreso(self.db, id)
            dlg.open = False  # Fix: Cierra el dialog específico con closure
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Ingreso eliminado"), bgcolor=ft.colors.ORANGE))
            self.cargar_ingresos()
        except Exception as ex:
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"), bgcolor=ft.colors.RED))

    # Métodos para gastos (similares a ingresos)
    def edit_gasto(self, id):
        gas = self.db.query(Gasto).filter(Gasto.id == id).first()
        if gas:
            desc_edit = ft.TextField(value=gas.concepto)
            monto_edit = ft.TextField(value=str(gas.monto), keyboard_type=ft.KeyboardType.NUMBER)
            cat_edit = ft.Dropdown(value=gas.categoria, options=[ft.dropdown.Option("Salarios"), ft.dropdown.Option("Suministros")])
            persona_edit = ft.Dropdown(value=str(gas.persona_id) if gas.persona_id else None, options=self.dropdown_persona.options)
            # Fix: Define dialog ANTES de actions
            dialog = ft.AlertDialog(
                title=ft.Text("Editar Gasto"),
                content=ft.Column([desc_edit, monto_edit, cat_edit, persona_edit], scroll=ft.ScrollMode.AUTO),
                actions=[
                    ft.ElevatedButton("Guardar", on_click=lambda e, dlg=dialog: self.save_edit_gasto(id, desc_edit.value, float(monto_edit.value), cat_edit.value, int(persona_edit.value) if persona_edit.value else None, dlg)),
                    ft.TextButton("Cancelar", on_click=lambda e, dlg=dialog: self.page.close(dlg))
                ]
            )
            self.page.open(dialog)

    def save_edit_gasto(self, id, concepto, monto, cat, persona_id, dlg):
        try:
            update_gasto(self.db, id, concepto, monto, cat, persona_id)
            dlg.open = False  # Fix: Cierra el dialog específico con closure
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Gasto actualizado"), bgcolor=ft.colors.GREEN))
            self.cargar_gastos()
        except Exception as ex:
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"), bgcolor=ft.colors.RED))

    def delete_gasto(self, id):
        # Fix: Define dialog ANTES de actions
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar"),
            content=ft.Text("¿Eliminar este gasto?"),
            actions=[
                ft.ElevatedButton("Sí", on_click=lambda e, dlg=dialog: self.confirm_delete_gasto(id, dlg)),
                ft.TextButton("No", on_click=lambda e, dlg=dialog: self.page.close(dlg))
            ]
        )
        self.page.open(dialog)

    def confirm_delete_gasto(self, id, dlg):
        try:
            delete_gasto(self.db, id)
            dlg.open = False  # Fix: Cierra el dialog específico con closure
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Gasto eliminado"), bgcolor=ft.colors.ORANGE))
            self.cargar_gastos()
        except Exception as ex:
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"), bgcolor=ft.colors.RED))