# ChEMBL download retry loop.
#
# scripts/fetch_chembl.py streams the 5.5 GB archive and aborts with
# "size mismatch" whenever the connection drops part-way through. The
# helper keeps the partial file (`.part`) and resumes with an HTTP
# Range on the next invocation, so progress is cumulative. This loop
# simply re-invokes it until the archive lands or the attempt budget
# is exhausted. It NEVER deletes a .part file.
param(
    [int]$MaxAttempts = 40
)

$repo = "<HOME>\Documents\CPSC\AlloAgent-v2"
$final = Join-Path $repo "data\chembl\chembl_37_sqlite.tar.gz"
$part = "$final.part"
$expected = 5764252857

for ($i = 1; $i -le $MaxAttempts; $i++) {
    if (Test-Path -LiteralPath $final) {
        $len = (Get-Item -LiteralPath $final).Length
        if ($len -eq $expected) {
            Write-Host "[$(Get-Date -Format HH:mm:ss)] COMPLETE after $i attempt(s): $len bytes"
            exit 0
        }
    }

    $have = 0
    if (Test-Path -LiteralPath $part) { $have = (Get-Item -LiteralPath $part).Length }
    $pct = [math]::Round($have / $expected * 100, 1)
    Write-Host "[$(Get-Date -Format HH:mm:ss)] attempt $i : have $([int]$have) bytes ($pct%) - resuming"

    Push-Location $repo
    try {
        & python scripts/fetch_chembl.py --download --out ./data/chembl 2>&1 |
            Select-Object -Last 2 | ForEach-Object { Write-Host "    $_" }
    } catch {
        Write-Host "    attempt error: $($_.Exception.Message)"
    } finally {
        Pop-Location
    }
    Start-Sleep -Seconds 5
}

Write-Host "exhausted $MaxAttempts attempts"
exit 1