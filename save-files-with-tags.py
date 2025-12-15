import os
import argparse
import sys

def add_prefix_in_tree(root_dir, prefix):
    """
    Recorre recursivamente root_dir y añade prefix a archivos y directorios.
    """
    script_name = os.path.basename(sys.argv[0])

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == script_name:
                continue
            
            old_path = os.path.join(dirpath, filename)
            new_filename = f"{prefix}{filename}"
            new_path = os.path.join(dirpath, new_filename)
            
            try:
                os.rename(old_path, new_path)
                print(f'Renombrando archivo: {old_path} -> {new_path}')
            except OSError as e:
                print(f"Error al renombrar archivo {old_path}: {e}")

    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        for dirname in dirnames:
            old_dir = os.path.join(dirpath, dirname)
            new_dirname = f"{prefix}{dirname}"
            new_dir = os.path.join(dirpath, new_dirname)
            
            try:
                os.rename(old_dir, new_dir)
                print(f'Renombrando directorio: {old_dir} -> {new_dir}')
            except OSError as e:
                print(f"Error al renombrar directorio {old_dir}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Renombra recursivamente archivos y carpetas añadiendo un prefijo."
    )
    parser.add_argument("prefix", help="El prefijo (tag) a añadir al inicio de los nombres.")
    parser.add_argument("--path", default=os.path.dirname(os.path.abspath(__file__)), help="Ruta del directorio raíz (opcional). Por defecto es la carpeta actual.")
    
    args = parser.parse_args()
    
    print(f"Iniciando proceso en: {args.path}")
    print(f"Prefijo a usar: '{args.prefix}'")
    
    add_prefix_in_tree(args.path, args.prefix)
