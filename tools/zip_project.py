"""
Zips the entire project directory into a distributable archive for enterprise deployment or sharing.
"""
import os
import zipfile

def create_archive(output_filename: str = "jules_sandbox.zip"):
    """Creates a zip archive of the current directory, ignoring unnecessary files."""
    exclude_dirs = {'.git', '.venv', '__pycache__', '.pytest_cache', '.ruff_cache'}
    exclude_files = {output_filename, '.DS_Store'}

    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if file in exclude_files:
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                zipf.write(file_path, arcname)

if __name__ == "__main__":
    import sys
    output = sys.argv[1] if len(sys.argv) > 1 else "jules_sandbox.zip"
    create_archive(output)
    print(f"Project successfully archived to {output}")
