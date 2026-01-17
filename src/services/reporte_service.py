import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy.orm import Session
from models.base import Ingreso, Gasto
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def calcular_balance(db: Session) -> dict:
    ingresos = db.query(Ingreso.monto).all()
    gastos = db.query(Gasto.monto).all()
    total_ingresos = sum([i[0] for i in ingresos])
    total_gastos = sum([g[0] for g in gastos])
    balance = total_ingresos - total_gastos
    return {'ingresos': total_ingresos, 'gastos': total_gastos, 'balance': balance}

def generar_reporte_pdf(db: Session, filename: str = None):
    if not filename:
        filename = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../balance_pebose.pdf'))
    data = calcular_balance(db)
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, "Reporte Financiero PEBOSE")
    c.drawString(100, 700, f"Ingresos Total: {data['ingresos']:.2f} FCFA")
    c.drawString(100, 675, f"Gastos Total: {data['gastos']:.2f} FCFA")
    c.drawString(100, 650, f"Balance: {data['balance']:.2f} FCFA")
    c.save()
    return filename

def generar_reporte_excel(db: Session, filename: str = None):
    if not filename:
        filename = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../reporte_pebose.xlsx'))
    data = calcular_balance(db)
    df = pd.DataFrame([data])
    df.to_excel(filename, index=False)
    return filename

def generar_grafico_balance(db: Session, filename: str = None):
    if not filename:
        filename = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../grafico_balance.png'))
    data = calcular_balance(db)
    plt.figure(figsize=(8, 5))
    plt.bar(['Ingresos', 'Gastos'], [data['ingresos'], data['gastos']])
    plt.title('Balance PEBOSE')
    plt.ylabel('FCFA')
    plt.savefig(filename)
    plt.close()
    return filename