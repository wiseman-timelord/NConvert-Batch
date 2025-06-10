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

# Global Constants
NCONVERT_URLS = {  # Download URLs for NConvert
    'x64': 'https://download.xnview.com/NConvert-win64.zip',
    'x32': 'https://download.xnview.com/NConvert-win.zip'
}

REQUIRED_PACKAGES = [  # Python packages to install
    'gradio',
    'pandas==2.1.3', 
    'numpy==1.26.0',
    'psutil==6.1.1'
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


class NConvertInstaller:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.data_dir = self.script_dir / "data"
        self.nconvert_exe = self.script_dir / "nconvert.exe"
        
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self, title, char=None, length=None):
        """Print a formatted header with customizable character and length"""
        char = char or HEADER_CHAR
        length = length or SEPARATOR_LENGTH
        separator = char * length
        print(f"\n{separator}")
        print(f"    {title}")
        print(f"{separator}\n")
        
    def print_separator(self, char=None, length=None):
        """Print a separator line with customizable character and length"""
        char = char or SEPARATOR_CHAR
        length = length or SEPARATOR_LENGTH
        print(char * length)
        
    def print_status(self, message, success=True):
        """Print a status message with checkmark or X"""
        symbol = "V" if success else "X"
        print(f"{symbol} {message}")
        
    def check_python_version(self):
        """Check if Python version meets minimum requirements"""
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
        """Detect system architecture with improved logic"""
        machine = platform.machine().lower()
        architecture = platform.architecture()[0]
        
        # Check both machine type and architecture
        if machine in ['amd64', 'x86_64'] or architecture == '64bit':
            detected = 'x64'
        elif machine in ['i386', 'i686', 'x86'] or architecture == '32bit':
            detected = 'x32'
        else:
            # Default to x64 for unknown architectures on modern systems
            detected = 'x64'
            
        print(f"Detected architecture: {detected} (machine: {machine}, arch: {architecture})")
        return detected
            
    def prompt_architecture(self):
        """Prompt user to confirm or override architecture detection"""
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
        """Create necessary directories with error handling"""
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
            
    def download_file(self, url, destination):
        """Download file with improved progress display and error handling"""
        try:
            print(f"Downloading: {url}")
            print(f"Destination: {destination}")
            
            start_time = time.time()
            last_update = 0
            
            def progress_hook(block_num, block_size, total_size):
                nonlocal last_update
                current_time = time.time()
                
                if total_size > 0 and (current_time - last_update) >= 0.5:  # Update every 0.5 seconds
                    downloaded = min(block_num * block_size, total_size)
                    percent = (downloaded * 100) // total_size
                    mb_downloaded = downloaded / (1024 * 1024)
                    mb_total = total_size / (1024 * 1024)
                    
                    print(f"\rProgress: {percent:3d}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", 
                          end='', flush=True)
                    last_update = current_time
                    
            urllib.request.urlretrieve(url, destination, progress_hook)
            
            elapsed = time.time() - start_time
            file_size = destination.stat().st_size / (1024 * 1024)
            print(f"\nDownload completed in {elapsed:.1f}s ({file_size:.1f} MB)")
            return True
            
        except urllib.error.HTTPError as e:
            print(f"\nHTTP Error {e.code}: {e.reason}")
            return False
        except urllib.error.URLError as e:
            print(f"\nNetwork Error: {e.reason}")
            return False
        except Exception as e:
            print(f"\nDownload failed: {e}")
            return False
            
    def extract_zip(self, zip_path, extract_to):
        """Extract ZIP file with improved error handling"""
        try:
            print(f"Extracting: {zip_path.name}")
            
            if not zip_path.exists():
                self.print_status("ZIP file does not exist", success=False)
                return False
                
            if zip_path.stat().st_size == 0:
                self.print_status("ZIP file is empty", success=False)
                return False
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Test the ZIP file first
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
        """Move NConvert files with better error handling and logging"""
        nconvert_dir = source_dir / "NConvert"
        
        if not nconvert_dir.exists():
            self.print_status("NConvert directory not found in extracted files", success=False)
            return False
            
        try:
            moved_count = 0
            
            for item in nconvert_dir.iterdir():
                destination = self.script_dir / item.name
                
                # Handle existing files/directories
                if destination.exists():
                    if destination.is_file():
                        destination.unlink()
                    else:
                        shutil.rmtree(destination)
                    print(f"Replaced existing: {item.name}")
                
                # Move the item
                shutil.move(str(item), str(destination))
                moved_count += 1
                print(f"Moved: {item.name}")
                    
            # Clean up empty source directory
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
        """Download and install NConvert executable"""
        if self.nconvert_exe.exists():
            self.print_status("nconvert.exe already exists")
            return True
            
        print("NConvert executable not found, starting download...")
        
        # Get architecture choice
        architecture = self.prompt_architecture()
        url = NCONVERT_URLS[architecture]
        zip_name = f"NConvert-win{'64' if architecture == 'x64' else ''}.zip"
        zip_path = self.data_dir / zip_name
        
        # Clean up any existing partial download
        if zip_path.exists():
            zip_path.unlink()
        
        # Download
        if not self.download_file(url, zip_path):
            # Clean up failed download
            if zip_path.exists():
                zip_path.unlink()
            return False
            
        # Extract to temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            if not self.extract_zip(zip_path, temp_path):
                zip_path.unlink(missing_ok=True)
                return False
                
            # Move files to final location
            if not self.move_nconvert_files(temp_path):
                return False
                
        # Clean up ZIP file
        zip_path.unlink(missing_ok=True)
        
        # Verify installation
        if self.nconvert_exe.exists():
            self.print_status("NConvert installation completed")
            return True
        else:
            self.print_status("nconvert.exe not found after installation", success=False)
            return False
            
    def create_requirements_file(self):
        """Create requirements.txt file with error handling"""
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
        """Install Python packages with better output handling"""
        try:
            print("Installing Python packages...")
            
            # Upgrade pip first
            print("Upgrading pip...")
            pip_upgrade = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
            ], capture_output=True, text=True)
            
            if pip_upgrade.returncode != 0:
                print("Warning: Could not upgrade pip")
            
            # Install requirements
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_status("Python packages installed successfully")
                
                # Show what was installed
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
            
    def verify_installation(self):
        """Verify all components are properly installed"""
        print("\nVerifying installation...")
        all_good = True
        
        # Check NConvert executable
        if self.nconvert_exe.exists():
            self.print_status("nconvert.exe found")
        else:
            self.print_status("nconvert.exe missing", success=False)
            all_good = False
            
        # Check Python packages
        for package in REQUIRED_PACKAGES:
            package_name = package.split('==')[0]
            import_name = PACKAGE_IMPORT_MAP.get(package_name, package_name.replace('-', '_'))
            
            try:
                # Try to import the package
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
        
    def run_installation(self):
        """Execute the complete installation process"""
        # Clear screen at the start
        self.clear_screen()
        
        self.print_header("NConvert-Batch Installer")
        
        # Check Python version
        if not self.check_python_version():
            return False
            
        # Create directories
        if not self.create_directories():
            return False
            
        # Install NConvert (no separator before this)
        if not self.install_nconvert():
            return False
            
        # Create and install Python requirements (no separator before this)
        requirements_path = self.create_requirements_file()
        if not requirements_path:
            return False
            
        if not self.install_python_packages(requirements_path):
            return False
            
        # Verify installation
        success = self.verify_installation()
        
        if success:
            print("    Installation Completed Successfully")
        else:
            print("    Installation Issues Detected")
            print("Please review the errors above and try again.")
        return success


def main():
    """Main entry point with comprehensive error handling"""
    installer = NConvertInstaller()
    
    try:
        success = installer.run_installation()
        
        print(f"\n{'='*SEPARATOR_LENGTH}")
        if success:
            print("V Installation completed successfully!")
        else:
            print("X Installation encountered errors!")
            
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