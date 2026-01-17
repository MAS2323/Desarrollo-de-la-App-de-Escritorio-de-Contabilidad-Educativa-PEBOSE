import os

def create_structure(base_dir):
    dirs = [
        base_dir,
        os.path.join(base_dir, 'assets', 'icons'),
        os.path.join(base_dir, 'src', 'models'),
        os.path.join(base_dir, 'src', 'views'),
        os.path.join(base_dir, 'src', 'services'),
        os.path.join(base_dir, 'src', 'utils'),
        os.path.join(base_dir, 'tests')
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    
    # Crea __init__.py en paquetes
    init_files = [
        'src/__init__.py',
        'src/models/__init__.py',
        'src/views/__init__.py',
        'src/services/__init__.py',
        'src/utils/__init__.py',
        'tests/__init__.py'
    ]
    for f in init_files:
        open(os.path.join(base_dir, f), 'w').close()
    
    print(f"Estructura creada en {base_dir}")

if __name__ == "__main__":
    create_structure('contabilidad_pebose')