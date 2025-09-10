$ErrorActionPreference = "Stop"

# Load ~assemblies~ and determine format integer.
#$wdTypes = Add-Type -AssemblyName 'Microsoft.Office.Interop.Word' -Passthru
#$wdSaveFormat = $wdTypes | Where {$_.Name -eq "wdSaveFormat"}
#$wdSaveFormatInt = $wdSaveFormat::wdFormatDocumentDefault.value__

#

# AI says necessary to load base office assemblies first.
Add-Type -Path "$env:WINDIR\assembly\GAC_MSIL\office\*\office.dll" -PassThru   

# Find Microsoft Word assemblies.
$wdWTypes = Get-ChildItem -Path "$env:windir\assembly" -Recurse -Filter "Microsoft.Office.Interop.Word*" -File | ForEach-Object {
    Add-Type -LiteralPath $_.FullName -PassThru
}

# Select that assembly that ~specifies~ the save format.
$wdSaveFormat = $wdWTypes | Where {$_.Name -eq "wdSaveFormat"}

# Get Default save format int.
$wdSaveFormatInt = $wdSaveFormat::wdFormatDocumentDefault.value__
# [ALT] save to HTML
# $wdSaveFormatInt = $wdSaveFormat::wdFormatHTML.value__




conda activate dsBase

## THIS HAS TO BE RUN ON A LOCAL MACHINE ##

#$reportsPath="data\reference_documents\ESDC_competency_framework\systems_and_architecture"

$word = New-Object -ComObject Word.application
#$docxType = 12

# select those html documents missing a corresponding docx
#$existingExcelDocs=Get-ChildItem $reportsPath\*.docx | foreach {$_.FullName}



#$htmlsMissingDocxVersion=find data/ -type f | grep ".mhtml$"
#$htmlsMissingDocxVersion=Get-ChildItem $reportsPath\*.mhtml 
#| Where-Object {-not $existingExcelDocs.Contains($_.FullName.Replace("mhtml",'docx'))}
$extensionEnd = ".pdf"
$mhtmlDocs = Get-ChildItem -Recurse -Path .\data\ | Where-Object {$_.Extension.Equals("$extensionEnd")}
echo $mhtmlDocs
foreach ($doc in $mhtmlDocs) {
    echo $doc
    $documentPath = $doc.FullName
    $wordOutputPath = $documentPath.Replace("$extensionEnd", ".docx")
    $txtOutputPath = $documentPath.Replace("$extensionEnd", ".md")
    #$wordOutputPath = $documentPath.Replace(".html", ".docx")

    echo $wordOutputPath

    $document = $word.Documents.Open("$documentPath")
    $document.SaveAs($wordOutputPath, $wdSaveFormatInt)
    $document.Close()

    pandoc -f docx -t markdown_strict -o $txtOutputPath $wordOutputPath
    rm $wordOutputPath
}
$word.quit()

