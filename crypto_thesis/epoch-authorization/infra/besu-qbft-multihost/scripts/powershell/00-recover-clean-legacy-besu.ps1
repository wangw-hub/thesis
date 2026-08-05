$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$remoteScriptPath = Join-Path $root 'scripts\remote\cleanup-legacy-besu.sh'
$evidenceDir = Join-Path $root 'evidence\recovery'
New-Item -ItemType Directory -Force -Path $evidenceDir | Out-Null

$targets = @('besu-validator-1', 'besu-validator-2', 'besu-validator-3', 'besu-validator-4')
$scriptText = (Get-Content -Raw -LiteralPath $remoteScriptPath -Encoding UTF8) -replace "`r", ''
$results = @()

function Invoke-RemoteBash {
    param([Parameter(Mandatory)][string]$HostAlias, [Parameter(Mandatory)][string]$Payload)

    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = 'ssh.exe'
    $psi.Arguments = "$HostAlias bash -s --"
    $psi.UseShellExecute = $false
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $psi
    [void]$process.Start()
    $process.StandardInput.Write($Payload)
    $process.StandardInput.Close()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    return [pscustomobject]@{ ExitCode = $process.ExitCode; StdOut = $stdout; StdErr = $stderr }
}

foreach ($hostAlias in $targets) {
    $started = [DateTime]::UtcNow.ToString('o')
    $result = Invoke-RemoteBash -HostAlias $hostAlias -Payload $scriptText
    $record = "host=$hostAlias`nstarted_at_utc=$started`nexit_code=$($result.ExitCode)`n--- stdout ---`n$($result.StdOut)`n--- stderr ---`n$($result.StdErr)"
    $recordPath = Join-Path $evidenceDir "$hostAlias-cleanup.txt"
    [System.IO.File]::WriteAllText($recordPath, $record, [System.Text.UTF8Encoding]::new($false))
    $results += [pscustomobject]@{ host = $hostAlias; exit_code = $result.ExitCode; evidence = $recordPath; sha256 = (Get-FileHash -LiteralPath $recordPath -Algorithm SHA256).Hash }
    if ($result.ExitCode -ne 0) {
        $results | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $evidenceDir 'summary.json') -Encoding UTF8
        throw "Legacy Besu cleanup failed on $hostAlias. See $recordPath"
    }
}

$summaryPath = Join-Path $evidenceDir 'summary.json'
$results | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $summaryPath -Encoding UTF8
$results
