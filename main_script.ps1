# Set default values
$folderLocation = "X:\PathTo\YourFolder"
$formatFrom = "pspimage"
$formatTo = "jpeg"  # Corrected format for JPEG output
$nconvertPath = ".\nconvert.exe"

function Show-Menu {
    Clear-Host
    Write-Host "NConvert Batch-Sub Convert"
    Write-Host
    Write-Host "1. Folder Location ($folderLocation)"
    Write-Host "2. Image Format From ($formatFrom)"
    Write-Host "3. Image Format To ($formatTo)"
    Write-Host "-------------------"
    Write-Host "Select; Options = 1-3, Start = S, Exit = X: "
}

function Set-FolderLocation {
    Write-Host "Enter folder location (e.g., X:\...):"
    $global:folderLocation = Read-Host
}

function Set-FormatFrom {
    Write-Host "Select source image format (pspimage, jpg, png, bmp):"
    $global:formatFrom = Read-Host
}

function Set-FormatTo {
    Write-Host "Select target image format (jpeg, png, bmp):"
    $global:formatTo = Read-Host
}

function Start-Conversion {
    if (-not (Test-Path $folderLocation)) {
        Write-Host "Please set a valid folder location."
        Pause
        return
    }

    Write-Host "Converting files in $folderLocation from $formatFrom to $formatTo format..."

    $files = Get-ChildItem -Path $folderLocation -Recurse -Filter *.$formatFrom
    if ($files.Count -eq 0) {
        Write-Host "No files with the extension $formatFrom found in the specified location."
        Pause
        return
    }

    $convertedCount = 0
    foreach ($file in $files) {
        $inputFile = $file.FullName
        $outputFile = [System.IO.Path]::ChangeExtension($inputFile, $formatTo)

        Write-Host "Processing $inputFile"
        $command = "$nconvertPath -out $formatTo -o `"$outputFile`" `"$inputFile`""
        Write-Host $command  # Display the command for debugging
        Invoke-Expression $command

        if ($LASTEXITCODE -eq 0) {
            Write-Host "Successfully processed $inputFile"
            $convertedCount++
        } else {
            Write-Host "Error processing $inputFile"
        }
    }

    Write-Host "Conversion completed. Total files converted: $convertedCount"

    $deleteOriginals = Read-Host "Delete Original Files? Y/N:"
    if ($deleteOriginals -eq "Y") {
        foreach ($file in $files) {
            Remove-Item -Path $file.FullName -Force
            Write-Host "Deleted $($file.FullName)"
        }
        Write-Host "Original files deleted."
    } else {
        Write-Host "Original files retained."
    }
    Pause
}

while ($true) {
    Show-Menu
    $choice = Read-Host

    switch ($choice) {
        "1" { Set-FolderLocation }
        "2" { Set-FormatFrom }
        "3" { Set-FormatTo }
        "S" { Start-Conversion }
        "X" { exit }
        default { Write-Host "Invalid option. Please try again." }
    }
}
