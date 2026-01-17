import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../db_local.sqlite'))
API_URL = 'https://tu-api-pebose.render.com/sync'  # Cambia por tu endpoint real
CURRENCY = 'FCFA'
LOGO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../assets/logo_pebose.png'))