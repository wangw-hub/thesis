param([switch]$AcceptanceOnly)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$infraRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$configPath = Join-Path $infraRoot 'configs\experiment-client.toml'
$staticPath = Join-Path $infraRoot 'configs\static-nodes-rpc.json'
$servicePath = Join-Path $infraRoot 'systemd\besu-rpc.service'
$installScriptPath = Join-Path $infraRoot 'scripts\remote\install-rpc-service.sh'
$acceptScriptPath = Join-Path $infraRoot 'scripts\remote\collect-rpc-acceptance.sh'
$validatorsPath = Join-Path $infraRoot 'validator-public\validators.json'
$evidenceDir = Join-Path $infraRoot 'evidence\rpc'
New-Item -ItemType Directory -Force -Path $evidenceDir | Out-Null
$installPayload = (Get-Content -Raw -LiteralPath $installScriptPath -Encoding UTF8) -replace "`r", ''
$acceptPayload = (Get-Content -Raw -LiteralPath $acceptScriptPath -Encoding UTF8) -replace "`r", ''
$validators = Get-Content -Raw -LiteralPath $validatorsPath -Encoding UTF8 | ConvertFrom-Json
$expectedGenesis = (Get-FileHash -LiteralPath (Join-Path $infraRoot 'genesis\genesis.json') -Algorithm SHA256).Hash.ToLowerInvariant()

function Invoke-RemoteBash {
    param([Parameter(Mandatory)][string]$Payload)
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = 'ssh.exe'
    $psi.Arguments = '-o BatchMode=yes experiment-client bash -s --'
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
    & scp.exe -q -- $configPath 'experiment-client:/tmp/besu-rpc.toml'
    if ($LASTEXITCODE -ne 0) { throw 'RPC config transfer failed' }
    & scp.exe -q -- $staticPath 'experiment-client:/tmp/static-nodes-rpc.json'
    if ($LASTEXITCODE -ne 0) { throw 'RPC static-node transfer failed' }
    & scp.exe -q -- $servicePath 'experiment-client:/tmp/besu-rpc.service'
    if ($LASTEXITCODE -ne 0) { throw 'RPC service transfer failed' }
    $install = Invoke-RemoteBash -Payload $installPayload
    $installLogPath = Join-Path $evidenceDir 'install.txt'
    [System.IO.File]::WriteAllText($installLogPath, "exit_code=$($install.ExitCode)`n$($install.StdOut)`n$($install.StdErr)", [System.Text.UTF8Encoding]::new($false))
    if ($install.ExitCode -ne 0) { throw "RPC deployment failed. See $installLogPath" }

    $nodeMatch = [regex]::Match($install.StdOut, '(?m)^rpc_node_id=([0-9a-f]{128})$')
    if (-not $nodeMatch.Success) { throw 'RPC node ID is missing from installation evidence' }
    $rpcNodeId = $nodeMatch.Groups[1].Value
    [System.IO.File]::WriteAllText((Join-Path $infraRoot 'validator-public\experiment-client.pub'), "$rpcNodeId`n", [System.Text.UTF8Encoding]::new($false))
} else {
    $rpcNodeId = (Get-Content -Raw -LiteralPath (Join-Path $infraRoot 'validator-public\experiment-client.pub') -Encoding UTF8).Trim().ToLowerInvariant()
}
$validatorNodeIds = @($validators | ForEach-Object { [string]$_.node_id })
if ($rpcNodeId -notmatch '^[0-9a-f]{128}$' -or $rpcNodeId -in $validatorNodeIds) {
    throw 'RPC node ID is invalid or duplicates a Validator'
}

Start-Sleep -Seconds $(if ($AcceptanceOnly) { 20 } else { 12 })
$acceptance = Invoke-RemoteBash -Payload $acceptPayload
$acceptLogPath = Join-Path $evidenceDir 'acceptance.txt'
[System.IO.File]::WriteAllText($acceptLogPath, "exit_code=$($acceptance.ExitCode)`n--- stdout ---`n$($acceptance.StdOut)`n--- stderr ---`n$($acceptance.StdErr)", [System.Text.UTF8Encoding]::new($false))
if ($acceptance.ExitCode -ne 0) { throw "RPC acceptance collection failed. See $acceptLogPath" }

$chainMatch = [regex]::Match($acceptance.StdOut, '(?m)^eth_chainId=.*"result":"(0x[0-9a-f]+)"')
$blockMatch = [regex]::Match($acceptance.StdOut, '(?m)^eth_blockNumber=.*"result":"(0x[0-9a-f]+)"')
$peerMatch = [regex]::Match($acceptance.StdOut, '(?m)^net_peerCount=.*"result":"(0x[0-9a-f]+)"')
$validatorMatch = [regex]::Match($acceptance.StdOut, '(?m)^qbft_getValidatorsByBlockNumber=(\{.*\})$')
if (-not $chainMatch.Success -or [Convert]::ToInt64($chainMatch.Groups[1].Value.Substring(2), 16) -ne 2026072801) { throw 'RPC chainId mismatch' }
if (-not $blockMatch.Success -or [Convert]::ToInt64($blockMatch.Groups[1].Value.Substring(2), 16) -lt 1) { throw 'RPC node has no chain height' }
if (-not $peerMatch.Success -or [Convert]::ToInt64($peerMatch.Groups[1].Value.Substring(2), 16) -lt 4) { throw 'RPC node has fewer than four peers' }
if (-not $validatorMatch.Success) { throw 'RPC validator-set response is missing' }
$validatorResponse = $validatorMatch.Groups[1].Value | ConvertFrom-Json
$observedValidators = @($validatorResponse.result | ForEach-Object { $_.ToLowerInvariant() } | Sort-Object)
$expectedValidators = @($validators | ForEach-Object { ([string]$_.address).ToLowerInvariant() } | Sort-Object)
$validatorDifferences = @(Compare-Object $observedValidators $expectedValidators)
if ($validatorDifferences.Count -ne 0) { throw 'RPC Validator set differs from frozen manifest' }

$request = @{
    Uri = 'http://192.168.6.133:8545'
    Method = 'Post'
    ContentType = 'application/json'
    Body = '{"jsonrpc":"2.0","id":1,"method":"web3_clientVersion","params":[]}'
    TimeoutSec = 10
}
$windowsResponse = Invoke-RestMethod @request
$windowsPath = Join-Path $evidenceDir 'windows-web3-clientVersion.json'
$windowsResponse | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $windowsPath -Encoding UTF8

$summary = [ordered]@{
    stage = 5
    passed = $true
    rpc_node_id = $rpcNodeId
    rpc_is_validator = $false
    chainId = 2026072801
    block_number_hex = $blockMatch.Groups[1].Value
    peer_count_hex = $peerMatch.Groups[1].Value
    validator_count = $observedValidators.Count
    rpc_binding = '192.168.6.133:8545'
    windows_rpc_access = $true
    completed_at_utc = [DateTime]::UtcNow.ToString('o')
}
$summary | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $evidenceDir 'summary.json') -Encoding UTF8
$summary
