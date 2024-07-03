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

def start_conversion():
    if not os.path.exists(folder_location):
        return "Please set a valid folder location."
    
    files = [os.path.join(root, file) 
             for root, dirs, files in os.walk(folder_location) 
             for file in files if file.endswith(f".{format_from}")]
    
    if not files:
        return f"No files with the extension {format_from} found in the specified location."
    
    converted_count = 0
    for input_file in files:
        output_file = os.path.splitext(input_file)[0] + f".{format_to}"
        command = f"{nconvert_path} -out {format_to} -o \"{output_file}\" \"{input_file}\""
        
        result = subprocess.run(command, shell=True)
        
        if result.returncode == 0:
            converted_count += 1
    
    return f"Conversion completed. Total files converted: {converted_count}"

def launch_gradio_interface():
    with gr.Blocks() as demo:
        with gr.Tabs():
            with gr.Tab("Main Page"):
                gr.Markdown("## NConvert Batch-Sub Convert")
                
                with gr.Column():
                    folder_location_input = gr.Textbox(label="Folder Location", value=folder_location, interactive=True)
                    format_from_input = gr.Dropdown(label="Image Format From", choices=allowed_formats, value=format_from.upper(), interactive=True)
                    format_to_input = gr.Dropdown(label="Image Format To", choices=allowed_formats, value=format_to.upper(), interactive=True)
                    start_button = gr.Button("Start Conversion")
                
                folder_location_input.change(set_folder_location, inputs=[folder_location_input], outputs=folder_location_input)
                format_from_input.change(set_format_from, inputs=[format_from_input], outputs=format_from_input)
                format_to_input.change(set_format_to, inputs=[format_to_input], outputs=format_to_input)
                start_button.click(start_conversion, outputs=None)
                
        port = 7860
        url = f"http://localhost:{port}"
        Timer(1, lambda: webbrowser.open(url)).start()
        demo.launch(server_name="localhost", server_port=port)

if __name__ == "__main__":
    launch_gradio_interface()
