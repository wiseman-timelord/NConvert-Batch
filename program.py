# Script: program.py - NConvert Batch Converter
# Compatible with Python 3.9–3.11 and Windows 8.1–11
# Gradio v5.49.1 + NConvert v7.110

print("Starting Imports...")
import os
import sys
import time
import gradio as gr
import webbrowser
from threading import Timer, Thread
import subprocess
import asyncio
import psutil
import socket
from pathlib import Path
import json
from tkinter import filedialog
import winsound

print("..Imports Completed.")

print("Initializing Program...")
# ─── Global References ──────────────────────────────────────────────────────────
global_demo = None

# ─── Paths & Globals ────────────────────────────────────────────────────────────

workspace_path = os.path.abspath(os.path.join(".", "temp"))
DATA_DIR = Path(__file__).parent / "data"
SETTINGS_FILE = DATA_DIR / "persistent.json"
nconvert_path = str(Path(__file__).parent / "nconvert.exe")
allowed_formats = ["JPEG", "PNG", "BMP", "GIF", "TIFF", "HEIF", "WEBP", "SVG", "PSD", "PSPIMAGE"]

# Session defaults
_session = {
    "last_folder": workspace_path,
    "last_from": "PSPIMAGE",
    "last_to": "JPEG",
    "last_delete": False,
    "beep_on_complete": False
}

# Load last session if exists
if SETTINGS_FILE.exists():
    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            candidate = Path(data.get("last_folder", ""))
            if candidate.exists() and candidate.is_dir():
                _session["last_folder"] = str(candidate.resolve())
            _session["last_from"] = data.get("last_from", _session["last_from"])
            _session["last_to"] = data.get("last_to", _session["last_to"])
            _session["last_delete"] = data.get("last_delete", _session["last_delete"])
            _session["beep_on_complete"] = data.get("beep_on_complete", _session["beep_on_complete"])
        print("Loaded: .\\data\\persistent.json")
    except Exception:
        pass

folder_location = _session["last_folder"]
format_from = _session["last_from"]
format_to = _session["last_to"]
delete_files_after = _session["last_delete"]
beep_on_complete = _session["beep_on_complete"]

# Processing tracking
files_process_done = 0
files_process_total = 0

print("..Initialization Complete.\n")

# ─── Helpers ────────────────────────────────────────────────────────────────────

def save_last_session():
    try:
        DATA_DIR.mkdir(exist_ok=True)
        SETTINGS_FILE.write_text(
            json.dumps({
                "last_folder": str(Path(folder_location).resolve()),
                "last_from": format_from.upper(),
                "last_to": format_to.upper(),
                "last_delete": bool(delete_files_after),
                "beep_on_complete": bool(beep_on_complete)
            }, indent=2),
            encoding="utf-8"
        )
        print("Saved: .\\data\\persistent.json")
    except Exception as e:
        print(f"Error saving session: {str(e)}")

def set_folder_location(new_location):
    global folder_location
    if new_location and os.path.exists(new_location):
        folder_location = new_location

def set_beep(value):
    global beep_on_complete
    beep_on_complete = bool(value)

def set_delete_files_after(value):
    global delete_files_after
    delete_files_after = bool(value)

def set_format_from(new_format):
    global format_from
    if new_format:
        format_from = new_format.upper()

def set_format_to(new_format):
    global format_to
    if new_format:
        format_to = new_format.upper()

def find_files_to_convert():
    if not os.path.exists(folder_location):
        return []
    files = []
    ext = f".{format_from.lower()}"
    for root, _, filenames in os.walk(folder_location):
        for fn in filenames:
            if fn.lower().endswith(ext):
                files.append(os.path.join(root, fn))
    return files

def graceful_shutdown():
    save_last_session()
    print("Shutting down NConvert Batch Converter...")
    try:
        if global_demo is not None:
            global_demo.close()
            time.sleep(0.6)
    except Exception as e:
        print(f"Graceful close failed: {e}")
    print("Process terminated cleanly")
    os._exit(0)

# ─── Main Conversion ────────────────────────────────────────────────────────────

