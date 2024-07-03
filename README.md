# NConvertBatch
Its a, Powershell or Puthon Gradio, interface for simplifying batch image conversion with NConvert.

### Status:
Under development....
- Testing of v0.02, code is considered experimental.
- Some kind of summary display on the powershell one. 

## Description:
- This was a PowerShell script designed to batch convert images from/to any format using NConvert, a command-line image conversion tool, however, this Powershell script is now optional, as one can now choose to instead use the Python version, featuring a Gradio Interface. The program provides a user-friendly menu to set the source folder, input file format, and desired output format. The scripts ensures efficient and seamless conversion and management of image files, making it a practical tool for users needing to process multiple .pspimage files. 

## Features:
- **Multiple Formats**: The Gradio interface limited to 10 including Pspimage, the powershell has hundereds. 
- **Interactive Menu**: Utilizing your standard text-based menu for effective configuration.
- **Batch Conversion**: All specified format files in, specified folder and its subfolders, to desired format.
- **Automatic Report**: Provides a summary of the total number of successfully converted files.
- **Deletion Option**: Offers the option to delete original files.
- **Error Handling**: Displays errors for any files that fail to convert.

### Preview:
- The Main Page (Python Gradio Version)...
![Alternative text](https://github.com/wiseman-timelord/NConvertBatch/blob/main/media/MainPage.jpg)
- The Main Menu (Powershell Version)...
```
===============(N Convert Batch)================


                  Conversion Menu

    1. Folder Location (X:\PathTo\YourFolder)
    2. Image Format From (pspimage)
    3. Image Format To (jpeg)
    4. Delete Files After Conversion (False)

-------------------------------------------------
Select; Options = 1-4, Start = S, Exit = X:

```

## Requirements:
- Windows; probably => 7
- NConvert; If you dont have it is free, and it converts a LOT of formats.

### Instructions:
1. **Download NConvert**: Get NConvert from [NConvert's download page](https://www.xnview.com/en/nconvert/#downloads).
2. **Place Executable**: Ensure my NConvert Batch is in the same directory as `nconvert.exe`.
3. **Run Script**: Execute the script by double clicking `NConvertBatch.Bat`.
4. Decide what version you want to run, do you want common image formats or more rare, if common use the Python one.
4. **Follow Prompts**: Use the interactive menu to set the folder location, source format, and target format.
5. **Start Conversion**: Select the option to start the conversion process.
6. **Review Report**: Check if the files were successfully converted, they will be in the same folder as the originals.
7. **Exit Script**: The script will pause and exit after completing the operations.

## DISCLAIMER:
This software is subject to the terms in License.Txt, covering usage, distribution, and modifications. For full details on your rights and obligations, refer to License.Txt.
