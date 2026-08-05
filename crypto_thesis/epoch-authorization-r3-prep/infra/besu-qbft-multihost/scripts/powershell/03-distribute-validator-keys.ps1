$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$infraRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$genesisPath = Join-Path $infraRoot 'genesis\genesis.json'
$validatorsPath = Join-Path $infraRoot 'validator-public\validators.json'
$privateRoot = Join-Path $infraRoot 'private\stage2-generated\besu-qbft-stage2-2026072801\keys'
$validatorScriptPath = Join-Path $infraRoot 'scripts\remote\install-validator-material.sh'
$clientScriptPath = Join-Path $infraRoot 'scripts\remote\install-public-network-material.sh'
$evidenceDir = Join-Path $infraRoot 'evidence\validators'
New-Item -ItemType Directory -Force -Path $evidenceDir | Out-Null

$validators = Get-Content -Raw -LiteralPath $validatorsPath -Encoding UTF8 | ConvertFrom-Json
if ($validators.Count -ne 4) { throw 'Validator manifest must contain exactly four entries' }
$genesisHash = (Get-FileHash -LiteralPath $genesisPath -Algorithm SHA256).Hash.ToLowerInvariant()
$validatorPayload = (Get-Content -Raw -LiteralPath $validatorScriptPath -Encoding UTF8) -replace "`r", ''
$clientPayload = (Get-Content -Raw -LiteralPath $clientScriptPath -Encoding UTF8) -replace "`r", ''

function Invoke-RemoteBash {
    param(
        [Parameter(Mandatory)][string]$HostAlias,
        [Parameter(Mandatory)][string]$Payload,
        [Parameter(Mandatory)][string]$Arguments
    )
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = 'ssh.exe'
    $psi.Arguments = "-o BatchMode=yes $HostAlias bash -s -- $Arguments"
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

$results = [System.Collections.Generic.List[object]]::new()
foreach ($validator in $validators) {
    $hostAlias = [string]$validator.host
    $keyDirectory = Join-Path $privateRoot ([string]$validator.generated_directory)
    $privatePath = Join-Path $keyDirectory 'key.priv'
    $publicPath = Join-Path $keyDirectory 'key.pub'
    if (-not (Test-Path -LiteralPath $privatePath -PathType Leaf)) { throw "Missing private material for $hostAlias" }
    $privateHash = (Get-FileHash -LiteralPath $privatePath -Algorithm SHA256).Hash.ToLowerInvariant()
    $publicHash = (Get-FileHash -LiteralPath $publicPath -Algorithm SHA256).Hash.ToLowerInvariant()
    & scp.exe -q -- $genesisPath "${hostAlias}:/tmp/besu-genesis.json"
    if ($LASTEXITCODE -ne 0) { throw "Genesis transfer failed for $hostAlias" }
    & scp.exe -q -- $privatePath "${hostAlias}:/tmp/besu-validator-key.priv"
    if ($LASTEXITCODE -ne 0) { throw "Private-key transfer failed for $hostAlias" }
    & scp.exe -q -- $publicPath "${hostAlias}:/tmp/besu-validator-key.pub"
    if ($LASTEXITCODE -ne 0) { throw "Public-key transfer failed for $hostAlias" }
    & scp.exe -q -- $validatorsPath "${hostAlias}:/tmp/besu-validators.json"
    if ($LASTEXITCODE -ne 0) { throw "Validator manifest transfer failed for $hostAlias" }

    $execution = Invoke-RemoteBash -HostAlias $hostAlias -Payload $validatorPayload -Arguments "$genesisHash $privateHash $publicHash"
    $logPath = Join-Path $evidenceDir "$hostAlias.txt"
    [System.IO.File]::WriteAllText($logPath, "exit_code=$($execution.ExitCode)`n--- stdout ---`n$($execution.StdOut)`n--- stderr ---`n$($execution.StdErr)", [System.Text.UTF8Encoding]::new($false))
    if ($execution.ExitCode -ne 0) { throw "Validator material installation failed on $hostAlias. See $logPath" }
    $remotePublic = [regex]::Match($execution.StdOut, '(?m)^public_key=([0-9a-f]{128})$')
    $remotePrivateHash = [regex]::Match($execution.StdOut, '(?m)^private_key_sha256=([0-9a-f]{64})$')
    if (-not $remotePublic.Success -or $remotePublic.Groups[1].Value -ne $validator.node_id) {
        throw "Node ID mapping mismatch on $hostAlias"
    }
    if (-not $remotePrivateHash.Success -or $remotePrivateHash.Groups[1].Value -ne $privateHash) {
        throw "Private-key hash mismatch on $hostAlias"
    }
    $results.Add([pscustomobject][ordered]@{
        host = $hostAlias
        address = $validator.address
        node_id = $validator.node_id
        genesis_sha256 = $genesisHash
        private_key_sha256 = $privateHash
        public_key_sha256 = $publicHash
        exit_code = $execution.ExitCode
        evidence = $logPath
        evidence_sha256 = (Get-FileHash -LiteralPath $logPath -Algorithm SHA256).Hash.ToLowerInvariant()
    })
    $results | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $evidenceDir 'key-distribution.json') -Encoding UTF8
}

& scp.exe -q -- $genesisPath 'experiment-client:/tmp/besu-genesis.json'
if ($LASTEXITCODE -ne 0) { throw 'Genesis transfer failed for experiment-client' }
& scp.exe -q -- $validatorsPath 'experiment-client:/tmp/besu-validators.json'
if ($LASTEXITCODE -ne 0) { throw 'Validator manifest transfer failed for experiment-client' }
$clientExecution = Invoke-RemoteBash -HostAlias 'experiment-client' -Payload $clientPayload -Arguments $genesisHash
$clientLogPath = Join-Path $evidenceDir 'experiment-client.txt'
[System.IO.File]::WriteAllText($clientLogPath, "exit_code=$($clientExecution.ExitCode)`n--- stdout ---`n$($clientExecution.StdOut)`n--- stderr ---`n$($clientExecution.StdErr)", [System.Text.UTF8Encoding]::new($false))
if ($clientExecution.ExitCode -ne 0 -or $clientExecution.StdOut -notmatch '(?m)^validator_private_key_present=false$') {
    throw "RPC public material installation failed or Validator private key exists. See $clientLogPath"
}

if (@($results.private_key_sha256 | Select-Object -Unique).Count -ne 4) { throw 'Distributed private-key hashes are not unique' }
if (@($results.node_id | Select-Object -Unique).Count -ne 4) { throw 'Distributed node IDs are not unique' }
$summary = [ordered]@{
    stage = 3
    passed = $true
    validator_count = 4
    validator_private_hashes_unique = $true
    validator_node_ids_unique = $true
    genesis_sha256 = $genesisHash
    experiment_client_has_validator_private_key = $false
    completed_at_utc = [DateTime]::UtcNow.ToString('o')
}
$summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $evidenceDir 'summary.json') -Encoding UTF8
$summary
