# Script: nconvert_gradio_batch.py
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

# Determine the full path of the workspace directory
workspace_path = os.path.abspath(os.path.join(".", "workspace"))

# Default values
folder_location = workspace_path
format_from = "PSPIMAGE"
format_to = "JPG"
nconvert_path = os.path.join(".", "nconvert.exe")
delete_files_after = False

# Allowed file formats (consistent capitalization)
allowed_formats = ["JPEG", "PNG", "BMP", "GIF", "TIFF", "HEIF", "WEBP", "SVG", "PSD", "PSPIMAGE"]

# Global variables to track processing status
files_process_done = 0
files_process_total = 0

def set_folder_location(new_location):
    """Update the global folder location."""
    global folder_location
    if new_location and os.path.exists(new_location):
        folder_location = new_location
    return folder_location

def set_format_from(new_format_from):
    """Update the source format."""
    global format_from
    if new_format_from:
        format_from = new_format_from.upper()
    return format_from

def set_format_to(new_format_to):
    """Update the target format."""
    global format_to
    if new_format_to:
        format_to = new_format_to.upper()
    return format_to

def set_delete_files_after(should_delete):
    """Update the delete files setting."""
    global delete_files_after
    delete_files_after = bool(should_delete)
    return delete_files_after

def validate_nconvert_path():
    """Validate that nconvert.exe exists and is accessible."""
    if not os.path.exists(nconvert_path):
        return False, f"nconvert.exe not found at {nconvert_path}"
    
    try:
        # Test if nconvert is executable
        result = subprocess.run([nconvert_path, "-help"], 
                              capture_output=True, text=True, timeout=5)
        return True, "nconvert.exe is accessible"
    except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError) as e:
        return False, f"Cannot execute nconvert.exe: {str(e)}"

def find_files_to_convert():
    """Find all files matching the source format in the specified folder."""
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

def start_conversion():
    """Main conversion function."""
    global files_process_done, files_process_total

    # Validate nconvert
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
            # Create output filename
            output_file = os.path.splitext(input_file)[0] + f".{format_to.lower()}"
            
            # Build nconvert command
            command = [
                nconvert_path,
                "-out", format_to.lower(),
                "-overwrite",
                "-o", output_file,
                input_file
            ]
            
            # Execute conversion
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

    # Delete original files if requested
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

    # Final summary
    failed_count = files_process_total - files_process_done
    status_message += f"\n=== CONVERSION SUMMARY ===\n"
    status_message += f"Total files processed: {files_process_total}\n"
    status_message += f"Successfully converted: {files_process_done}\n"
    status_message += f"Failed conversions: {failed_count}\n"

    return status_message

def check_if_port_in_use(port):
    """Check if the specified port is in use."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            return sock.connect_ex(("localhost", port)) == 0
    except Exception:
        return False

def find_available_port(start_port=7860, max_attempts=10):
    """Find an available port starting from start_port."""
    for i in range(max_attempts):
        port = start_port + i
        if not check_if_port_in_use(port):
            return port
    return None

def close_existing_gradio_servers(port):
    """Attempt to close existing Gradio servers on the specified port."""
    closed_count = 0
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'python' in proc.info.get('name', '').lower():
                    # Check if this process is using the port
                    cmdline_str = ' '.join(cmdline)
                    if f"--port {port}" in cmdline_str or f"server_port={port}" in cmdline_str:
                        proc.terminate()
                        closed_count += 1
                        time.sleep(0.5)  # Give process time to terminate
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"Error closing processes: {e}")
    
    return closed_count

def browse_folder_dialog():
    """Open folder browser dialog. Fallback to input if tkinter fails."""
    try:
        # Try tkinter approach first
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
        # Fallback: return current location
        return folder_location

def create_gradio_interface():
    """Create and configure the Gradio interface."""
    
    def browse_folder():
        """Handle folder browsing."""
        new_location = browse_folder_dialog()
        set_folder_location(new_location)
        return new_location

    def on_format_from_change(new_format):
        """Handle source format change."""
        return set_format_from(new_format)

    def on_format_to_change(new_format):
        """Handle target format change."""
        return set_format_to(new_format)

    def on_delete_change(should_delete):
        """Handle delete checkbox change."""
        return set_delete_files_after(should_delete)

    def on_start_conversion():
        """Handle conversion start."""
        return start_conversion()

    def on_exit():
        """Handle program exit."""
        try:
            os._exit(0)
        except:
            sys.exit(0)

    # Create Gradio interface
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
        browse_button.click(
            fn=browse_folder, 
            inputs=None, 
            outputs=folder_location_display
        )
        
        folder_location_display.change(
            fn=set_folder_location,
            inputs=folder_location_display,
            outputs=folder_location_display
        )
        
        format_from_input.change(
            fn=on_format_from_change, 
            inputs=format_from_input, 
            outputs=None
        )
        
        format_to_input.change(
            fn=on_format_to_change, 
            inputs=format_to_input, 
            outputs=None
        )
        
        delete_files_checkbox.change(
            fn=on_delete_change, 
            inputs=delete_files_checkbox, 
            outputs=None
        )
        
        start_button.click(
            fn=on_start_conversion, 
            inputs=None, 
            outputs=result_output
        )
        
        exit_button.click(
            fn=on_exit, 
            inputs=None, 
            outputs=None
        )

    return demo

def launch_gradio_interface():
    """Launch the Gradio interface with proper port management."""
    
    # Create the interface
    demo = create_gradio_interface()
    
    # Find available port
    port = find_available_port(7860)
    if port is None:
        print("Error: No available ports found. Please close other applications and try again.")
        return
    
    # Check if workspace directory exists, create if not
    if not os.path.exists(workspace_path):
        try:
            os.makedirs(workspace_path)
            print(f"Created workspace directory: {workspace_path}")
        except Exception as e:
            print(f"Warning: Could not create workspace directory: {e}")
    
    # Launch interface
    try:
        url = f"http://localhost:{port}"
        print(f"Starting Gradio interface on {url}")
        
        # Open browser after a short delay
        Timer(2, lambda: webbrowser.open(url)).start()
        
        # Launch Gradio
        demo.launch(
            server_name="localhost",
            server_port=port,
            share=False,
            inbrowser=False,  # We handle browser opening manually
            show_error=True,
            quiet=False
        )
        
    except Exception as e:
        print(f"Error launching Gradio interface: {e}")
        print("Please check that the port is available and try again.")

def main():
    """Main entry point."""
    print("NConvert Batch Processor")
    print("=" * 30)
    
    # Validate Python version
    if sys.version_info < (3, 9):
        print("Error: Python 3.9 or higher is required.")
        return
    
    # Check if nconvert exists
    is_valid, message = validate_nconvert_path()
    if not is_valid:
        print(f"Warning: {message}")
        print("Please ensure nconvert.exe is in the same directory as this script.")
    
    # Set event loop policy for Windows Server 2012 compatibility
    if os.name == 'nt':
        try:
            # Try to use ProactorEventLoop, fall back to default if not available
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except AttributeError:
            # Fallback for older Python versions or systems without ProactorEventLoop
            pass
    
    # Launch interface
    launch_gradio_interface()

if __name__ == "__main__":
    main()