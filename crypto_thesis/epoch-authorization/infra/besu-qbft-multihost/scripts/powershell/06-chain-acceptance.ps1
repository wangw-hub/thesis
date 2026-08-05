$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$infraRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$evidenceDir = Join-Path $infraRoot 'evidence\acceptance'
$logDir = Join-Path $infraRoot 'logs'
New-Item -ItemType Directory -Force -Path $evidenceDir, $logDir | Out-Null

$hosts = @(
    [pscustomobject]@{ Alias = 'besu-validator-1'; Service = 'besu.service'; Rpc = 'http://127.0.0.1:8545' },
    [pscustomobject]@{ Alias = 'besu-validator-2'; Service = 'besu.service'; Rpc = 'http://127.0.0.1:8545' },
    [pscustomobject]@{ Alias = 'besu-validator-3'; Service = 'besu.service'; Rpc = 'http://127.0.0.1:8545' },
    [pscustomobject]@{ Alias = 'besu-validator-4'; Service = 'besu.service'; Rpc = 'http://127.0.0.1:8545' },
    [pscustomobject]@{ Alias = 'experiment-client'; Service = 'besu-rpc.service'; Rpc = 'http://192.168.6.133:8545' }
)
$collector = (Get-Content -Raw -LiteralPath (Join-Path $infraRoot 'scripts\remote\collect-chain-state.sh') -Encoding UTF8) -replace "`r", ''
$validators = Get-Content -Raw -LiteralPath (Join-Path $infraRoot 'validator-public\validators.json') -Encoding UTF8 | ConvertFrom-Json
$expectedValidators = @($validators | ForEach-Object { ([string]$_.address).ToLowerInvariant() } | Sort-Object)
$expectedNodeIds = @($validators | ForEach-Object { [string]$_.node_id })
$rpcNodeId = (Get-Content -Raw -LiteralPath (Join-Path $infraRoot 'validator-public\experiment-client.pub') -Encoding UTF8).Trim()
$expectedGenesis = (Get-FileHash -LiteralPath (Join-Path $infraRoot 'genesis\genesis.json') -Algorithm SHA256).Hash.ToLowerInvariant()
$expectedStatic = (Get-FileHash -LiteralPath (Join-Path $infraRoot 'configs\static-nodes-validators.json') -Algorithm SHA256).Hash.ToLowerInvariant()

function Invoke-RemoteScript {
    param(
        [Parameter(Mandatory)][string]$HostAlias,
        [Parameter(Mandatory)][string]$Payload,
        [Parameter(Mandatory)][string[]]$Arguments
    )
    $escaped = @($Arguments | ForEach-Object { "'" + ($_ -replace "'", "'\''") + "'" })
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = 'ssh.exe'
    $psi.Arguments = "-o BatchMode=yes $HostAlias bash -s -- $($escaped -join ' ')"
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

function Invoke-RemoteCommand {
    param([Parameter(Mandatory)][string]$HostAlias, [Parameter(Mandatory)][string]$Command)
    $output = & ssh.exe -o BatchMode=yes $HostAlias $Command 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Remote command failed on ${HostAlias}: $output" }
    $output
}

function Get-RpcValue {
    param([Parameter(Mandatory)][string]$Text, [Parameter(Mandatory)][string]$Name)
    $match = [regex]::Match($Text, "(?m)^$([regex]::Escape($Name))=(\{.*\})$")
    if (-not $match.Success) { throw "Missing RPC field $Name" }
    $match.Groups[1].Value | ConvertFrom-Json
}

function Collect-State {
    param([Parameter(Mandatory)][string]$Label, [Parameter(Mandatory)][string]$BlockTag)
    $dir = Join-Path $evidenceDir $Label
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    $rows = [System.Collections.Generic.List[object]]::new()
    foreach ($hostInfo in $hosts) {
        $result = Invoke-RemoteScript -HostAlias $hostInfo.Alias -Payload $collector -Arguments @($hostInfo.Service, $hostInfo.Rpc, $BlockTag)
        $path = Join-Path $dir "$($hostInfo.Alias).txt"
        [System.IO.File]::WriteAllText($path, "exit_code=$($result.ExitCode)`n--- stdout ---`n$($result.StdOut)`n--- stderr ---`n$($result.StdErr)", [System.Text.UTF8Encoding]::new($false))
        if ($result.ExitCode -ne 0) { throw "State collection failed for $($hostInfo.Alias); see $path" }
        $block = Get-RpcValue -Text $result.StdOut -Name 'block_number'
        $peer = Get-RpcValue -Text $result.StdOut -Name 'peer_count'
        $validatorSet = Get-RpcValue -Text $result.StdOut -Name 'validators'
        $fixedBlock = Get-RpcValue -Text $result.StdOut -Name 'block_at_tag'
        $nodeMatch = [regex]::Match($result.StdOut, '(?m)^node_id=(?:0x)?([0-9a-f]{128})$')
        $keyHashMatch = [regex]::Match($result.StdOut, '(?m)^private_key_sha256=([0-9a-f]{64})$')
        $errorMatch = [regex]::Match($result.StdOut, '(?m)^recent_error_count=(\d+)$')
        $rows.Add([pscustomobject][ordered]@{
            host = $hostInfo.Alias
            service = $hostInfo.Service
            active = $result.StdOut -match '(?m)^service_active=active$'
            genesis_sha256 = ([regex]::Match($result.StdOut, '(?m)^genesis_sha256=([0-9a-f]{64})$')).Groups[1].Value
            static_nodes_sha256 = ([regex]::Match($result.StdOut, '(?m)^static_nodes_sha256=([0-9a-f]{64})$')).Groups[1].Value
            private_key_sha256 = $keyHashMatch.Groups[1].Value
            node_id = $nodeMatch.Groups[1].Value
            block_number_hex = [string]$block.result
            block_number = [Convert]::ToInt64(([string]$block.result).Substring(2), 16)
            peer_count_hex = [string]$peer.result
            peer_count = [Convert]::ToInt64(([string]$peer.result).Substring(2), 16)
            validators = @($validatorSet.result | ForEach-Object { $_.ToLowerInvariant() } | Sort-Object)
            fixed_block_hash = [string]$fixedBlock.result.hash
            recent_error_count = [int]$errorMatch.Groups[1].Value
            evidence = $path
        })
    }
    $rows | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $dir 'summary.json') -Encoding UTF8
    @($rows)
}

