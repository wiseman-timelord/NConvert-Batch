# Script: `.\nconvert

# Imports
import os
import gradio as gr
import webbrowser
from threading import Timer
import subprocess
from tkinter import Tk, filedialog
import asyncio
import psutil
import socket

# Determine the full path of the workspace directory
workspace_path = os.path.abspath(".\\workspace")

# Default values
folder_location = workspace_path
format_from = "PSPIMAGE"
format_to = "JPG"
nconvert_path = ".\\nconvert.exe"
delete_files_after = False

# Allowed file formats (consistent capitalization)
allowed_formats = ["JPEG", "PNG", "BMP", "GIF", "TIFF", "HEIF", "WEBP", "SVG", "PSD", "PSPIMAGE"]

# Global variables to track processing status
files_process_done = 0
files_process_total = 0

def set_folder_location(new_location):
    global folder_location
    folder_location = new_location
    return folder_location

def set_format_from(new_format_from):
    global format_from
    format_from = new_format_from.upper()
    return format_from

def set_format_to(new_format_to):
    global format_to
    format_to = new_format_to.upper()
    return format_to

def set_delete_files_after(should_delete):
    global delete_files_after
    delete_files_after = should_delete
    return delete_files_after

def start_conversion():
    global files_process_done, files_process_total

    if not os.path.exists(folder_location):
        return "Please set a valid folder location."
    
    files = []
    for root, dirs, filenames in os.walk(folder_location):
        for filename in filenames:
            if filename.lower().endswith(f".{format_from.lower()}"):
                files.append(os.path.join(root, filename))

    if not files:
        return f"No files with the extension {format_from} found in the specified location."
    
    files_process_done = 0
    files_process_total = len(files)
    conversion_results = []

    for input_file in files:
        output_file = os.path.splitext(input_file)[0] + f".{format_to.lower()}"
        command = f"{nconvert_path} -out {format_to.lower()} -overwrite -o \"{output_file}\" \"{input_file}\""
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            files_process_done += 1
            conversion_results.append((input_file, True, ""))
        else:
            error_message = result.stderr.strip() if result.stderr else "Unknown error occurred"
            conversion_results.append((input_file, False, error_message))

    if delete_files_after:
        for input_file, success, _ in conversion_results:
            if success:
                try:
                    os.remove(input_file)
                except Exception as e:
                    conversion_results.append((input_file, False, f"Failed to delete: {str(e)}"))

    result_message = f"Conversion completed. Total files processed: {files_process_total}\n"
    result_message += f"Successfully converted: {files_process_done}\n"
    result_message += f"Failed conversions: {files_process_total - files_process_done}"

    for input_file, success, error_message in conversion_results:
        if not success:
            result_message += f"Error converting {input_file}: {error_message}\n"

    return result_message

def check_if_port_in_use(port):
    """Check if the specified port is in use by any process."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("localhost", port)) == 0

def prompt_user_for_action():
    """Prompt the user to decide how to handle the existing Gradio server."""
    while True:
        choice = input("Critical Warning: Gradio Server On Same Port!\n"
                       "Selection; Close Other = C, Change Port = P, Run Anyway = R: ").strip().upper()
        if choice in ['C', 'P', 'R']:
            return choice
        else:
            print("Invalid selection. Please choose C, P, or R.")

def close_existing_gradio_servers(port):
    """Close existing Gradio servers running on the specified port."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'] and any(f"--port {port}" in arg for arg in proc.info['cmdline']):
                proc.terminate()  # You can use proc.kill() for a forceful termination.
        except psutil.NoSuchProcess:
            pass

def launch_gradio_interface():
    global files_process_done, files_process_total, folder_location, format_from, format_to

    def browse_folder():
        global folder_location
        root = Tk()
        root.withdraw()
        root.lift()
        root.attributes("-topmost", True)
        folder_selected = filedialog.askdirectory(initialdir=folder_location)
        root.destroy()
        if folder_selected:
            folder_location = folder_selected
        return folder_location

    with gr.Blocks() as demo:
        with gr.Tabs():
            with gr.Tab("Main Page"):
                gr.Markdown("## NConvert Batch")
                
                with gr.Row():
                    folder_location_display = gr.Textbox(label="Folder Location", value=folder_location, interactive=False, scale=5)
                    browse_button = gr.Button("Browse", scale=1)
                
                with gr.Row():
                    format_from_input = gr.Dropdown(label="Image Format From", choices=allowed_formats, value=format_from, interactive=True, scale=2)
                    format_to_input = gr.Dropdown(label="Image Format To", choices=allowed_formats, value=format_to, interactive=True, scale=2)
                    delete_files_checkbox = gr.Checkbox(label="Delete Original Files?", value=False, scale=1)
                
                with gr.Row():
                    start_button = gr.Button("Start Conversion", scale=5)
                    exit_button = gr.Button("Exit Program", scale=1)

                result_output = gr.Textbox(label="Conversion Result", interactive=False, lines=2)

                def on_start_conversion():
                    result = start_conversion()
                    return result
                
                def update_folder_location():
                    new_location = browse_folder()
                    set_folder_location(new_location)
                    return new_location

                browse_button.click(fn=update_folder_location, inputs=None, outputs=folder_location_display)
                format_from_input.change(fn=set_format_from, inputs=format_from_input, outputs=format_from_input)
                format_to_input.change(fn=set_format_to, inputs=format_to_input, outputs=format_to_input)
                delete_files_checkbox.change(fn=set_delete_files_after, inputs=delete_files_checkbox, outputs=delete_files_checkbox)
                start_button.click(fn=on_start_conversion, inputs=None, outputs=result_output)
                exit_button.click(fn=lambda: os._exit(0), inputs=None, outputs=None)
                
        port = 7860
        while True:
            if check_if_port_in_use(port):
                user_choice = prompt_user_for_action()
                if user_choice == 'C':
                    close_existing_gradio_servers(port)
                elif user_choice == 'P':
                    port += 1
                    continue
                elif user_choice == 'R':
                    break
            try:
                url = f"http://localhost:{port}"
                Timer(1, lambda: webbrowser.open(url)).start()
                demo.launch(server_name="localhost", server_port=port, share=False)
                break
            except OSError:
                port += 1

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop(asyncio.ProactorEventLoop())
    launch_gradio_interface()
