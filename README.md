# Contabilidad PEBOSE

Aplicación de escritorio en Python para gestionar la contabilidad del Colegio Privado PEBOSE (Malabo, GQ). Funciona offline con SQLite y sincroniza online con cloud.

## Instalación

1. Clona o crea la estructura.
2. `pip install -r requirements.txt`
3. `python src/main.py`

## Estructura

- src/: Código fuente modular.
- assets/: Imágenes y recursos.
- db_local.sqlite: DB local.

## Features

- CRUD ingresos/gastos (matrículas, salarios).
- Reportes PDF/Excel con balances.
- Sync offline-online (futuro).

Desarrollado con Flet (GUI), SQLAlchemy (DB), Pandas (análisis).
