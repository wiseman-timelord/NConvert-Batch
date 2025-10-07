# Script: launcher.py  (COMPLETE UPDATED FILE)
# Compatible with Python 3.9 and Windows Server 2012

# Imports
import os
import sys
import gradio as gr
import webbrowser
from threading import Timer
import subprocess
import asyncio
import psutil
import socket
import time
from pathlib import Path
import json   # NEW

# Determine the full path of the workspace directory
workspace_path = os.path.abspath(os.path.join(".", "workspace"))

# NEW: settings file path
SETTINGS_FILE = Path(__file__).with_name("last_session.json")

# NEW: load last session (folder + formats)
def load_last_session():
    """Return dict with last used folder, from, to; use defaults if missing."""
    defaults = {
        "last_folder": workspace_path,
        "last_from": "PSPIMAGE",
        "last_to": "JPEG"
    }
    if SETTINGS_FILE.exists():
        try:
            with SETTINGS_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
                candidate = Path(data.get("last_folder", ""))
                if candidate.exists() and candidate.is_dir():
                    defaults["last_folder"] = str(candidate.resolve())
                defaults["last_from"]  = data.get("last_from", defaults["last_from"])
                defaults["last_to"]    = data.get("last_to",   defaults["last_to"])
        except Exception:
            pass  # corrupted -> ignore
    return defaults

# NEW: persist session after successful conversion
def save_last_session(folder: str, from_fmt: str, to_fmt: str):
    """Save folder and formats for next launch."""
    try:
        SETTINGS_FILE.write_text(
            json.dumps({
                "last_folder": str(Path(folder).resolve()),
                "last_from": from_fmt.upper(),
                "last_to": to_fmt.upper()
            }, indent=2),
            encoding="utf-8"
        )
    except Exception:
        pass  # fail silently

# Load persisted values (or defaults)
_session = load_last_session()
folder_location = _session["last_folder"]
format_from     = _session["last_from"]
format_to       = _session["last_to"]

nconvert_path = os.path.join(".", "nconvert.exe")
delete_files_after = False

# Allowed file formats (consistent capitalization)
allowed_formats = ["JPEG", "PNG", "BMP", "GIF", "TIFF", "HEIF", "WEBP", "SVG", "PSD", "PSPIMAGE"]

# Global variables to track processing status
files_process_done = 0
files_process_total = 0

# -------------------- existing helpers unchanged --------------------
def set_folder_location(new_location):
    global folder_location
    if new_location and os.path.exists(new_location):
        folder_location = new_location
    return folder_location

def set_format_from(new_format_from):
    global format_from
    if new_format_from:
        format_from = new_format_from.upper()
    return format_from

def set_format_to(new_format_to):
    global format_to
    if new_format_to:
        format_to = new_format_to.upper()
    return format_to

def set_delete_files_after(should_delete):
    global delete_files_after
    delete_files_after = bool(should_delete)
    return delete_files_after

def validate_nconvert_path():
    if not os.path.exists(nconvert_path):
        return False, f"nconvert.exe not found at {nconvert_path}"
    try:
        result = subprocess.run([nconvert_path, "-help"],
                              capture_output=True, text=True, timeout=5)
        return True, "nconvert.exe is accessible"
    except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError) as e:
        return False, f"Cannot execute nconvert.exe: {str(e)}"

def find_files_to_convert():
    if not os.path.exists(folder_location):
        return []
    files = []
    try:
        for root, dirs, filenames in os.walk(folder_location):
            for filename in filenames:
                if filename.lower().endswith(f".{format_from.lower()}"):
                    files.append(os.path.join(root, filename))
    except (PermissionError, OSError) as e:
        print(f"Error accessing directory: {e}")
    return files

# -------------------- conversion function --------------------
def start_conversion():
    global files_process_done, files_process_total
    is_valid, message = validate_nconvert_path()
    if not is_valid:
        return f"Error: {message}"
    if not os.path.exists(folder_location):
        return "Error: Please set a valid folder location."
    files = find_files_to_convert()
    if not files:
        return f"No files with the extension '{format_from}' found in the specified location."
    files_process_done = 0
    files_process_total = len(files)
    conversion_results = []
    status_message = f"Starting conversion of {files_process_total} files...\n"
    for i, input_file in enumerate(files, 1):
        try:
            output_file = os.path.splitext(input_file)[0] + f".{format_to.lower()}"
            command = [
                nconvert_path,
                "-out", format_to.lower(),
                "-overwrite",
                "-o", output_file,
                input_file
            ]
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                files_process_done += 1
                conversion_results.append((input_file, True, ""))
                status_message += f"[{i}/{files_process_total}] Converted: {os.path.basename(input_file)}\n"
            else:
                error_message = result.stderr.strip() if result.stderr else "Unknown error occurred"
                conversion_results.append((input_file, False, error_message))
                status_message += f"[{i}/{files_process_total}] Failed: {os.path.basename(input_file)} - {error_message}\n"
        except subprocess.TimeoutExpired:
            conversion_results.append((input_file, False, "Conversion timeout"))
            status_message += f"[{i}/{files_process_total}] Timeout: {os.path.basename(input_file)}\n"
        except Exception as e:
            conversion_results.append((input_file, False, str(e)))
            status_message += f"[{i}/{files_process_total}] Error: {os.path.basename(input_file)} - {str(e)}\n"
    if delete_files_after:
        deleted_count = 0
        for input_file, success, _ in conversion_results:
            if success:
                try:
                    os.remove(input_file)
                    deleted_count += 1
                except Exception as e:
                    status_message += f"Failed to delete {os.path.basename(input_file)}: {str(e)}\n"
        if deleted_count > 0:
            status_message += f"Deleted {deleted_count} original files.\n"
    failed_count = files_process_total - files_process_done
    status_message += f"\n=== CONVERSION SUMMARY ===\n"
    status_message += f"Total files processed: {files_process_total}\n"
    status_message += f"Successfully converted: {files_process_done}\n"
    status_message += f"Failed conversions: {failed_count}\n"
    # NEW: persist session
    save_last_session(folder_location, format_from, format_to)
    return status_message

