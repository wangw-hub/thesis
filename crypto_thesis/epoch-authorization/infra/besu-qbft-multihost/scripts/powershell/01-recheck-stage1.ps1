$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$infraRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$remoteScriptPath = Join-Path $infraRoot 'scripts\remote\recheck-stage1.sh'
$evidenceDir = Join-Path $infraRoot 'evidence\installation\recheck'
$hosts = @('besu-validator-1', 'besu-validator-2', 'besu-validator-3', 'besu-validator-4', 'experiment-client')
New-Item -ItemType Directory -Force -Path $evidenceDir | Out-Null
$payload = (Get-Content -Raw -LiteralPath $remoteScriptPath -Encoding UTF8) -replace "`r", ''

function Invoke-RemoteBash {
    param([Parameter(Mandatory)][string]$HostAlias, [Parameter(Mandatory)][string]$ScriptText)
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = 'ssh.exe'
    $psi.Arguments = "-o BatchMode=yes $HostAlias bash -s --"
    $psi.UseShellExecute = $false
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $psi
    [void]$process.Start()
    $process.StandardInput.Write($ScriptText)
    $process.StandardInput.Close()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    [pscustomobject]@{ ExitCode = $process.ExitCode; StdOut = $stdout; StdErr = $stderr }
}

$results = foreach ($hostAlias in $hosts) {
    $execution = Invoke-RemoteBash -HostAlias $hostAlias -ScriptText $payload
    $recordPath = Join-Path $evidenceDir "$hostAlias.txt"
    $record = "host=$hostAlias`nexit_code=$($execution.ExitCode)`n--- stdout ---`n$($execution.StdOut)`n--- stderr ---`n$($execution.StdErr)"
    [System.IO.File]::WriteAllText($recordPath, $record, [System.Text.UTF8Encoding]::new($false))
    $passed = $execution.ExitCode -eq 0 -and
        $execution.StdOut -match '(?m)^java_version=.*version "21\.' -and
        $execution.StdOut -match '(?m)^besu_version=besu/v26\.5\.0/' -and
        $execution.StdOut -match '(?m)^besu_target=/opt/besu-26\.5\.0$' -and
        $execution.StdOut -match '(?m)^besu_user=uid=.*\(besu\)' -and
        $execution.StdOut -match '(?m)^unexpected_processes=false$' -and
        $execution.StdOut -match '(?m)^unexpected_units=false$'
    [pscustomobject]@{
        host = $hostAlias
        exit_code = $execution.ExitCode
        passed = $passed
        evidence = $recordPath
        evidence_sha256 = (Get-FileHash -LiteralPath $recordPath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}

$summaryPath = Join-Path $evidenceDir 'summary.json'
$results | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $summaryPath -Encoding UTF8
if (@($results | Where-Object { -not $_.passed }).Count -gt 0) {
    throw "Stage 1 recheck failed. See $summaryPath"
}
$results
