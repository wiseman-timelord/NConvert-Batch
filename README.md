# NConvertBatch
Its a powershell interface for simplifying batch conversion with NConvert.

### Status:
- It worked well enough. I wont be updating it for a while, but when I have a bunch of files again, I will test it, as I told it to check, sanity and logic, and I dont have any files I want to convert currently.  

## Description:
- This PowerShell script is designed to batch convert .pspimage files to various formats using NConvert, a command-line image conversion tool. The program provides a user-friendly menu to set the source folder, input file format, and desired output format. After converting the files, it reports the total number of successfully converted files and prompts the user with the option to delete the original files. The script ensures efficient and seamless conversion and management of image files, making it a practical tool for users needing to process multiple .pspimage files.

## Features:
- **Multiple Formats**: Type in what format you want from the list, but for reference, its JPEG not JPG, I use these, ask GPT to add your own.
- **Interactive Menu**: Utilizing your standard text-based menu for effective configuration.
- **Batch Conversion**: Converts all `.pspimage` files in the specified folder and its subfolders to the desired format.
- **Automatic Report**: Provides a summary of the total number of successfully converted files.
- **Deletion Option**: Offers the option to delete original files after conversion.
- **Error Handling**: Displays errors for any files that fail to convert.

### Preview:
- The Main Menu...
```
NConvert Batch-Sub Convert

1. Folder Location (F:\Bookwork\Materials)
2. Image Format From (pspimage)
3. Image Format To (jpeg)
-------------------
Select; Options = 1-3, Start = S, Exit = X:

```

## Requirements:
- Windows; probably => 7
- NConvert; If you dont have it is free, and it converts a LOT of formats.

### Instructions:
1. **Download NConvert**: Get NConvert from [NConvert's download page](https://www.xnview.com/en/nconvert/#downloads).
2. **Place Executable**: Ensure my interface is in the same directory as `nconvert.exe`.
3. **Run Script**: Execute the script by double clicking `NConvertBatch.Bat`.
4. **Follow Prompts**: Use the interactive menu to set the folder location, source format, and target format.
5. **Start Conversion**: Select the option to start the conversion process.
6. **Review Report**: Check the report of successfully converted files, and decide whether to delete the original files.
7. **Exit Script**: The script will pause and exit after completing the operations.

## DISCLAIMER:
This software is subject to the terms in License.Txt, covering usage, distribution, and modifications. For full details on your rights and obligations, refer to License.Txt.
