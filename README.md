# NConvert-Batch
Status: Updating to, fix and enhance, now; critical error found.

## Description:
Its a Python Gradio interface for converting ANY image format to ANY imgage format, even rare ones like `.pspimage`, all made possible through `NConvert` binary command line tool. The program provides a user-friendly menu to set the source folder, input file format, and desired output format. The scripts ensures efficient and seamless conversion and management of image files, making it a practical tool for users needing to process multiple `.pspimage` into a common format such as `.jpg`.

## Features:
- **Multiple Formats**: The Gradio interface limited to 10, but they can be edited in the `.py` script. 
- **Interactive Menu**: Utilizing your standard text-based menu for effective configuration.
- **Batch Conversion**: All specified format files in, specified folder and its subfolders, to desired format.
- **Automatic Report**: Provides a summary of the total number of successfully converted files.
- **Deletion Option**: Offers the option to delete original files.
- **Error Handling**: Displays errors for any files that fail to convert.

### Preview:
- The Video Demonstration on YouTube (for v1.00-Final)...
<br>[![NConvert-Batch on YouTube](./media/wisetime_youtube.jpg)](https://www.youtube.com/watch?v=ECydHjJ04U4)
- The NConvert-Batch Gradio WebUi...
![Alternative text](https://github.com/wiseman-timelord/NConvertBatch/blob/main/media/gradio_interface.jpg)
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

## Requirements:
- [NConvert](https://www.xnview.com/en/nconvert) - ~500 image formats supported (installed by installer).
- Python 3.12 - Edit the Global if you want other versions, but not sure libraries will be compatible.
- Python Requirements - Installed from the created `.\requirements.txt`, you can inspect them there if you like.

### Instructions:
1. Run `NConvert-Batch.Bat` by right click `Run as Administrator`, as we are doing, complex recursive file operations under the interface and downloading/unpacking NConvert in the installer.
2. Install Requirements from menu through option `2`, it will run `.\installer.py`, which will install everything you require via direct links/pip. 
3. After requirements are installed, then run `NConvert-Batch` from `1.` on the batch menu, and if the gradio interface does not pop-up in the default browser, then right click the server address and then click open.. 
4. Configure the settings in the browser interface, if your file format preference is not in the list, then edit relevant lists in python script by replace appropriate extension text.
7. When all setting are correct, then 1st ensure you noticed the `Delete Original Files?` tickbox, and if you did, then click `Start Conversion`, and it will convert the files, as  you have specified, over-writing as it goes.
8. Check the image folders, I saved you hours of work, now isnt that worth a little donation.

### NOTATION:
- De-Confustion... Meaning 1: "Batch" - a `*.bat` Windows Batch file. Meaning 2: "Batch" - Repetitive actions done together in sequence. 
- Thanks to, DeepSeek v2.5-v3 and GPT-4o, for assistance in programming . 
- Thanks to [XnView Software](https://www.xnview.com/en/) for, creating and hosting, [NConvert](https://www.xnview.com/en/nconvert/).

## DISCLAIMER:
This software is subject to the terms in License.Txt, covering usage, distribution, and modifications. For full details on your rights and obligations, refer to License.Txt.
NConvert is not made by Wiseman-Timelord, only the, Gradio Interface and Batch Launcher/Installer, is; Terms and Conditions, for NConvert still apply.
