import os
import argparse
import sys

def remove_relative_duplicates(reference_dir: str, target_dir: str, dry_run: bool = False) -> None:
    """
    Traverses the reference directory to identify files. Checks if a file with the 
    same relative path exists in the target directory and deletes it.

    Args:
        reference_dir (str): The path to the source folder (folder1).
        target_dir (str): The path to the folder to be cleaned (folder2).
        dry_run (bool): If True, simulates the deletion without executing it.
    """
    
    if not os.path.isdir(reference_dir):
        print(f"[ERROR] Reference directory not found: {reference_dir}")
        return
    if not os.path.isdir(target_dir):
        print(f"[ERROR] Target directory not found: {target_dir}")
        return

    print(f"[INFO] Starting scan using Reference: '{reference_dir}' -> Target: '{target_dir}'")
    
    files_deleted_count = 0

    for root, _, files in os.walk(reference_dir):
        for filename in files:
            source_file_abs_path = os.path.join(root, filename)

            # Example: If root is "folder1/test256/" and file is "hola.png",
            # relative_path becomes "test256/hola.png"
            relative_path = os.path.relpath(source_file_abs_path, reference_dir)

            target_file_abs_path = os.path.join(target_dir, relative_path)

            if os.path.exists(target_file_abs_path) and os.path.isfile(target_file_abs_path):
                try:
                    if not dry_run:
                        os.remove(target_file_abs_path)
                        print(f"[DELETED] {relative_path}")
                    else:
                        print(f"[DRY-RUN] Would delete: {relative_path}")
                    
                    files_deleted_count += 1
                
                except OSError as e:
                    print(f"[ERROR] Failed to delete {target_file_abs_path}. Reason: {e}")

    status = "Simulated deletion of" if dry_run else "Deleted"
    print("-" * 40)
    print(f"[INFO] Process complete. {status} {files_deleted_count} files.")

if __name__ == "__main__":
    # Argument parsing configuration
    parser = argparse.ArgumentParser(
        description="Recursively deletes files in target_dir that exist in reference_dir with the same relative path."
    )
    
    parser.add_argument("folder1", help="Reference source folder (files here are kept).")
    parser.add_argument("folder2", help="Target folder (duplicates here are deleted).")
    parser.add_argument("--dry-run", action="store_true", help="Simulate the process without deleting files.")

    args = parser.parse_args()

    remove_relative_duplicates(args.folder1, args.folder2, args.dry_run)
