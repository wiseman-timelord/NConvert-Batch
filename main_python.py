import os
import gradio as gr
import webbrowser
from threading import Timer
import subprocess

# Default values
folder_location = "X:\\PathTo\\YourFolder"
format_from = "pspimage"
format_to = "jpeg"  # Corrected format for JPEG output
nconvert_path = ".\\nconvert.exe"
delete_files_after = False

# Allowed file formats
allowed_formats = ["JPEG", "PNG", "BMP", "GIF", "TIFF", "HEIF", "WebP", "SVG", "PSD", "PSPIMAGE"]

def set_folder_location(new_location):
    global folder_location
    folder_location = new_location
    return folder_location

def set_format_from(new_format_from):
    global format_from
    format_from = new_format_from.lower()
    return format_from

def set_format_to(new_format_to):
    global format_to
    format_to = new_format_to.lower()
    return format_to

def set_delete_files_after(should_delete):
    global delete_files_after
    delete_files_after = should_delete
    return delete_files_after

def start_conversion():
    if not os.path.exists(folder_location):
        return "Please set a valid folder location."
    
    files = [os.path.join(root, file) 
             for root, dirs, files in os.walk(folder_location) 
             for file in files if file.endswith(f".{format_from}")]
    
    if not files:
        return f"No files with the extension {format_from} found in the specified location."
    
    converted_count = 0
    total_files = len(files)
    remaining_files = total_files

    for input_file in files:
        output_file = os.path.splitext(input_file)[0] + f".{format_to}"
        command = f"{nconvert_path} -out {format_to} -o \"{output_file}\" \"{input_file}\""
        
        result = subprocess.run(command, shell=True)
        
        if result.returncode == 0:
            converted_count += 1
        remaining_files -= 1
    
    if delete_files_after:
        for input_file in files:
            os.remove(input_file)
    
    return f"Conversion completed. Total files converted: {converted_count}"

def launch_gradio_interface():
    def update_stats():
        if not os.path.exists(folder_location):
            return "N/A", "N/A"
        
        files = [os.path.join(root, file) 
                 for root, dirs, files in os.walk(folder_location) 
                 for file in files if file.endswith(f".{format_from}")]
        
        total_files = len(files)
        return str(total_files), str(total_files)

    with gr.Blocks() as demo:
        with gr.Tabs():
            with gr.Tab("Main Page"):
                gr.Markdown("## NConvert Batch")
                
                with gr.Row():
                    folder_location_input = gr.Textbox(label="Folder Location", value=folder_location, interactive=True, scale=5)
                    delete_files_checkbox = gr.Checkbox(label="Delete Files After?", value=False, scale=1)
                
                with gr.Row():
                    format_from_input = gr.Dropdown(label="Image Format From", choices=allowed_formats, value=format_from.upper(), interactive=True)
                    format_to_input = gr.Dropdown(label="Image Format To", choices=allowed_formats, value=format_to.upper(), interactive=True)
                
                with gr.Row():
                    files_processed = gr.Textbox(label="Files Processed", value="0", interactive=False)
                    files_remaining = gr.Textbox(label="Files Remaining", value="0", interactive=False)
                
                with gr.Row():
                    start_button = gr.Button("Start Conversion", scale=5)
                    exit_button = gr.Button("Exit Program", scale=1)

                def on_start_conversion():
                    total_files, _ = update_stats()
                    files_remaining.update(value=total_files)
                    result = start_conversion()
                    files_processed.update(value=total_files)
                    files_remaining.update(value="0")
                    return result
                
                folder_location_input.change(set_folder_location, inputs=[folder_location_input], outputs=folder_location_input)
                format_from_input.change(set_format_from, inputs=[format_from_input], outputs=format_from_input)
                format_to_input.change(set_format_to, inputs=[format_to_input], outputs=format_to_input)
                delete_files_checkbox.change(set_delete_files_after, inputs=[delete_files_checkbox], outputs=delete_files_checkbox)
                start_button.click(on_start_conversion, outputs=None)
                exit_button.click(lambda: os._exit(0), outputs=None)
                
        port = 7860
        while True:
            try:
                url = f"http://localhost:{port}"
                Timer(1, lambda: webbrowser.open(url)).start()
                demo.launch(server_name="localhost", server_port=port)
                break
            except OSError:
                port += 1

if __name__ == "__main__":
    launch_gradio_interface()