def start_conversion():
    global files_process_done, files_process_total

    if not os.path.exists(folder_location):
        return "Error: Invalid folder location."

    files = find_files_to_convert()
    if not files:
        return f"No .{format_from.lower()} files found in selected folder."

    files_process_done = 0
    files_process_total = len(files)
    newly_converted = []
    log = [f"Processing {files_process_total} file(s)...\n"]

    for infile in files:
        outfile = os.path.splitext(infile)[0] + f".{format_to.lower()}"
        infile_abs = os.path.abspath(infile)
        outfile_abs = os.path.abspath(outfile)
        working_dir = os.path.dirname(nconvert_path)

        cmd = [
            nconvert_path,
            "-out", format_to.lower(),
            "-overwrite",
            "-o", outfile_abs,
            infile_abs
        ]

        filename_display = os.path.basename(infile)
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False,
                cwd=working_dir,
                timeout=30
            )
            if result.returncode == 0:
                files_process_done += 1
                newly_converted.append(outfile_abs)
                log.append(f"{filename_display} - {format_from.lower()} → {format_to.lower()}")
            else:
                err = result.stderr.strip() or "Unknown error"
                log.append(f"{filename_display} - FAILED ({err})")
        except subprocess.TimeoutExpired:
            log.append(f"{filename_display} - TIMEOUT")
        except Exception as e:
            log.append(f"{filename_display} - ERROR: {str(e)}")

    # Delete originals if requested
    if delete_files_after:
        deleted_count = 0
        converted_set = set(newly_converted)
        for orig in files:
            expected = os.path.splitext(orig)[0] + f".{format_to.lower()}"
            if expected in converted_set:
                try:
                    os.remove(orig)
                    deleted_count += 1
                except Exception as e:
                    log.append(f"Failed to delete {os.path.basename(orig)}: {e}")
        if deleted_count:
            log.append(f"\nDeleted {deleted_count} original file(s)")

    # Summary
    failed = files_process_total - files_process_done
    log.append("\n" + "─" * 40)
    log.append("CONVERSION SUMMARY")
    log.append(f"Total files:      {files_process_total}")
    log.append(f"Successfully:     {files_process_done}")
    log.append(f"Failed:           {failed}")
    log.append("─" * 40)

    if failed == 0 and files_process_done > 0:
        log.insert(1, "All files converted successfully ✓\n")

    # Beep on completion
    if beep_on_complete and files_process_done > 0:
        def delayed_beep():
            time.sleep(0.5)
            if os.name == 'nt':
                winsound.Beep(1000, 800)
            else:
                print("\a")
        Thread(target=delayed_beep, daemon=True).start()

    return "\n".join(log)

# ─── UI ─────────────────────────────────────────────────────────────────────────

def create_interface():
    css = """
    button, .gr-button {
        min-height: 80px !important;
        height: 80px !important;
        font-size: 1.2rem !important;
        padding: 0.5rem 1rem !important;
    }
    .gr-row {
        margin-bottom: 1rem;
    }
    """

    with gr.Blocks(title="NConvert Batch Converter", css=css) as demo:
        gr.Markdown("# NConvert Batch Image Converter")

        with gr.Row():
            folder_txt = gr.Textbox(
                label="Folder Location",
                value=folder_location,
                placeholder="Select or type folder path...",
                scale=5
            )
            browse_btn = gr.Button("Browse", scale=1)

        with gr.Row():
            from_dd = gr.Dropdown(
                choices=allowed_formats,
                value=format_from,
                label="Convert From",
                scale=1
            )
            to_dd = gr.Dropdown(
                choices=allowed_formats,
                value=format_to,
                label="Convert To",
                scale=1
            )
            with gr.Column(scale=1):
                delete_cb = gr.Checkbox(
                    label="Delete originals after",
                    value=delete_files_after
                )
                beep_cb = gr.Checkbox(
                    label="Beep on completion",
                    value=beep_on_complete
                )

        with gr.Row():
            result_box = gr.Textbox(
                label="Conversion Log",
                lines=20,
                max_lines=20,
                interactive=False,
                show_copy_button=True
            )

        with gr.Row():
            convert_btn = gr.Button("Start Conversion", variant="primary", scale=4)
            exit_btn = gr.Button("Exit", variant="stop", scale=1)

        # ─── Event Handlers ─────────────────────────────────────────────────────

        def browse_folder():
            new_folder = filedialog.askdirectory(initialdir=folder_location)
            if new_folder:
                set_folder_location(new_folder)
                return os.path.abspath(new_folder), ""
            return folder_location, ""

        def change_folder(new_location):
            set_folder_location(new_location)
            return new_location, ""

        def handle_exit():
            graceful_shutdown()

        # ─── Bindings ───────────────────────────────────────────────────────────

        browse_btn.click(
            browse_folder,
            outputs=[folder_txt, result_box]
        )

        folder_txt.change(
            change_folder,
            inputs=folder_txt,
            outputs=[folder_txt, result_box]
        )

        from_dd.change(set_format_from, inputs=from_dd)
        to_dd.change(set_format_to, inputs=to_dd)
        delete_cb.change(set_delete_files_after, inputs=delete_cb)
        beep_cb.change(set_beep, inputs=beep_cb)

        convert_btn.click(
            start_conversion,
            outputs=result_box
        )

        exit_btn.click(fn=handle_exit)

    return demo

# ─── Launcher ───────────────────────────────────────────────────────────────────

def find_free_port(start=7860, attempts=12):
    for p in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    return None

def close_old_gradio(port):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = ' '.join(proc.info['cmdline'] or [])
            if 'gradio' in cmd.lower() and f"port {port}" in cmd:
                proc.terminate()
        except:
            pass

def launch():
    global global_demo

    if sys.version_info < (3, 9):
        print("Python 3.9 or newer required")
        sys.exit(1)

    port = find_free_port()
    if not port:
        print("No free port found in range 7860–7871")
        sys.exit(1)

    close_old_gradio(port)

    print(f"Launching interface on http://localhost:{port}")
    Timer(2.5, lambda: webbrowser.open(f"http://localhost:{port}")).start()

    demo = create_interface()
    global_demo = demo

    demo.launch(
        server_name="127.0.0.1",
        server_port=port,
        share=False,
        inbrowser=False,
        quiet=False
    )

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    launch()