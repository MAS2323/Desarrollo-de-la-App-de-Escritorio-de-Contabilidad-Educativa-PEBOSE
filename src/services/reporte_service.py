import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from pathlib import Path
from datetime import datetime
from models.ingreso import Ingreso
from models.gasto import Gasto
from models.persona import Persona
from services.persona_service import NivelEducativo

# Directorio base del proyecto (donde se guardarán los reportes)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"

# Asegura que el directorio de reportes existe
REPORTS_DIR.mkdir(exist_ok=True)

def calcular_balance(db: Session, categoria: str = None, nivel: str = None, tipo_registro: str = None, fecha_inicio: datetime = None, fecha_fin: datetime = None) -> dict:
    """Calcula balance filtrado por categoría, nivel, tipo y rango de fechas."""
    try:
        query = db.query(Ingreso.monto).join(Persona, Ingreso.persona_id == Persona.id, isouter=True)
        if categoria:
            query = query.filter(Ingreso.categoria == categoria)
        if nivel:
            query = query.filter(Persona.nivel_educativo == nivel)
        if fecha_inicio:
            query = query.filter(Ingreso.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Ingreso.fecha <= fecha_fin)
        ingresos = query.all()
        total_ingresos = sum([i[0] for i in ingresos])

        query = db.query(Gasto.monto).join(Persona, Gasto.persona_id == Persona.id, isouter=True)
        if categoria:
            query = query.filter(Gasto.categoria == categoria)
        if nivel:
            query = query.filter(Persona.nivel_educativo == nivel)
        if fecha_inicio:
            query = query.filter(Gasto.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Gasto.fecha <= fecha_fin)
        gastos = query.all()
        total_gastos = sum([g[0] for g in gastos])

        balance = total_ingresos - total_gastos
        return {'ingresos': total_ingresos, 'gastos': total_gastos, 'balance': balance}
    except Exception as e:
        print(f"Error calculando balance: {e}")
        return {'ingresos': 0, 'gastos': 0, 'balance': 0}

def obtener_registros_filtrados(db: Session, tipo_registro: str, categoria: str = None, nivel: str = None, fecha_inicio: datetime = None, fecha_fin: datetime = None) -> list:
    """Obtiene registros filtrados para tabla o export."""
    try:
        if tipo_registro == 'Ingresos':
            query = db.query(Ingreso).join(Persona, Ingreso.persona_id == Persona.id, isouter=True)
        else:
            query = db.query(Gasto).join(Persona, Gasto.persona_id == Persona.id, isouter=True)
        
        if categoria:
            query = query.filter(Ingreso.categoria == categoria if tipo_registro == 'Ingresos' else Gasto.categoria == categoria)
        if nivel:
            query = query.filter(Persona.nivel_educativo == nivel)
        if fecha_inicio:
            query = query.filter(Ingreso.fecha >= fecha_inicio if tipo_registro == 'Ingresos' else Gasto.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Ingreso.fecha <= fecha_fin if tipo_registro == 'Ingresos' else Gasto.fecha <= fecha_fin)
        
        registros = query.order_by(Ingreso.fecha.desc() if tipo_registro == 'Ingresos' else Gasto.fecha.desc()).all()
        return [
            {
                'id': r.id,
                'concepto': r.concepto,
                'monto': r.monto,
                'categoria': r.categoria,
                'fecha': r.fecha,
                'persona': f"{r.persona.nombre} {r.persona.apellidos}" if r.persona else "General"
            } for r in registros
        ]
    except Exception as e:
        print(f"Error obteniendo registros: {e}")
        return []

