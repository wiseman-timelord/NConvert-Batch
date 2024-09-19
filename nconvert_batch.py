import os
import gradio as gr
import webbrowser
from threading import Timer
import subprocess
from tkinter import Tk, filedialog
import asyncio

# Determine the full path of the workspace directory
workspace_path = os.path.abspath(".\\workspace")

# Default values
folder_location = workspace_path
format_from = "PSPIMAGE"
format_to = "JPEG"
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
    
    files = [os.path.join(root, file) 
             for root, dirs, files in os.walk(folder_location) 
             for file in files if file.lower().endswith(f".{format_from.lower()}")]

    if not files:
        return f"No files with the extension {format_from} found in the specified location."
    
    files_process_done = 0
    files_process_total = len(files)

    for input_file in files:
        output_file = os.path.splitext(input_file)[0] + f".{format_to.lower()}"
        command = f"{nconvert_path} -out {format_to.lower()} -o \"{output_file}\" \"{input_file}\""
        
        result = subprocess.run(command, shell=True)
        
        if result.returncode == 0:
            files_process_done += 1
    
    if delete_files_after:
        for input_file in files:
            os.remove(input_file)
    
    return f"Conversion completed. Total files converted: {files_process_done}"

def launch_gradio_interface():
    global files_process_done, files_process_total, folder_location, format_from, format_to

    def browse_folder():
        global folder_location
        root = Tk()
        root.withdraw()  # Hide the main window
        root.lift()  # Bring the window to the front
        root.attributes("-topmost", True)  # Keep the window on top
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
                start_button.click(fn=on_start_conversion, inputs=None, outputs=None)
                exit_button.click(fn=lambda: os._exit(0), inputs=None, outputs=None)
                
        port = 7860
        while True:
            try:
                url = f"http://localhost:{port}"
                Timer(1, lambda: webbrowser.open(url)).start()
                demo.launch(server_name="localhost", server_port=port, share=False)
                break
            except OSError:
                port += 1

if __name__ == "__main__":
    # Set ProactorEventLoop for Windows explicitly
    if os.name == 'nt':
        asyncio.set_event_loop(asyncio.ProactorEventLoop())
    launch_gradio_interface()
