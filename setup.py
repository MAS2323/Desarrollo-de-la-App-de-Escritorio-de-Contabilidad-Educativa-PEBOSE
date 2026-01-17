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
    print(f"Estructura creada en {base_dir}")

create_structure('contabilidad_pebose')