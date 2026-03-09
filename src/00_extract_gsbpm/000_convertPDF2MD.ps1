$ErrorActionPreference = "Stop"

## REQUIRES POWERSHELL 7 ##

## Load ~assemblies~ and determine integer that specifies formats in MS Word. ##

# AI says necessary to load base office assemblies first.
$baseAssemblies = Add-Type -Path "$env:WINDIR\assembly\GAC_MSIL\office\*\office.dll" -PassThru   

# Find Microsoft Word assemblies, and add to Powershell types.
$wdWTypes = Get-ChildItem -Path "$env:windir\assembly" -Recurse -Filter "Microsoft.Office.Interop.Word*" -File | ForEach-Object {
    Add-Type -LiteralPath $_.FullName -PassThru
}

# Select that assembly that ~specifies~ the save format.
$wdSaveFormat = $wdWTypes | Where {$_.Name -eq "wdSaveFormat"}

# Get Default save format int.
$wdSaveFormatInt = $wdSaveFormat::wdFormatDocumentDefault.value__
# [ALT] save to HTML
#$wdSaveFormatInt = $wdSaveFormat::wdFormatHTML.value__





## OPEN MS OFFICE, LOOP OVER INPUT DOCMENTS AND SAVE-AS FOR EACH. ##

conda activate dsBase

## THIS HAS TO BE RUN ON A LOCAL MACHINE ##

$word = New-Object -ComObject Word.application
#$docxType = 12

# specify input/staging extensions.
$extensionEnd = ".pdf"
$extensionIntermediate = ".docx"

# Collect all input items
$inputDocs = Get-ChildItem -Recurse -Path .\data\0000_raw\ | Where-Object {$_.Extension.Equals("$extensionEnd")}
foreach ($doc in $inputDocs) {
    echo $doc

    # Create staging path.
    $documentPath = $doc.FullName
    $wordOutputPath = $documentPath.Replace("$extensionEnd", "$extensionIntermediate").replace("0000_raw", "0001_staging")


    # Open input file using Microsoft Word/Powerpoint/Etc., save-as output type.
    $document = $word.Documents.Open("$documentPath")
    $document.SaveAs($wordOutputPath, $wdSaveFormatInt)
    $document.Close()

    echo $wordOutputPath

    # Then convert to Strict Markdown.
    $txtOutputPath = $documentPath.Replace("$extensionEnd", ".md").replace("0000_raw", "0002_output")
    $HOME\.conda\envs\dsBase\Library\bin\pandoc.exe -t markdown_strict -o $txtOutputPath $wordOutputPath

    # Optional clean-up
    #rm $wordOutputPath
}
$word.quit()

