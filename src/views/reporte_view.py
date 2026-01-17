import flet as ft
from services.reporte_service import calcular_balance, generar_reporte_pdf, generar_reporte_excel, generar_grafico_balance
from sqlalchemy.orm import Session
import os

class ReporteView:
    def __init__(self, page: ft.Page, db: Session):
        self.page = page
        self.db = db
        self.page_view = ft.View("/reportes", controls=[])

    def build(self):
        data = calcular_balance(self.db)

        balance_text = ft.Text(f"Balance Actual: {data['balance']:.2f} FCFA", size=18, weight=ft.FontWeight.BOLD)

        def pdf_click(e):
            path = generar_reporte_pdf(self.db)
            self.page.snack_bar = ft.SnackBar(ft.Text(f"PDF generado: {os.path.basename(path)}"), bgcolor=ft.colors.GREEN)
            self.page.snack_bar.open = True
            self.page.update()

        def excel_click(e):
            path = generar_reporte_excel(self.db)
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Excel generado: {os.path.basename(path)}"), bgcolor=ft.colors.GREEN)
            self.page.snack_bar.open = True
            self.page.update()

        def grafico_click(e):
            path = generar_grafico_balance(self.db)
            img = ft.Image(src=path, width=400, height=300)

            dialog = ft.AlertDialog(
                title=ft.Text("Gráfico de Balance PEBOSE"),
                content=img,
                actions_alignment=ft.MainAxisAlignment.END,
                actions=[
                    ft.TextButton(
                        "Cerrar",
                        on_click=lambda e: self.page.close(dialog)
                    )
                ]
            )

            self.page.open(dialog)

        layout_column = ft.Column(
            [
                ft.Text("Reportes Financieros PEBOSE", size=20),
                balance_text,
                ft.Row([
                    ft.ElevatedButton("Generar PDF", on_click=pdf_click),
                    ft.ElevatedButton("Generar Excel", on_click=excel_click),
                    ft.ElevatedButton("Ver Gráfico", on_click=grafico_click)
                ]),
                ft.ElevatedButton("Volver al Home", on_click=lambda _: self.page.go("/home"))
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        self.page_view.controls = [layout_column]
        self.page_view.scroll = ft.ScrollMode.AUTO