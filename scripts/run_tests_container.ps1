# scripts/run_tests_container.ps1
#
# Run the full AlloAgent-v2 test suite inside the Docker image
# with the Biolab data files bind-mounted read-only and a
# temporary --env-file (created outside the repo, deleted
# afterward) carrying ONLY the MINIMAX_* and BIOMNI_* variable
# names (and any alias the tests need) from the host file at
# $env:ALLOAGENT_ENV_SOURCE (a path to the Biolab .env outside
# the repo).
#
# No .env, .omo, or .env.extracted is mounted. The .env file is
# read from the host (NOT mounted) and its MINIMAX_*/BIOMNI_*
# variables are copied into a temp file that is then passed
# via --env-file and deleted at exit.
#
# If RUN_REAL_NETWORK=1 and MINIMAX_API_KEY is absent from the
# extracted variables, the script fails with a clear message
# BEFORE starting the container.

[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path "$PSScriptRoot/..").Path,
    [string]$Image = "alloagent-dev:v4",
    [string]$BiolabHostRoot = "<HOME>\Documents\CPSC\Biolab",
    [string]$LogDir = "$RepoRoot\build_logs",
    [string[]]$ExtraPytestArgs = @()
)

$ErrorActionPreference = "Stop"

if (-not $env:ALLOAGENT_ENV_SOURCE) {
    Write-Host "ERROR: ALLOAGENT_ENV_SOURCE is not set." -ForegroundColor Red
    Write-Host "       Set it to the absolute path of the host .env file" -ForegroundColor Red
    Write-Host "       (e.g., C:<HOME>/Documents/CPSC/Biolab/.env)." -ForegroundColor Red
    Write-Host "       The script reads MINIMAX_* and BIOMNI_* from that file" -ForegroundColor Red
    Write-Host "       and passes them via a temporary --env-file." -ForegroundColor Red
    exit 2
}
$envSource = $env:ALLOAGENT_ENV_SOURCE
if (-not (Test-Path -LiteralPath $envSource)) {
    Write-Host "ERROR: ALLOAGENT_ENV_SOURCE file not found: ${envSource}" -ForegroundColor Red
    exit 2
}

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}
$armLabel = (& git rev-parse --abbrev-ref HEAD 2>$null)
if (-not $armLabel) { $armLabel = "alloagent" }
$logFile = Join-Path $LogDir ("_test_run_arm_{0}_{1}.log" -f $armLabel, $ts)
$tempEnv = [System.IO.Path]::GetTempFileName()
$tempEnvRenamed = [System.IO.Path]::ChangeExtension($tempEnv, ".env")
Move-Item -Path $tempEnv -Destination $tempEnvRenamed -Force
$tempEnv = $tempEnvRenamed

try {
    # Read the host .env file and copy only MINIMAX_* and
    # BIOMNI_* variables (plus any alias in TEST_ENV_ALIASES,
    # comma-separated) to the temp env-file.
    $aliases = @()
    if ($env:TEST_ENV_ALIASES) {
        $aliases = $env:TEST_ENV_ALIASES -split ',' | ForEach-Object { $_.Trim() }
    }
    $allowedPrefixes = @('MINIMAX_', 'BIOMNI_')

    $extractedVars = @()
    $hasMinimaxKey = $false
    foreach ($line in Get-Content ${envSource}) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith('#')) { continue }
        $m = [regex]::Match($trimmed, '^([A-Za-z_][A-Za-z0-9_]*)=(.*)$')
        if (-not $m.Success) { continue }
        $key = $m.Groups[1].Value
        $val = $m.Groups[2].Value
        # Strip surrounding quotes.
        $val = $val.Trim('"', "'")
        $allowed = $false
        foreach ($p in $allowedPrefixes) {
            if ($key.StartsWith($p)) { $allowed = $true; break }
        }
        if (-not $allowed -and $aliases -contains $key) { $allowed = $true }
        if ($allowed) {
            "$key=$val" | Out-File -FilePath $tempEnv -Append -Encoding UTF8
            $extractedVars += $key
            if ($key -eq 'MINIMAX_API_KEY' -and $val) { $hasMinimaxKey = $true }
        }
    }

    if ($env:RUN_REAL_NETWORK -eq '1' -and -not $hasMinimaxKey) {
        Write-Host "ERROR: RUN_REAL_NETWORK=1 but MINIMAX_API_KEY is not" -ForegroundColor Red
        Write-Host "       present in ${envSource} (or its name does not start" -ForegroundColor Red
        Write-Host "       with MINIMAX_/BIOMNI_)." -ForegroundColor Red
        Write-Host "       Extracted variables: $($extractedVars -join ', ')" -ForegroundColor Red
        exit 3
    }

    Write-Host "Extracted $($extractedVars.Count) variable(s) from ${envSource}:"
    foreach ($v in $extractedVars) { Write-Host "  - $v" }

    # Compute mount paths.
    $scoredRunsHost = Join-Path $BiolabHostRoot "eval_ablation\scoring\scored_runs.csv"
    $nullRunsHost = Join-Path $BiolabHostRoot "prep_reports\investigation\null_runs.csv"
    $resultsHost = Join-Path $BiolabHostRoot "results"
    $blocklistHost = Join-Path $BiolabHostRoot "prep_reports\benchmark_blocklist.tsv"

    $runNetwork = if ($env:RUN_REAL_NETWORK) { $env:RUN_REAL_NETWORK } else { "1" }

    # The benchmark suite is optional: the benchmark folder can be deleted
    # from the product tree without affecting the agent.
    $pytestTargets = @("/workspace/tests/")
    if (Test-Path (Join-Path $RepoRoot "benchmark\tests")) {
        $pytestTargets += "/workspace/benchmark/tests/"
    }

    $dockerArgs = @(
        "run", "--rm",
        "--name", "alloagent-tests-$(Get-Random)",
        "--env-file", $tempEnv,
        "-e", "REQUIRE_REAL_DATA=1",
        "-e", "RUN_REAL_NETWORK=$runNetwork",
        "-e", "TMPDIR=/tmp",
        "-e", "HOME=/tmp",
        "-v", "${RepoRoot}:/workspace",
        "-v", "${scoredRunsHost}:/Biolab/eval_ablation/scoring/scored_runs.csv:ro",
        "-v", "${nullRunsHost}:/Biolab/prep_reports/investigation/null_runs.csv:ro",
        "-v", "${resultsHost}:/Biolab/results:ro",
        "-v", "${blocklistHost}:/workspace/Biolab/prep_reports/benchmark_blocklist.tsv:ro",
        $Image,
        "/opt/conda/envs/alloagent_e1/bin/python", "-m", "pytest", $pytestTargets,
            "--no-header", "-q", "-p", "no:cacheprovider"
    ) + $ExtraPytestArgs

    Write-Host "Running: docker $($dockerArgs -join ' ')" -ForegroundColor Cyan
    Write-Host "Log: $logFile" -ForegroundColor Cyan

    & docker @dockerArgs 2>&1 | Tee-Object -FilePath $logFile
    $exitCode = $LASTEXITCODE
} finally {
    Remove-Item -Path $tempEnv -ErrorAction SilentlyContinue
}

Write-Host "Exit code: $exitCode" -ForegroundColor $(if ($exitCode -eq 0) { "Green" } else { "Red" })
Write-Host "Log: $logFile" -ForegroundColor $(if ($exitCode -eq 0) { "Green" } else { "Red" })
exit $exitCode