# -------------------- existing port / process helpers --------------------
def check_if_port_in_use(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            return sock.connect_ex(("localhost", port)) == 0
    except Exception:
        return False

def find_available_port(start_port=7860, max_attempts=10):
    for i in range(max_attempts):
        port = start_port + i
        if not check_if_port_in_use(port):
            return port
    return None

def close_existing_gradio_servers(port):
    closed_count = 0
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'python' in proc.info.get('name', '').lower():
                    cmdline_str = ' '.join(cmdline)
                    if f"--port {port}" in cmdline_str or f"server_port={port}" in cmdline_str:
                        proc.terminate()
                        closed_count += 1
                        time.sleep(0.5)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"Error closing processes: {e}")
    return closed_count

def browse_folder_dialog():
    try:
        from tkinter import Tk, filedialog
        root = Tk()
        root.withdraw()
        root.lift()
        root.attributes("-topmost", True)
        folder_selected = filedialog.askdirectory(initialdir=folder_location)
        root.destroy()
        if folder_selected:
            return folder_selected
        return folder_location
    except Exception as e:
        print(f"Tkinter dialog failed: {e}")
        return folder_location

# -------------------- Gradio interface --------------------
def create_gradio_interface():
    def browse_folder():
        new_location = browse_folder_dialog()
        set_folder_location(new_location)
        return new_location
    def on_format_from_change(new_format):
        return set_format_from(new_format)
    def on_format_to_change(new_format):
        return set_format_to(new_format)
    def on_delete_change(should_delete):
        return set_delete_files_after(should_delete)
    def on_start_conversion():
        return start_conversion()
    def on_exit():
        try:
            os._exit(0)
        except:
            sys.exit(0)
    with gr.Blocks(title="NConvert Batch Processor", theme=gr.themes.Default()) as demo:
        gr.Markdown("# NConvert Batch Image Converter")
        gr.Markdown("Convert multiple image files from one format to another using NConvert.")
        with gr.Row():
            folder_location_display = gr.Textbox(
                label="Folder Location",
                value=folder_location,
                interactive=True,
                scale=4,
                placeholder="Enter folder path or use Browse button"
            )
            browse_button = gr.Button("Browse", scale=1, variant="secondary")
        with gr.Row():
            format_from_input = gr.Dropdown(
                label="Convert From",
                choices=allowed_formats,
                value=format_from,
                interactive=True,
                scale=1
            )
            format_to_input = gr.Dropdown(
                label="Convert To",
                choices=allowed_formats,
                value=format_to,
                interactive=True,
                scale=1
            )
            delete_files_checkbox = gr.Checkbox(
                label="Delete Original Files After Conversion",
                value=False,
                scale=1
            )
        with gr.Row():
            start_button = gr.Button("Start Conversion", variant="primary", scale=4)
            exit_button = gr.Button("Exit Program", variant="stop", scale=1)
        result_output = gr.Textbox(
            label="Conversion Results",
            interactive=False,
            lines=10,
            max_lines=20,
            show_copy_button=True
        )
        # Connect events
        browse_button.click(fn=browse_folder, inputs=None, outputs=folder_location_display)
        folder_location_display.change(fn=set_folder_location, inputs=folder_location_display, outputs=folder_location_display)
        format_from_input.change(fn=on_format_from_change, inputs=format_from_input, outputs=None)
        format_to_input.change(fn=on_format_to_change, inputs=format_to_input, outputs=None)
        delete_files_checkbox.change(fn=on_delete_change, inputs=delete_files_checkbox, outputs=None)
        start_button.click(fn=on_start_conversion, inputs=None, outputs=result_output)
        exit_button.click(fn=on_exit, inputs=None, outputs=None)
    return demo

# -------------------- launcher entry --------------------
def launch_gradio_interface():
    port = find_available_port(7860)
    if port is None:
        print("Error: No available ports found. Please close other applications and try again.")
        return
    if not os.path.exists(workspace_path):
        try:
            os.makedirs(workspace_path)
            print(f"Created workspace directory: {workspace_path}")
        except Exception as e:
            print(f"Warning: Could not create workspace directory: {e}")
    try:
        url = f"http://localhost:{port}"
        print(f"Starting Gradio interface on {url}")
        Timer(2, lambda: webbrowser.open(url)).start()
        demo = create_gradio_interface()
        demo.launch(
            server_name="localhost",
            server_port=port,
            share=False,
            inbrowser=False,
            show_error=True,
            quiet=False
        )
    except Exception as e:
        print(f"Error launching Gradio interface: {e}")
        print("Please check that the port is available and try again.")

def main():
    print("NConvert Batch Processor")
    print("=" * 30)
    if sys.version_info < (3, 9):
        print("Error: Python 3.9 or higher is required.")
        return
    is_valid, message = validate_nconvert_path()
    if not is_valid:
        print(f"Warning: {message}")
        print("Please ensure nconvert.exe is in the same directory as this script.")
    if os.name == 'nt':
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except AttributeError:
            pass
    launch_gradio_interface()

if __name__ == "__main__":
    main()