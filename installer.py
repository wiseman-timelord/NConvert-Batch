# script: installer.py
"""
NConvert-Batch Installer
Handles all installation requirements for NConvert-Batch application
"""
import os
import sys
import subprocess
import platform
import zipfile
import shutil
import urllib.request
import urllib.error
from pathlib import Path
import tempfile
import time
import json

# Global Constants
NCONVERT_URLS = {  # Download URLs for NConvert
    'x64': 'https://download.xnview.com/NConvert-win64.zip  ',
    'x32': 'https://download.xnview.com/NConvert-win.zip  '
}

# All application packages with pinned versions
INSTALL_PACKAGES = [
    "aiofiles==24.1.0",
    "annotated-doc==0.0.4",
    "annotated-types==0.7.0",
    "anyio==4.12.0",
    "autobuild==3.10.1",
    "backports.zstd==1.2.0",
    "brotli==1.2.0",
    "certifi==2025.11.12",
    "click==8.3.1",
    "colorama==0.4.6",
    "fastapi==0.124.4",
    "ffmpy==1.0.0",
    "filelock==3.20.1",
    "fsspec==2025.12.0",
    "gradio==5.49.1",
    "gradio_client==1.13.3",
    "groovy==0.1.2",
    "h11==0.16.0",
    "hf-xet==1.2.0",
    "httpcore==1.0.9",
    "httpx==0.28.1",
    "huggingface_hub==1.2.3",
    "idna==3.11",
    "Jinja2==3.1.6",
    "llsd==1.2.4",
    "markdown-it-py==4.0.0",
    "MarkupSafe==3.0.3",
    "mdurl==0.1.2",
    "numpy==1.26.0",
    "orjson==3.11.5",
    "packaging==25.0",
    "pandas==2.1.3",
    "pillow==11.3.0",
    "psutil==5.9.4",
    "pydantic==2.11.10",
    "pydantic_core==2.33.2",
    "pydot==4.0.1",
    "pydub==0.25.1",
    "Pygments==2.19.2",
    "pyparsing==3.2.5",
    "python-dateutil==2.9.0.post0",
    "python-multipart==0.0.20",
    "pytz==2025.2",
    "PyYAML==6.0.3",
    "pyzstd==0.19.1",
    "rich==14.2.0",
    "ruff==0.14.9",
    "safehttpx==0.1.7",
    "semantic-version==2.10.0",
    "shellingham==1.5.4",
    "six==1.17.0",
    "starlette==0.50.0",
    "tomlkit==0.13.3",
    "tqdm==4.67.1",
    "typer==0.20.0",
    "typer-slim==0.20.0",
    "typing_extensions==4.15.0",
    "typing-inspection==0.4.2",
    "tzdata==2025.3",
    "uvicorn==0.38.0",
    "websockets==15.0.1"
]

# Critical packages for verification (subset of installed packages)
CRITICAL_PACKAGES = ['gradio', 'pandas', 'numpy', 'psutil']

PACKAGE_IMPORT_MAP = {  # Map package names to import names for verification
    'gradio': 'gradio',
    'pandas': 'pandas',
    'numpy': 'numpy',
    'psutil': 'psutil'
}

MIN_PYTHON_VERSION = (3, 8)  # Minimum required Python version
SEPARATOR_LENGTH = 60
HEADER_CHAR = "="
SEPARATOR_CHAR = "-"
MAX_RETRIES = 3
RETRY_DELAY = 2

# Default settings for persistent.json
DEFAULT_SESSION = {
    "last_folder": str(Path(__file__).parent.resolve() / "temp"),
    "last_from": "PSPIMAGE",
    "last_to": "JPEG",
    "last_delete": False,
    "beep_on_complete": False
}

