#!/usr/bin/env python3
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
import json   # NEW

# Global Constants
NCONVERT_URLS = {  # Download URLs for NConvert
    'x64': 'https://download.xnview.com/NConvert-win64.zip',
    'x32': 'https://download.xnview.com/NConvert-win.zip'
}

REQUIRED_PACKAGES = [  # Python packages to install
    'gradio',
    'pandas==2.1.3',
    'numpy==1.26.0',
    'psutil==5.9.4'
]

PACKAGE_IMPORT_MAP = {  # Map package names to import names
    'gradio': 'gradio',
    'pandas': 'pandas',
    'numpy': 'numpy',
    'psutil': 'psutil'
}

MIN_PYTHON_VERSION = (3, 8)  # Minimum required Python version
SEPARATOR_LENGTH = 60  # Length of separator lines
HEADER_CHAR = "="  # Character for headers
SEPARATOR_CHAR = "-"  # Character for separators
MAX_RETRIES = 3  # Maximum download retry attempts
RETRY_DELAY = 2  # Seconds between retries

# NEW: default settings for last_session.json
DEFAULT_SESSION = {
    "last_folder": str(Path(__file__).parent.resolve() / "workspace"),
    "last_from": "PSPIMAGE",
    "last_to": "JPEG"
}

class NConvertInstaller:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.data_dir = self.script_dir / "data"
        self.nconvert_exe = self.script_dir / "nconvert.exe"
        self.session_file = self.script_dir / "last_session.json"   # NEW

    # -------------------- existing helpers unchanged --------------------
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
            detected = 'x64'
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

    def create_directories(self):
        try:
            self.data_dir.mkdir(exist_ok=True)
            self.print_status(f"Data directory ready: {self.data_dir}")
            return True
        except PermissionError:
            self.print_status("Permission denied creating data directory", success=False)
            return False
        except Exception as e:
            self.print_status(f"Error creating directories: {e}", success=False)
            return False

    # -------------------- download / extract helpers unchanged --------------------
    def download_file(self, url, destination):
        retry_count = 0
        downloaded_bytes = 0
        total_size = 0
        last_valid_position = 0
        if destination.exists():
            downloaded_bytes = destination.stat().st_size
            print(f"Resuming download at: {downloaded_bytes/(1024*1024):.1f}MB")
            last_valid_position = downloaded_bytes
        while retry_count < MAX_RETRIES:
            try:
                req = urllib.request.Request(url)
                if downloaded_bytes > 0:
                    req.add_header("Range", f"bytes={downloaded_bytes}-")
                print(f"Download attempt {retry_count + 1}/{MAX_RETRIES}")
                start_time = time.time()
                with urllib.request.urlopen(req) as response:
                    content_range = response.getheader('Content-Range')
                    if content_range:
                        total_size = int(content_range.split('/')[-1])
                    else:
                        total_size = int(response.getheader('Content-Length', 0)) + downloaded_bytes
                    if downloaded_bytes > 0 and content_range is None:
                        print("Server doesn't support resume - restarting")
                        downloaded_bytes = 0
                        last_valid_position = 0
                        mode = 'wb'
                    else:
                        mode = 'ab' if downloaded_bytes > 0 else 'wb'
                    with open(destination, mode) as f:
                        while True:
                            chunk = response.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded_bytes += len(chunk)
                            last_valid_position = downloaded_bytes
                            if total_size > 0:
                                percent = (downloaded_bytes * 100) // total_size
                                mb_downloaded = downloaded_bytes / (1024 * 1024)
                                print(f"\rProgress: {percent}% ({mb_downloaded:.1f}MB)", end='')
                    elapsed = time.time() - start_time
                    speed = (downloaded_bytes / (1024 * 1024)) / max(elapsed, 1)
                    print(f"\nDownload complete: {speed:.1f}MB/s")
                    try:
                        with zipfile.ZipFile(destination, 'r') as zip_ref:
                            if zip_ref.testzip() is not None:
                                print("ZIP verification failed - retrying")
                                raise zipfile.BadZipFile("Corrupted download")
                        return True
                    except zipfile.BadZipFile:
                        print("Download corrupted - bad ZIP file")
                        raise
            except urllib.error.HTTPError as e:
                print(f"HTTP error: {e.code}")
                if e.code == 416:
                    destination.unlink(missing_ok=True)
                    downloaded_bytes = 0
                    last_valid_position = 0
            except (urllib.error.URLError, ConnectionResetError, TimeoutError) as e:
                print(f"Network error: {e}")
            except zipfile.BadZipFile:
                print("Invalid ZIP structure - retrying")
            except Exception as e:
                print(f"Download error: {e}")
            if destination.exists():
                if downloaded_bytes != last_valid_position:
                    try:
                        destination.truncate(last_valid_position)
                        downloaded_bytes = last_valid_position
                        print(f"Rolled back to last valid position: {last_valid_position} bytes")
                    except Exception as e:
                        print(f"Failed to truncate file: {e}")
                        destination.unlink(missing_ok=True)
                        downloaded_bytes = 0
                        last_valid_position = 0
            retry_count += 1
            if retry_count < MAX_RETRIES:
                print(f"Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
                continue
        print("Max retries reached")
        return False

    def extract_zip(self, zip_path, extract_to):
        try:
            print(f"Extracting: {zip_path.name}")
            if not zip_path.exists():
                self.print_status("ZIP file does not exist", success=False)
                return False
            if zip_path.stat().st_size == 0:
                self.print_status("ZIP file is empty", success=False)
                return False
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                bad_file = zip_ref.testzip()
                if bad_file:
                    self.print_status(f"Corrupted file in ZIP: {bad_file}", success=False)
                    return False
                zip_ref.extractall(extract_to)
            self.print_status("Extraction completed")
            return True
        except zipfile.BadZipFile:
            self.print_status("Invalid or corrupted ZIP file", success=False)
            return False
        except PermissionError:
            self.print_status("Permission denied during extraction", success=False)
            return False
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
                    print(f"Replaced existing: {item.name}")
                shutil.move(str(item), str(destination))
                moved_count += 1
                print(f"Moved: {item.name}")
            if nconvert_dir.exists():
                nconvert_dir.rmdir()
            self.print_status(f"Moved {moved_count} items successfully")
            return True
        except PermissionError as e:
            self.print_status(f"Permission denied moving files: {e}", success=False)
            return False
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
        zip_path = self.data_dir / zip_name
        if zip_path.exists():
            zip_path.unlink()
        if not self.download_file(url, zip_path):
            if zip_path.exists():
                zip_path.unlink()
            return False
        try:
            print("Verifying download integrity...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                if zip_ref.testzip() is not None:
                    self.print_status("Download corrupted - bad ZIP file", success=False)
                    zip_path.unlink()
                    return False
        except zipfile.BadZipFile:
            self.print_status("Invalid ZIP file - download may be incomplete", success=False)
            zip_path.unlink()
            return False
        except Exception as e:
            self.print_status(f"ZIP verification failed: {e}", success=False)
            zip_path.unlink()
            return False
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            if not self.extract_zip(zip_path, temp_path):
                zip_path.unlink(missing_ok=True)
                return False
            if not self.move_nconvert_files(temp_path):
                return False
        zip_path.unlink(missing_ok=True)
        if self.nconvert_exe.exists():
            self.print_status("NConvert installation completed")
            return True
        else:
            self.print_status("nconvert.exe not found after installation", success=False)
            return False

    def create_requirements_file(self):
        try:
            requirements_path = self.data_dir / "requirements.txt"
            with open(requirements_path, 'w', encoding='utf-8') as f:
                for package in REQUIRED_PACKAGES:
                    f.write(f"{package}\n")
            self.print_status(f"Requirements file created: {requirements_path.name}")
            return requirements_path
        except PermissionError:
            self.print_status("Permission denied creating requirements file", success=False)
            return None
        except Exception as e:
            self.print_status(f"Error creating requirements file: {e}", success=False)
            return None

    def install_python_packages(self, requirements_path):
        try:
            print("Installing Python packages...")
            print("Upgrading pip...")
            pip_upgrade = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
            ], capture_output=True, text=True)
            if pip_upgrade.returncode != 0:
                print("Warning: Could not upgrade pip")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_path)
            ], capture_output=True, text=True)
            if result.returncode == 0:
                self.print_status("Python packages installed successfully")
                if result.stdout:
                    print("\nInstallation output:")
                    print(result.stdout)
                return True
            else:
                self.print_status("Package installation failed", success=False)
                if result.stderr:
                    print("Error details:")
                    print(result.stderr)
                return False
        except FileNotFoundError:
            self.print_status("pip not found - Python installation may be incomplete", success=False)
            return False
        except Exception as e:
            self.print_status(f"Error during package installation: {e}", success=False)
            return False

    # -------------------- NEW: create / overwrite session file --------------------
    def create_default_session_file(self):
        try:
            self.session_file.write_text(
                json.dumps(DEFAULT_SESSION, indent=2),
                encoding="utf-8"
            )
            self.print_status(f"Default session file created: {self.session_file.name}")
            return True
        except Exception as e:
            self.print_status(f"Could not create session file: {e}", success=False)
            return False

    # -------------------- verify installation unchanged --------------------
    def verify_installation(self):
        print("\nVerifying installation...")
        all_good = True
        if self.nconvert_exe.exists():
            self.print_status("nconvert.exe found")
        else:
            self.print_status("nconvert.exe missing", success=False)
            all_good = False
        for package in REQUIRED_PACKAGES:
            package_name = package.split('==')[0]
            import_name = PACKAGE_IMPORT_MAP.get(package_name, package_name.replace('-', '_'))
            try:
                result = subprocess.run([
                    sys.executable, '-c', f'import {import_name}; print("{import_name} OK")'
                ], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.print_status(f"{package_name} available")
                else:
                    self.print_status(f"{package_name} not importable", success=False)
                    all_good = False
            except subprocess.TimeoutExpired:
                self.print_status(f"{package_name} import timeout", success=False)
                all_good = False
            except Exception as e:
                self.print_status(f"Could not verify {package_name}: {e}", success=False)
                all_good = False
        if all_good:
            self.print_status("All components verified successfully")
        else:
            self.print_status("Some components failed verification", success=False)
        return all_good

    # -------------------- main installation flow --------------------
    def run_installation(self):
        self.clear_screen()
        self.print_header("NConvert-Batch Installer")
        if not self.check_python_version():
            return False
        if not self.create_directories():
            return False
        if not self.install_nconvert():
            return False
        requirements_path = self.create_requirements_file()
        if not requirements_path:
            return False
        if not self.install_python_packages(requirements_path):
            return False
        # NEW: always create / overwrite session file
        if not self.create_default_session_file():
            return False
        success = self.verify_installation()
        if success:
            print("    Installation Completed Successfully")
        else:
            print("    Installation Issues Detected")
            print("Please review the errors above and try again.")
        return success

def main():
    installer = NConvertInstaller()
    try:
        success = installer.run_installation()
        print(f"\n{'='*SEPARATOR_LENGTH}")
        if success:
            print("✓ Installation completed successfully!")
        else:
            print("✗ Installation encountered errors!")
        print("Press Enter to exit...")
        input()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        installer.print_header("Unexpected Error")
        print(f"An unexpected error occurred: {e}")
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)

if __name__ == "__main__":
    main()