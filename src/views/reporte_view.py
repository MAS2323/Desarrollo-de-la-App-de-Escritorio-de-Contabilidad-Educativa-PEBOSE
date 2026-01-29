import flet as ft
import os
from services.reporte_service import calcular_balance, obtener_registros_filtrados, generar_reporte_pdf, generar_reporte_excel, generar_grafico_balance
from sqlalchemy.orm import Session
from services.persona_service import NivelEducativo
from datetime import datetime

class ReporteView:
    def __init__(self, page: ft.Page, db: Session):
        self.page = page
        self.db = db
        self.page_view = ft.View("/reportes", controls=[])
        self.tabla_registros = None
        self.balance_text = None
        self.filtros = {'categoria': None, 'nivel': None, 'tipo_registro': 'Ingresos', 'fecha_inicio': None, 'fecha_fin': None}

    def aplicar_filtros(self, e=None):
        """Aplica filtros y actualiza vista (tabla y balance)."""
        # Validación de fechas
        if self.filtros['fecha_inicio'] and self.filtros['fecha_fin'] and self.filtros['fecha_inicio'] > self.filtros['fecha_fin']:
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Fecha fin debe ser mayor o igual a fecha inicio"), bgcolor=ft.colors.RED))
            return
        
        data = calcular_balance(self.db, **self.filtros)
        self.balance_text.value = f"Ingresos: {data['ingresos']:,.2f} FCFA | Gastos: {data['gastos']:,.2f} FCFA | Balance: {data['balance']:,.2f} FCFA"
        
        registros = obtener_registros_filtrados(self.db, self.filtros['tipo_registro'], **{k: v for k, v in self.filtros.items() if k != 'tipo_registro'})
        self.tabla_registros.rows.clear()
        for reg in registros:
            self.tabla_registros.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(reg['id']))),
                ft.DataCell(ft.Text(reg['concepto'])),
                ft.DataCell(ft.Text(f"{reg['monto']:,.2f}")),
                ft.DataCell(ft.Text(reg['categoria'])),
                ft.DataCell(ft.Text(reg['fecha'].strftime('%d/%m/%Y'))),
                ft.DataCell(ft.Text(reg['persona']))
            ]))
        self.page.update()

    def limpiar_filtros(self, e):
        self.filtros = {'categoria': None, 'nivel': None, 'tipo_registro': 'Ingresos', 'fecha_inicio': None, 'fecha_fin': None}
        self.categoria_dropdown.value = None
        self.nivel_dropdown.value = None
        self.tipo_dropdown.value = "Ingresos"
        self.fecha_inicio_picker.value = None
        self.fecha_fin_picker.value = None
        self.aplicar_filtros()

    def build(self):
        # Filtros
        self.categoria_dropdown = ft.Dropdown(
            label="Categoría",
            options=[ft.dropdown.Option("Matrícula"), ft.dropdown.Option("APA"), ft.dropdown.Option("Uniforme regular"), ft.dropdown.Option("Uniforme de deporte")],
            on_change=lambda e: (self.filtros.__setitem__('categoria', e.control.value), self.aplicar_filtros())
        )
        self.nivel_dropdown = ft.Dropdown(
            label="Nivel Educativo",
            options=[ft.dropdown.Option(n.value) for n in NivelEducativo],
            on_change=lambda e: (self.filtros.__setitem__('nivel', e.control.value), self.aplicar_filtros())
        )
        self.tipo_dropdown = ft.Dropdown(
            label="Tipo de Registro",
            options=[ft.dropdown.Option("Ingresos"), ft.dropdown.Option("Gastos")],
            value="Ingresos",
            on_change=lambda e: (self.filtros.__setitem__('tipo_registro', e.control.value), self.aplicar_filtros())
        )
        # Envuelve DatePicker en Column con Text para "label"
        self.fecha_inicio_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
            on_change=lambda e: (self.filtros.__setitem__('fecha_inicio', datetime.combine(e.control.value, datetime.min.time()) if e.control.value else None), self.aplicar_filtros())
        )
        fecha_inicio_col = ft.Column([
            ft.Text("Fecha Inicio", size=12),
            self.fecha_inicio_picker
        ])
        self.fecha_fin_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
            on_change=lambda e: (self.filtros.__setitem__('fecha_fin', datetime.combine(e.control.value, datetime.max.time()) if e.control.value else None), self.aplicar_filtros())
        )
        fecha_fin_col = ft.Column([
            ft.Text("Fecha Fin", size=12),
            self.fecha_fin_picker
        ])
        btn_limpiar_filtros = ft.TextButton("Limpiar Filtros", on_click=self.limpiar_filtros)

        self.balance_text = ft.Text("Cargando...", size=18, weight=ft.FontWeight.BOLD)

        self.tabla_registros = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Concepto")),
                ft.DataColumn(ft.Text("Monto (FCFA)")),
                ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Persona"))
            ],
            rows=[],
            expand=1,
            border=ft.border.all(1, "grey")  # Borde para mejor visualización
        )

        def pdf_click(e):
            path = generar_reporte_pdf(self.db, **self.filtros)
            if path:
                self.page.show_snack_bar(ft.SnackBar(ft.Text(f"PDF generado: {os.path.basename(path)}"), bgcolor=ft.colors.GREEN))
            else:
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Error al generar PDF"), bgcolor=ft.colors.RED))

        def excel_click(e):
            path = generar_reporte_excel(self.db, **self.filtros)
            if path:
                self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Excel generado: {os.path.basename(path)}"), bgcolor=ft.colors.GREEN))
            else:
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Error al generar Excel"), bgcolor=ft.colors.RED))

        def grafico_click(e):
            path = generar_grafico_balance(self.db, **self.filtros)
            if path:
                img = ft.Image(src=path, width=400, height=300)
                dialog = ft.AlertDialog(
                    title=ft.Text("Gráfico de Balance Filtrado"),
                    content=img,
                    actions=[ft.TextButton("Cerrar", on_click=lambda e: self.page.close(dialog))]
                )
                self.page.open(dialog)
            else:
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Error al generar gráfico"), bgcolor=ft.colors.RED))

        # Layout completo con filtros y tabla
        layout = ft.Column(
            [
                ft.Text("Reportes Financieros PEBOSE", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("Filtros:", size=16),
                ft.Row([self.categoria_dropdown, self.nivel_dropdown]),
                ft.Row([self.tipo_dropdown, fecha_inicio_col, fecha_fin_col]),
                ft.Row([btn_limpiar_filtros]),
                self.balance_text,
                ft.Divider(),
                self.tabla_registros,
                ft.Divider(),
                ft.Row([
                    ft.ElevatedButton("Generar PDF", on_click=pdf_click),
                    ft.ElevatedButton("Generar Excel", on_click=excel_click),
                    ft.ElevatedButton("Ver Gráfico", on_click=grafico_click)
                ], alignment=ft.MainAxisAlignment.CENTER),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            expand=True
        )

        # Carga inicial
        self.aplicar_filtros()

        self.page_view.controls = [layout]
        self.page_view.scroll = ft.ScrollMode.AUTO