class NConvertInstaller:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.nconvert_exe = self.script_dir / "nconvert.exe"
        self.data_dir = self.script_dir / "data"
        self.session_file = self.data_dir / "persistent.json"
        self.workspace_dir = self.script_dir / "temp"

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title, char=None, length=None):
        char = char or HEADER_CHAR
        length = length or SEPARATOR_LENGTH
        separator = char * length
        print(f"\n{separator}")
        print(f"    {title}")
        print(f"{separator}\n")

    def print_separator(self, char=None, length=None):
        char = char or SEPARATOR_CHAR
        length = length or SEPARATOR_LENGTH
        print(char * length)

    def print_status(self, message, success=True):
        symbol = "✓" if success else "✗"
        print(f"{symbol} {message}")

    def check_python_version(self):
        current_version = sys.version_info[:2]
        if current_version < MIN_PYTHON_VERSION:
            self.print_status(
                f"Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+ required, "
                f"found {current_version[0]}.{current_version[1]}",
                success=False
            )
            return False
        self.print_status(f"Python {current_version[0]}.{current_version[1]} detected")
        return True

    def detect_architecture(self):
        machine = platform.machine().lower()
        architecture = platform.architecture()[0]
        if machine in ['amd64', 'x86_64'] or architecture == '64bit':
            detected = 'x64'
        elif machine in ['i386', 'i686', 'x86'] or architecture == '32bit':
            detected = 'x32'
        else:
            detected = 'x64'  # default assumption
        print(f"Detected architecture: {detected} (machine: {machine}, arch: {architecture})")
        return detected

    def prompt_architecture(self):
        detected = self.detect_architecture()
        while True:
            print(f"\nArchitecture options:")
            print(f"  1) x64 (64-bit) {'[Detected]' if detected == 'x64' else ''}")
            print(f"  2) x32 (32-bit) {'[Detected]' if detected == 'x32' else ''}")
            choice = input(f"Select architecture (1/2, Enter for detected [{detected}]): ").strip()
            if choice == "" or choice == "1":
                return 'x64'
            elif choice == "2":
                return 'x32'
            else:
                print("Invalid selection. Please enter 1, 2, or press Enter.")

    def create_workspace(self):
        try:
            self.workspace_dir.mkdir(exist_ok=True)
            self.print_status(f"Workspace directory ready: {self.workspace_dir}")
            return True
        except Exception as e:
            self.print_status(f"Failed to create workspace directory: {e}", success=False)
            return False

    def download_file(self, url, destination):
        retry_count = 0
        downloaded_bytes = 0
        if destination.exists():
            downloaded_bytes = destination.stat().st_size
            print(f"Resuming download at: {downloaded_bytes/(1024*1024):.1f}MB")
        
        while retry_count < MAX_RETRIES:
            try:
                req = urllib.request.Request(url)
                if downloaded_bytes > 0:
                    req.add_header("Range", f"bytes={downloaded_bytes}-")
                print(f"Download attempt {retry_count + 1}/{MAX_RETRIES}")
                start_time = time.time()
                with urllib.request.urlopen(req) as response:
                    total_size = int(response.getheader('Content-Length', 0)) + downloaded_bytes
                    with open(destination, 'ab' if downloaded_bytes > 0 else 'wb') as f:
                        while True:
                            chunk = response.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded_bytes += len(chunk)
                            if total_size > 0:
                                percent = (downloaded_bytes * 100) // total_size
                                mb_downloaded = downloaded_bytes / (1024 * 1024)
                                print(f"\rProgress: {percent}% ({mb_downloaded:.1f}MB)", end='')
                print()  # newline after progress
                return True
            except Exception as e:
                print(f"Download error: {e}")
                retry_count += 1
                if retry_count < MAX_RETRIES:
                    print(f"Retrying in {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY)
        return False

    def extract_zip(self, zip_path, extract_to):
        try:
            print(f"Extracting: {zip_path.name}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                if zip_ref.testzip() is not None:
                    self.print_status("Corrupted ZIP file", success=False)
                    return False
                zip_ref.extractall(extract_to)
            self.print_status("Extraction completed")
            return True
        except Exception as e:
            self.print_status(f"Extraction error: {e}", success=False)
            return False

    def move_nconvert_files(self, source_dir):
        nconvert_dir = source_dir / "NConvert"
        if not nconvert_dir.exists():
            self.print_status("NConvert directory not found in extracted files", success=False)
            return False
        try:
            moved_count = 0
            for item in nconvert_dir.iterdir():
                destination = self.script_dir / item.name
                if destination.exists():
                    if destination.is_file():
                        destination.unlink()
                    else:
                        shutil.rmtree(destination)
                shutil.move(str(item), str(destination))
                moved_count += 1
                print(f"Moved: {item.name}")
            if nconvert_dir.exists():
                nconvert_dir.rmdir()
            self.print_status(f"Moved {moved_count} items successfully")
            return True
        except Exception as e:
            self.print_status(f"Error moving files: {e}", success=False)
            return False

    def install_nconvert(self):
        if self.nconvert_exe.exists():
            self.print_status("nconvert.exe already exists")
            return True
        
        print("NConvert executable not found, starting download...")
        architecture = self.prompt_architecture()
        url = NCONVERT_URLS[architecture]
        zip_name = f"NConvert-win{'64' if architecture == 'x64' else ''}.zip"
        zip_path = tempfile.NamedTemporaryFile(suffix='.zip', delete=False).name
        zip_path = Path(zip_path)

        if not self.download_file(url, zip_path):
            zip_path.unlink(missing_ok=True)
            return False

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            if not self.extract_zip(zip_path, temp_path):
                zip_path.unlink(missing_ok=True)
                return False
            if not self.move_nconvert_files(temp_path):
                zip_path.unlink(missing_ok=True)
                return False

        zip_path.unlink(missing_ok=True)
        
        if self.nconvert_exe.exists():
            self.print_status("NConvert installation completed")
            return True
        else:
            self.print_status("nconvert.exe not found after installation", success=False)
            return False

    def install_python_packages(self):
        print("\nUpgrading build tools (pip, setuptools) to latest...")
        build_tools = ["pip", "setuptools"]
        for tool in build_tools:
            print(f"→ Upgrading {tool} to latest version...")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--upgrade', tool],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                self.print_status(f"{tool} upgraded successfully")
            else:
                self.print_status(f"Failed to upgrade {tool}", success=False)
                if result.stderr:
                    print(result.stderr.strip())
                return False

        print("\nInstalling pinned application packages...")
        # Create temporary requirements file for pinned dependencies
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as req_file:
            req_file.write("\n".join(INSTALL_PACKAGES))
            req_file_path = Path(req_file.name)

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', str(req_file_path)],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                self.print_status("All application packages installed successfully")
                return True
            else:
                self.print_status("Failed to install application packages", success=False)
                if result.stderr:
                    print(result.stderr.strip())
                return False
        finally:
            req_file_path.unlink(missing_ok=True)

    def create_default_session_file(self):
        try:
            self.data_dir.mkdir(exist_ok=True)
            self.session_file.write_text(
                json.dumps(DEFAULT_SESSION, indent=2),
                encoding="utf-8"
            )
            self.print_status(f"Default persistent config created: data/persistent.json")
            return True
        except Exception as e:
            self.print_status(f"Could not create persistent config: {e}", success=False)
            return False

    def verify_installation(self):
        print("\nVerifying critical components...")
        all_good = True

        if self.nconvert_exe.exists():
            self.print_status("nconvert.exe found")
        else:
            self.print_status("nconvert.exe missing", success=False)
            all_good = False

        for package_name in CRITICAL_PACKAGES:
            import_name = PACKAGE_IMPORT_MAP.get(package_name, package_name.replace('-', '_'))
            try:
                subprocess.run(
                    [sys.executable, '-c', f'import {import_name}; print("{import_name} OK")'],
                    capture_output=True, text=True, timeout=8, check=True
                )
                self.print_status(f"{package_name} available")
            except Exception as e:
                self.print_status(f"{package_name} verification failed: {str(e)}", success=False)
                all_good = False

        if all_good:
            self.print_status("All critical components verified successfully")
        else:
            self.print_status("Some critical components failed verification", success=False)
        
        return all_good

    def run_installation(self):
        self.clear_screen()
        self.print_header("NConvert-Batch Installer")

        if not self.check_python_version():
            return False

        if not self.create_workspace():
            return False

        if not self.install_nconvert():
            return False

        if not self.install_python_packages():
            return False

        if not self.create_default_session_file():
            return False

        success = self.verify_installation()

        print("\n" + "=" * SEPARATOR_LENGTH)
        if success:
            print("✓ Installation completed successfully!")
            print("\nYou can now run NConvert-Batch.bat")
        else:
            print("✗ Installation encountered issues")
            print("Please review the messages above")

        return success


def main():
    installer = NConvertInstaller()
    try:
        success = installer.run_installation()
        print("\nPress Enter to exit...")
        input()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 60)
        print("Unexpected error during installation:")
        print(str(e))
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)


if __name__ == "__main__":
    main()