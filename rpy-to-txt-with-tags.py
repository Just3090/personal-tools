import os
import os
import argparse
import sys

def rename_rpy_files_recursively(root_dir, prefix):
    """
    Recorre un directorio y sus subdirectorios para renombrar archivos .rpy a .txt,
    añadiendo un prefijo al nuevo nombre de archivo.

    Args:
        root_dir (str): La ruta del directorio raíz desde donde empezar a buscar.
        prefix (str): El prefijo que se añadirá al nombre de los archivos renombrados.
    """
    print(f"Iniciando la búsqueda de archivos .rpy en: '{root_dir}'")
    print(f"Se usará el prefijo: '{prefix}'\n")

    files_renamed_count = 0

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.rpy'):
                old_filepath = os.path.join(dirpath, filename)

                name_without_ext, _ = os.path.splitext(filename)

                new_filename = f"{prefix}{name_without_ext}.txt"

                new_filepath = os.path.join(dirpath, new_filename)

                try:
                    os.rename(old_filepath, new_filepath)
                    print(f"Renombrado: '{old_filepath}' -> '{new_filepath}'")
                    files_renamed_count += 1
                except OSError as e:
                    print(f"Error al renombrar el archivo '{old_filepath}': {e}", file=sys.stderr)

    print(f"\nProceso completado. Se renombraron {files_renamed_count} archivos.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Renombra archivos .rpy a .txt de forma recursiva, añadiendo un prefijo al nombre.",
        epilog="Ejemplo de uso: python rpt-to-txt-with-tags.py --prefix backup_"
    )
    parser.add_argument(
        "--prefix",
        type=str,
        required=True,
        help="Prefijo para añadir al nombre de los archivos de salida .txt"
    )
    args = parser.parse_args()

    start_directory = os.path.dirname(os.path.abspath(__file__))
    rename_rpy_files_recursively(start_directory, args.prefix)