# Select a stable historical height from the public RPC node.
$latest = Invoke-RestMethod -Uri 'http://192.168.6.133:8545' -Method Post -ContentType 'application/json' -Body '{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}' -TimeoutSec 10
$latestNumber = [Convert]::ToInt64(([string]$latest.result).Substring(2), 16)
if ($latestNumber -lt 10) { throw 'Chain height is too low for fixed-height acceptance' }
$fixedHeight = $latestNumber - 5
$fixedTag = '0x' + $fixedHeight.ToString('x')

$before = Collect-State -Label 'before' -BlockTag $fixedTag
Start-Sleep -Seconds 8
$afterGrowth = Collect-State -Label 'growth' -BlockTag $fixedTag

foreach ($row in $afterGrowth) {
    $previous = @($before | Where-Object { $_.host -eq $row.host })[0]
    if (-not $row.active -or $row.block_number -le $previous.block_number) { throw "Block height did not grow on $($row.host)" }
    if ($row.genesis_sha256 -ne $expectedGenesis) { throw "Genesis hash mismatch on $($row.host)" }
    if ($row.static_nodes_sha256 -ne $expectedStatic) { throw "Static-node hash mismatch on $($row.host)" }
    if ($row.peer_count -ne 4) { throw "Unexpected peer count on $($row.host): $($row.peer_count)" }
    if (@(Compare-Object $row.validators $expectedValidators).Count -ne 0) { throw "Validator set mismatch on $($row.host)" }
    if ($row.recent_error_count -ne 0) { throw "Recent service errors found on $($row.host)" }
}
if (@($afterGrowth.fixed_block_hash | Sort-Object -Unique).Count -ne 1) { throw 'Fixed-height block hash differs across nodes' }
if (@($afterGrowth.private_key_sha256 | Sort-Object -Unique).Count -ne 5) { throw 'Node private key hashes are not unique' }
if (@($afterGrowth.node_id | Sort-Object -Unique).Count -ne 5) { throw 'Node IDs are not unique' }
if ($rpcNodeId -in $expectedNodeIds) { throw 'RPC node ID duplicates a Validator' }

# Non-destructive RPC restart acceptance.
$rpcBefore = @($afterGrowth | Where-Object { $_.host -eq 'experiment-client' })[0]
Invoke-RemoteCommand -HostAlias 'experiment-client' -Command 'sudo -n systemctl restart besu-rpc.service'
Start-Sleep -Seconds 30
$afterRpcRestart = Collect-State -Label 'after-rpc-restart' -BlockTag $fixedTag
$rpcAfter = @($afterRpcRestart | Where-Object { $_.host -eq 'experiment-client' })[0]
if (-not $rpcAfter.active -or $rpcAfter.peer_count -ne 4 -or $rpcAfter.block_number -le $rpcBefore.block_number) {
    throw 'RPC node did not recover and advance after restart'
}

# Restart one Validator while the other three continue finalizing blocks.
$networkBefore = @($afterRpcRestart | Where-Object { $_.host -eq 'experiment-client' })[0]
Invoke-RemoteCommand -HostAlias 'besu-validator-4' -Command 'sudo -n systemctl restart besu.service'
Start-Sleep -Seconds 30
$afterValidatorRestart = Collect-State -Label 'after-validator-restart' -BlockTag $fixedTag
$validatorAfter = @($afterValidatorRestart | Where-Object { $_.host -eq 'besu-validator-4' })[0]
$networkAfter = @($afterValidatorRestart | Where-Object { $_.host -eq 'experiment-client' })[0]
if (-not $validatorAfter.active -or $validatorAfter.peer_count -ne 4) { throw 'Validator-4 did not reconnect after restart' }
if ($networkAfter.block_number -le $networkBefore.block_number) { throw 'Network did not continue producing blocks during Validator restart' }
if (($networkAfter.block_number - $validatorAfter.block_number) -gt 2) { throw 'Validator-4 did not catch up after restart' }

$summary = [ordered]@{
    stage = 6
    passed = $true
    chain_id = 2026072801
    fixed_height = $fixedHeight
    fixed_height_hex = $fixedTag
    fixed_block_hash = $afterValidatorRestart[0].fixed_block_hash
    validator_count = 4
    rpc_is_validator = $false
    peer_count_each = 4
    genesis_sha256 = $expectedGenesis
    static_nodes_sha256 = $expectedStatic
    initial_heights = @($before | ForEach-Object { [ordered]@{ host = $_.host; height = $_.block_number } })
    final_heights = @($afterValidatorRestart | ForEach-Object { [ordered]@{ host = $_.host; height = $_.block_number } })
    rpc_restart_passed = $true
    validator_restart_passed = $true
    block_growth_passed = $true
    completed_at_utc = [DateTime]::UtcNow.ToString('o')
}
$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $evidenceDir 'summary.json') -Encoding UTF8
$summary
