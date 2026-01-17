import flet as ft
from services.reporte_service import calcular_balance, generar_reporte_pdf, generar_reporte_excel, generar_grafico_balance
from sqlalchemy.orm import Session
import os

class ReporteView:
    def __init__(self, page: ft.Page, db: Session):
        self.page = page
        self.db = db
        self.page_view = ft.View("/reportes", controls=[])  # Fix: Crea page_view en __init__

    def build(self):
        data = calcular_balance(self.db)
        balance_text = ft.Text(f"Balance Actual: {data['balance']:.2f} FCFA", size=18, weight=ft.FontWeight.BOLD)

        def pdf_click(e):
            path = generar_reporte_pdf(self.db)
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"PDF generado: {os.path.basename(path)}"), bgcolor=ft.colors.GREEN))

        def excel_click(e):
            path = generar_reporte_excel(self.db)
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Excel generado: {os.path.basename(path)}"), bgcolor=ft.colors.GREEN))

        def grafico_click(e):
            path = generar_grafico_balance(self.db)
            img = ft.Image(src=path, width=400, height=300)
            dialog = ft.AlertDialog(
                title=ft.Text("Gráfico de Balance PEBOSE"),
                content=img,
                actions=[ft.TextButton("Cerrar", on_click=lambda e: self.page.close(dialog))]
            )
            self.page.open(dialog)

        # Layout completo
        layout = ft.Column(
            [
                ft.Text("Reportes Financieros PEBOSE", size=20, weight=ft.FontWeight.BOLD),
                balance_text,
                ft.Row([
                    ft.ElevatedButton("Generar PDF", on_click=pdf_click),
                    ft.ElevatedButton("Generar Excel", on_click=excel_click),
                    ft.ElevatedButton("Ver Gráfico", on_click=grafico_click)
                ], alignment=ft.MainAxisAlignment.CENTER),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Asigna a page_view.controls (Fix AttributeError)
        self.page_view.controls = [layout]
        self.page_view.scroll = ft.ScrollMode.AUTO
