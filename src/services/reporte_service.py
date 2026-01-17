import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from pathlib import Path
from models.ingreso import Ingreso
from models.gasto import Gasto

# Directorio base del proyecto (donde se guardarán los reportes)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"

# Asegura que el directorio de reportes existe
REPORTS_DIR.mkdir(exist_ok=True)

def calcular_balance(db: Session) -> dict:
    try:
        ingresos = db.query(Ingreso.monto).all()
        gastos = db.query(Gasto.monto).all()
        total_ingresos = sum([i[0] for i in ingresos])
        total_gastos = sum([g[0] for g in gastos])
        balance = total_ingresos - total_gastos
        return {'ingresos': total_ingresos, 'gastos': total_gastos, 'balance': balance}
    except Exception as e:
        print(f"Error calculando balance: {e}")
        return {'ingresos': 0, 'gastos': 0, 'balance': 0}

def generar_reporte_pdf(db: Session, filename: str = None) -> str:
    try:
        if filename is None:
            filename = REPORTS_DIR / "balance_pebose.pdf"
        
        data = calcular_balance(db)
        c = canvas.Canvas(str(filename), pagesize=letter)
        c.drawString(100, 750, "Reporte Financiero PEBOSE")
        c.drawString(100, 720, f"Fecha de generación: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")
        c.drawString(100, 680, f"Ingresos Total: {data['ingresos']:,.2f} FCFA")
        c.drawString(100, 650, f"Gastos Total: {data['gastos']:,.2f} FCFA")
        c.drawString(100, 620, f"Balance: {data['balance']:,.2f} FCFA")
        c.save()
        return str(filename)
    except Exception as e:
        print(f"Error generando PDF: {e}")
        return None

def generar_reporte_excel(db: Session, filename: str = None) -> str:
    try:
        if filename is None:
            filename = REPORTS_DIR / "reporte_pebose.xlsx"
        
        data = calcular_balance(db)
        
        # Crear DataFrame con más detalles
        df_resumen = pd.DataFrame([{
            'Concepto': 'Resumen Financiero',
            'Ingresos Total (FCFA)': data['ingresos'],
            'Gastos Total (FCFA)': data['gastos'],
            'Balance (FCFA)': data['balance'],
            'Fecha Generación': pd.Timestamp.now()
        }])
        
        # Obtener datos detallados
        ingresos_detalle = db.query(Ingreso).all()
        gastos_detalle = db.query(Gasto).all()
        
        df_ingresos = pd.DataFrame([{
            'ID': i.id,
            'Concepto': i.concepto,
            'Monto': i.monto,
            'Categoría': i.categoria,
            'Fecha': i.fecha,
            'Persona': f"{i.persona.nombre} {i.persona.apellidos}" if i.persona else "General"
        } for i in ingresos_detalle])
        
        df_gastos = pd.DataFrame([{
            'ID': g.id,
            'Concepto': g.concepto,
            'Monto': g.monto,
            'Categoría': g.categoria,
            'Fecha': g.fecha,
            'Persona': f"{g.persona.nombre} {g.persona.apellidos}" if g.persona else "General"
        } for g in gastos_detalle])
        
        # Guardar múltiples hojas en el Excel
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
            df_ingresos.to_excel(writer, sheet_name='Ingresos Detalle', index=False)
            df_gastos.to_excel(writer, sheet_name='Gastos Detalle', index=False)
        
        return str(filename)
    except Exception as e:
        print(f"Error generando Excel: {e}")
        return None

def generar_grafico_balance(db: Session, filename: str = None) -> str:
    try:
        if filename is None:
            filename = REPORTS_DIR / "grafico_balance.png"
        
        data = calcular_balance(db)
        plt.figure(figsize=(10, 6))
        
        # Gráfico de barras
        plt.subplot(1, 2, 1)
        plt.bar(['Ingresos', 'Gastos'], [data['ingresos'], data['gastos']], color=['green', 'red'])
        plt.title('Balance PEBOSE')
        plt.ylabel('FCFA')
        
        # Gráfico de pastel
        plt.subplot(1, 2, 2)
        plt.pie([data['ingresos'], data['gastos']], labels=['Ingresos', 'Gastos'], autopct='%1.1f%%')
        plt.title('Distribución')
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        return str(filename)
    except Exception as e:
        print(f"Error generando gráfico: {e}")
        return None