def generar_reporte_pdf(db: Session, categoria: str = None, nivel: str = None, tipo_registro: str = None, fecha_inicio: datetime = None, fecha_fin: datetime = None, filename: str = None) -> str:
    """Genera PDF filtrado con tabla de registros."""
    try:
        if filename is None:
            filename = REPORTS_DIR / f"reporte_pebose_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        
        data = calcular_balance(db, categoria, nivel, tipo_registro, fecha_inicio, fecha_fin)
        registros = obtener_registros_filtrados(db, tipo_registro or 'Ingresos', categoria, nivel, fecha_inicio, fecha_fin)
        
        c = canvas.Canvas(str(filename), pagesize=letter)
        y = 750
        c.drawString(100, y, "Reporte Financiero PEBOSE")
        y -= 30
        c.drawString(100, y, f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        y -= 30
        if categoria:
            c.drawString(100, y, f"Categoría: {categoria}")
            y -= 20
        if nivel:
            c.drawString(100, y, f"Nivel Educativo: {nivel}")
            y -= 20
        if tipo_registro:
            c.drawString(100, y, f"Tipo: {tipo_registro}")
            y -= 20
        if fecha_inicio:
            c.drawString(100, y, f"Desde: {fecha_inicio.strftime('%d/%m/%Y')}")
            y -= 20
        if fecha_fin:
            c.drawString(100, y, f"Hasta: {fecha_fin.strftime('%d/%m/%Y')}")
            y -= 30
        
        c.drawString(100, y, f"Ingresos Total: {data['ingresos']:,.2f} FCFA")
        y -= 20
        c.drawString(100, y, f"Gastos Total: {data['gastos']:,.2f} FCFA")
        y -= 20
        c.drawString(100, y, f"Balance: {data['balance']:,.2f} FCFA")
        y -= 40
        
        # Tabla de registros
        c.drawString(100, y, "Registros Detallados:")
        y -= 20
        for i, reg in enumerate(registros[:20]):  # Limita a 20 para PDF
            if y < 100:  # Nueva página si es necesario
                c.showPage()
                y = 750
            c.drawString(100, y, f"ID {reg['id']}: {reg['concepto']} - {reg['monto']:,.2f} FCFA ({reg['categoria']}) - {reg['fecha'].strftime('%d/%m/%Y')} - {reg['persona']}")
            y -= 20
        
        c.save()
        return str(filename)
    except Exception as e:
        print(f"Error generando PDF: {e}")
        return None

def generar_reporte_excel(db: Session, categoria: str = None, nivel: str = None, tipo_registro: str = None, fecha_inicio: datetime = None, fecha_fin: datetime = None, filename: str = None) -> str:
    """Genera Excel filtrado con hojas de resumen y detalle."""
    try:
        if filename is None:
            filename = REPORTS_DIR / f"reporte_pebose_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        
        data = calcular_balance(db, categoria, nivel, tipo_registro, fecha_inicio, fecha_fin)
        registros = obtener_registros_filtrados(db, tipo_registro or 'Ingresos', categoria, nivel, fecha_inicio, fecha_fin)
        
        df_resumen = pd.DataFrame([{
            'Concepto': 'Resumen Financiero',
            'Ingresos Total (FCFA)': data['ingresos'],
            'Gastos Total (FCFA)': data['gastos'],
            'Balance (FCFA)': data['balance'],
            'Fecha Generación': datetime.now(),
            'Filtro Categoría': categoria or 'Todos',
            'Filtro Nivel': nivel or 'Todos',
            'Filtro Tipo': tipo_registro or 'Ingresos',
            'Fecha Inicio': fecha_inicio,
            'Fecha Fin': fecha_fin
        }])
        
        df_registros = pd.DataFrame(registros)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
            df_registros.to_excel(writer, sheet_name='Detalle', index=False)
        
        return str(filename)
    except Exception as e:
        print(f"Error generando Excel: {e}")
        return None

def generar_grafico_balance(db: Session, categoria: str = None, nivel: str = None, tipo_registro: str = None, fecha_inicio: datetime = None, fecha_fin: datetime = None, filename: str = None) -> str:
    """Genera gráfico filtrado (barras/pastel)."""
    try:
        if filename is None:
            filename = REPORTS_DIR / f"grafico_balance_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
        
        data = calcular_balance(db, categoria, nivel, tipo_registro, fecha_inicio, fecha_fin)
        registros = obtener_registros_filtrados(db, tipo_registro or 'Ingresos', categoria, nivel, fecha_inicio, fecha_fin)
        
        plt.figure(figsize=(12, 5))
        
        # Gráfico de barras (totales)
        plt.subplot(1, 2, 1)
        plt.bar(['Ingresos', 'Gastos'], [data['ingresos'], data['gastos']], color=['green', 'red'])
        plt.title(f'Balance Filtrado (Categoría: {categoria or "Todos"}, Nivel: {nivel or "Todos"})')
        plt.ylabel('FCFA')
        
        # Gráfico de pastel (distribución por categoría si hay registros)
        if registros:
            categorias = [r['categoria'] for r in registros]
            montos_cat = pd.Series(categorias).value_counts()
            plt.subplot(1, 2, 2)
            plt.pie(montos_cat.values, labels=montos_cat.index, autopct='%1.1f%%')
            plt.title('Distribución por Categoría')
        else:
            plt.subplot(1, 2, 2)
            plt.text(0.5, 0.5, 'Sin Registros', ha='center', va='center')
            plt.title('Distribución')
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        return str(filename)
    except Exception as e:
        print(f"Error generando gráfico: {e}")
        return None