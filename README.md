# NConvert-Batch
Status: Working well after recent revisit, upcoming video on youtube, and I fixed my mic.

## Description:
Its a Python Gradio interface for converting ANY image format to ANY imgage format, even rare ones like `.pspimage`, all made possible through `NConvert` binary command line tool. The program provides a user-friendly menu to set the source folder, input file format, and desired output format. The scripts ensures efficient and seamless conversion and management of image files, making it a practical tool for users needing to process multiple `.pspimage` into a common format such as `.jpg`.

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
- The Batch Launcher (NConvert-Batch.Bat)...
```
========================================================================================================================
    NConvert-Batch
========================================================================================================================










    1. Run NConvert-Batch

    2. Install Requirements









========================================================================================================================
Selection; Menu Options = 1-2, Exit NConvert-Batch = X:
```
- The `Setup-Install` Process (new code for integrated requirements list)...
```
========================================================================================================================
   Run Setup-Install
========================================================================================================================

Installing Requirements...

Upgrading Pip..
Requirement already satisfied: pip in c:\users\mastar\appdata\local\programs\python\python310\lib\site-packages (24.2)
Pip Upgraded.

Installing Requirements with Versions:
gradio--gradio--3.35.2
pandas--pandas--1.5.3
numpy--numpy--1.23.5

Installing packageVersion...
...
packageVersion installed successfully.


Verifying Packages...
No errors encountered during installation.

Detailing All Python Compatibility Issues...
...
Warning: Conflicts Exist.

Installation complete

Please review the output above.
```

## Requirements:
- [NConvert](https://www.xnview.com/en/nconvert); It converts a LOT of formats through command line interface.
- Python 3.10 - If yer like, or edit the Python version in a Global at the top of the batch.
- Python Requirements - They are all integrated into globals near the top of the batch.

### Instructions:
1. Download NConvert, get it from [here](https://www.xnview.com/en/nconvert/#downloads), unpack to a sensible directory.
2. Download the latest release of `NConvert-Batch`, ensure the files are dropped into the same directory as `nconvert.exe`.
3. Run `NConvert-Batch.Bat` by right click `Run as Administrator`, as we are doing remote file writing with scripts.
4. Install Requirements from menu, I worked on it till it worked comprihensively without error, automatically resolving issues. 
5. After requirements are installed, then run `NConvert-Batch` from the menu, and the gradio interface will pop-up in the default browser, while the gradio server shell should be in the background until you close the browser tab. 

### NOTATION:
- If your rare file format is not in the list, the lists are easiy editable, just to replace the extensions with the ones you are going to be using.
- Thanks to DeepSeek v2.5 for its ability to analyze large amounts of output, and implement automated solutions along the lines of my instruction. 
- Thanks to GPT4o with my Personalization, figuring out code for my idea, storing the librarie and versions with a `--`, and converting it to `==` when it is used. Thus reducing, garbage and complication, by 1 file.

## DISCLAIMER:
This software is subject to the terms in License.Txt, covering usage, distribution, and modifications. For full details on your rights and obligations, refer to License.Txt.
