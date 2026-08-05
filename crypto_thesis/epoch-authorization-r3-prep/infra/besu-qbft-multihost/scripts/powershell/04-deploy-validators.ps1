param([switch]$AcceptanceOnly)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$infraRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$staticPath = Join-Path $infraRoot 'configs\static-nodes-validators.json'
$servicePath = Join-Path $infraRoot 'systemd\besu.service'
$installScriptPath = Join-Path $infraRoot 'scripts\remote\install-validator-service.sh'
$acceptScriptPath = Join-Path $infraRoot 'scripts\remote\collect-validator-acceptance.sh'
$validatorsPath = Join-Path $infraRoot 'validator-public\validators.json'
$evidenceDir = Join-Path $infraRoot 'evidence\validators\deployment'
New-Item -ItemType Directory -Force -Path $evidenceDir | Out-Null
$validators = Get-Content -Raw -LiteralPath $validatorsPath -Encoding UTF8 | ConvertFrom-Json
$installPayload = (Get-Content -Raw -LiteralPath $installScriptPath -Encoding UTF8) -replace "`r", ''
$acceptPayload = (Get-Content -Raw -LiteralPath $acceptScriptPath -Encoding UTF8) -replace "`r", ''
$expectedGenesis = (Get-FileHash -LiteralPath (Join-Path $infraRoot 'genesis\genesis.json') -Algorithm SHA256).Hash.ToLowerInvariant()

function Invoke-RemoteBash {
    param([Parameter(Mandatory)][string]$HostAlias, [Parameter(Mandatory)][string]$Payload)
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
    $process.StandardInput.Write($Payload)
    $process.StandardInput.Close()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    [pscustomobject]@{ ExitCode = $process.ExitCode; StdOut = $stdout; StdErr = $stderr }
}

if (-not $AcceptanceOnly) {
    foreach ($validator in $validators) {
        $hostAlias = [string]$validator.host
        $configPath = Join-Path $infraRoot "configs\$hostAlias.toml"
        & scp.exe -q -- $configPath "${hostAlias}:/tmp/besu-validator.toml"
        if ($LASTEXITCODE -ne 0) { throw "Config transfer failed for $hostAlias" }
        & scp.exe -q -- $staticPath "${hostAlias}:/tmp/static-nodes.json"
        if ($LASTEXITCODE -ne 0) { throw "Static-node transfer failed for $hostAlias" }
        & scp.exe -q -- $servicePath "${hostAlias}:/tmp/besu.service"
        if ($LASTEXITCODE -ne 0) { throw "Service transfer failed for $hostAlias" }
        $execution = Invoke-RemoteBash -HostAlias $hostAlias -Payload $installPayload
        $logPath = Join-Path $evidenceDir "$hostAlias-install.txt"
        [System.IO.File]::WriteAllText($logPath, "exit_code=$($execution.ExitCode)`n$($execution.StdOut)`n$($execution.StdErr)", [System.Text.UTF8Encoding]::new($false))
        if ($execution.ExitCode -ne 0) { throw "Validator deployment failed on $hostAlias. See $logPath" }
    }
    Start-Sleep -Seconds 16
} else {
    Start-Sleep -Seconds 2
}
$results = [System.Collections.Generic.List[object]]::new()
foreach ($validator in $validators) {
    $hostAlias = [string]$validator.host
    $execution = Invoke-RemoteBash -HostAlias $hostAlias -Payload $acceptPayload
    $logPath = Join-Path $evidenceDir "$hostAlias-acceptance.txt"
    [System.IO.File]::WriteAllText($logPath, "exit_code=$($execution.ExitCode)`n--- stdout ---`n$($execution.StdOut)`n--- stderr ---`n$($execution.StdErr)", [System.Text.UTF8Encoding]::new($false))
    $blockMatch = [regex]::Match($execution.StdOut, '(?m)^eth_blockNumber=.*"result":"(0x[0-9a-f]+)"')
    $peerMatch = [regex]::Match($execution.StdOut, '(?m)^net_peerCount=.*"result":"(0x[0-9a-f]+)"')
    $passed = $execution.ExitCode -eq 0 -and
        $execution.StdOut -match '(?m)^service_active=active$' -and
        $execution.StdOut -match '(?m)^process_user=besu$' -and
        $execution.StdOut -match '(?m)^p2p_listener=.*:30303$' -and
        $execution.StdOut -match '(?m)^rpc_listener=.*127\.0\.0\.1.*:8545$' -and
        $execution.StdOut -match "(?m)^genesis_sha256=$expectedGenesis$" -and
        $execution.StdOut -match "(?m)^node_id=$($validator.node_id)$" -and
        $blockMatch.Success -and $peerMatch.Success
    $results.Add([pscustomobject][ordered]@{
        host = $hostAlias
        passed = $passed
        block_number_hex = if ($blockMatch.Success) { $blockMatch.Groups[1].Value } else { $null }
        peer_count_hex = if ($peerMatch.Success) { $peerMatch.Groups[1].Value } else { $null }
        evidence = $logPath
        evidence_sha256 = (Get-FileHash -LiteralPath $logPath -Algorithm SHA256).Hash.ToLowerInvariant()
    })
}
$results | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $evidenceDir 'summary.json') -Encoding UTF8
if (@($results | Where-Object { -not $_.passed }).Count -gt 0) {
    throw "Stage 4 acceptance failed. See $(Join-Path $evidenceDir 'summary.json')"
}
if (@($results | Where-Object { [Convert]::ToInt64($_.block_number_hex.Substring(2), 16) -lt 1 }).Count -gt 0) {
    throw 'QBFT chain has not produced blocks'
}
$results
