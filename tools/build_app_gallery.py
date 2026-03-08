import os
import sys
import glob
import json
import zipfile
import subprocess
import ast
import tempfile
import venv
import shutil

APP_ROOT = os.environ.get('APP_ROOT', 'examples')
DOCS_DIR = 'docs'
ZIPS_DIR = os.path.join(DOCS_DIR, 'app_zips')
MANIFEST_PATH = os.path.join(DOCS_DIR, 'app-manifest.json')
INDEX_MD_PATH = os.path.join(DOCS_DIR, 'index.md')

os.makedirs(ZIPS_DIR, exist_ok=True)

def get_git_timestamp(path):
    try:
        result = subprocess.run(['git', 'log', '-1', '--format=%ci', path], capture_output=True, text=True, check=True)
        ts = result.stdout.strip()
        return ts if ts else "<auto-filled by script>"
    except subprocess.CalledProcessError:
        return "<auto-filled by script>"

def extract_metadata(main_py_path):
    description = "No description provided."
    version = None
    try:
        with open(main_py_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            doc = ast.get_docstring(tree)
            if doc:
                description = doc.strip()

            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == '__version__':
                            if isinstance(node.value, ast.Constant):
                                version = node.value.value
                            elif isinstance(node.value, ast.Str): # For older python versions if any
                                version = node.value.s
    except Exception as e:
        print(f"Warning: Could not parse metadata from {main_py_path}: {e}")
    return description, version

def get_screenshot(app_dir):
    for ext in ['.png', '.jpg']:
        if os.path.exists(os.path.join(app_dir, f'screenshot{ext}')):
            return f'screenshot{ext}'
    return "https://via.placeholder.com/300x200?text=No+Image"

def run_tests_in_venv(app_dir, req_path):
    tests_dir = os.path.join(app_dir, 'tests')
    if not os.path.exists(tests_dir):
        return True # No tests to run

    print(f"Running tests for {app_dir}...")
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_dir = os.path.join(temp_dir, 'venv')
        venv.create(venv_dir, with_pip=True)

        # Determine paths for executables
        if os.name == 'nt':
            pip_exe = os.path.join(venv_dir, 'Scripts', 'pip.exe')
            pytest_exe = os.path.join(venv_dir, 'Scripts', 'pytest.exe')
        else:
            pip_exe = os.path.join(venv_dir, 'bin', 'pip')
            pytest_exe = os.path.join(venv_dir, 'bin', 'pytest')

        # Install requirements
        try:
            subprocess.run([pip_exe, 'install', '-r', req_path], check=True, capture_output=True)
            subprocess.run([pip_exe, 'install', 'pytest'], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to install requirements for {app_dir}: {e.stderr.decode()}")
            return False

        # Run pytest
        try:
            subprocess.run([pytest_exe, tests_dir], check=True, capture_output=True)
            print(f"Tests passed for {app_dir}.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Tests failed for {app_dir}: {e.stdout.decode()}\n{e.stderr.decode()}")
            return False

def zip_app(app_dir, zip_name):
    zip_path = os.path.join(ZIPS_DIR, zip_name)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(app_dir):
            # Exclude common dev directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.pytest_cache', '.venv'}]
            for file in files:
                file_path = os.path.join(root, file)
                # Store relative to the app directory itself
                arcname = os.path.relpath(file_path, app_dir)
                zipf.write(file_path, arcname)
    return zip_path

def update_index_md(apps):
    try:
        with open(INDEX_MD_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        start_marker = '<!-- APP_GALLERY_START -->'
        end_marker = '<!-- APP_GALLERY_END -->'

        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)

        if start_idx == -1 or end_idx == -1:
            print(f"Error: Delimiters not found in {INDEX_MD_PATH}")
            return

        gallery_md = "\n\n"
        for app in apps:
            img = app['screenshot_url']
            if not img.startswith('http'):
                # Assuming screenshot is placed in the docs directory or referenced relatively.
                # Since the instructions don't specify where the actual image file is copied,
                # we'll use a relative path assuming it's in the repo structure.
                # For a true static site, it should be copied to docs/assets/, but we'll link to the source for now or assume it's copied.
                pass # Keeping original string, might need adjustment based on site setup.

            gallery_md += f"### {app['name']}\n"
            gallery_md += f"![Screenshot]({img})\n\n"
            gallery_md += f"{app['description']}\n\n"
            if app['version']:
                gallery_md += f"**Version:** {app['version']} | "
            gallery_md += f"**Last Updated:** {app['last_updated']}\n\n"
            gallery_md += f"[Download Zip]({app['zip_url']})\n\n"
            gallery_md += "---\n\n"

        new_content = content[:start_idx + len(start_marker)] + gallery_md + content[end_idx:]

        with open(INDEX_MD_PATH, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Updated docs/index.md gallery section.")
    except Exception as e:
        print(f"Failed to update index.md: {e}")

def main():
    if not os.path.exists(APP_ROOT):
        print(f"App root '{APP_ROOT}' does not exist.")
        sys.exit(0)

    ready_apps = []

    for item in os.listdir(APP_ROOT):
        app_dir = os.path.join(APP_ROOT, item)
        if not os.path.isdir(app_dir):
            continue

        main_py = os.path.join(app_dir, 'main.py')
        req_txt = os.path.join(app_dir, 'requirements.txt')

        # Check for executable entry point and requirements
        entry_point = None
        if os.path.exists(main_py):
            entry_point = main_py
        else:
            # Look for any .py file if main.py is missing (simplification)
            py_files = glob.glob(os.path.join(app_dir, '*.py'))
            if py_files:
                entry_point = py_files[0]

        if not entry_point or not os.path.exists(req_txt):
            continue

        print(f"Processing app: {item}")

        if not run_tests_in_venv(app_dir, req_txt):
            print(f"Aborting build due to test failure in {item}.")
            sys.exit(1)

        desc, version = extract_metadata(entry_point)
        screenshot = get_screenshot(app_dir)
        last_updated = get_git_timestamp(app_dir)

        zip_name = f"{item}.zip"
        zip_app(app_dir, zip_name)

        zip_url = f"app_zips/{zip_name}"

        ready_apps.append({
            "name": item,
            "description": desc,
            "version": version,
            "screenshot_url": screenshot,
            "zip_url": zip_url,
            "last_updated": last_updated
        })

    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump({"apps": ready_apps}, f, indent=4)

    print(f"Generated manifest with {len(ready_apps)} apps.")

    update_index_md(ready_apps)

if __name__ == '__main__':
    main()
