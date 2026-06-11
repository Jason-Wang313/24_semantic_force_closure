
$ErrorActionPreference = 'Continue'
$PaperDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $PaperDir
$Paper = Join-Path $Root 'paper'
$DownloadsPdf = 'C:\Users\wangz\Downloads\24.pdf'
$Status = Join-Path $Paper 'build_status.txt'
Set-Content -LiteralPath $Status -Value "Build started at $((Get-Date).ToString('o'))" -Encoding UTF8
Push-Location $Paper
function Run-Step {
    param([string]$Name, [string[]]$StepArgs)
    Add-Content -LiteralPath $Status -Value "RUN $($Name): $($StepArgs -join ' ')"
    $output = & $StepArgs[0] @($StepArgs[1..($StepArgs.Length-1)]) 2>&1
    $code = $LASTEXITCODE
    $output | Set-Content -LiteralPath "$Name.output.txt" -Encoding UTF8
    Add-Content -LiteralPath $Status -Value "EXIT $($Name): $code"
    return $code
}
$c1 = Run-Step 'pdflatex1' @('pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex')
$cb = Run-Step 'bibtex' @('bibtex','main')
$c2 = Run-Step 'pdflatex2' @('pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex')
$c3 = Run-Step 'pdflatex3' @('pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex')
Pop-Location
if (($c1 -eq 0) -and ($cb -eq 0) -and ($c2 -eq 0) -and ($c3 -eq 0) -and (Test-Path -LiteralPath (Join-Path $Paper 'main.pdf'))) {
    Copy-Item -LiteralPath (Join-Path $Paper 'main.pdf') -Destination $DownloadsPdf -Force
    Add-Content -LiteralPath $Status -Value "PDF copied to $DownloadsPdf"
    Add-Content -LiteralPath $Status -Value "Build finished at $((Get-Date).ToString('o'))"
    exit 0
}
Add-Content -LiteralPath $Status -Value "Build failed or PDF missing at $((Get-Date).ToString('o'))"
exit 1
