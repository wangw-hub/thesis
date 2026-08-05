$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$infraRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$repoRoot = Split-Path -Parent (Split-Path -Parent $infraRoot)
$evidenceDir = Join-Path $infraRoot "evidence\infrastructure-freeze"
New-Item -ItemType Directory -Force -Path $evidenceDir | Out-Null

function Invoke-Rpc {
    param(
        [Parameter(Mandatory)][string]$Method,
        [object[]]$Params = @()
    )
    $request = @{ jsonrpc = "2.0"; id = 1; method = $Method; params = $Params } |
        ConvertTo-Json -Compress
    $arguments = @{
        Uri = "http://192.168.6.133:8545"
        Method = "Post"
        ContentType = "application/json"
        Body = $request
        TimeoutSec = 10
    }
    Invoke-RestMethod @arguments
}

$gitStatus = @(git -C $repoRoot status --short)
$tracked = @(git -C $repoRoot -c core.quotepath=false ls-files)
$cachedDiff = @(git -C $repoRoot diff --cached --name-only)
$worktreeDiff = @(git -C $repoRoot diff --name-only)
$patterns = @(
    "PRIVATE KEY",
    "BEGIN OPENSSH PRIVATE KEY",
    "BEGIN PRIVATE KEY",
    "mnemonic",
    "password=",
    "DATABASE_URL=",
    "0x[0-9a-fA-F]{64}"
)
$secretCandidates = [System.Collections.Generic.List[object]]::new()
foreach ($relative in $tracked) {
    $path = Join-Path $repoRoot $relative
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { continue }
    $bytes = [System.IO.File]::ReadAllBytes($path)
    if ($bytes -contains 0) { continue }
    $text = [System.Text.Encoding]::UTF8.GetString($bytes)
    foreach ($pattern in $patterns) {
        if ([regex]::IsMatch($text, $pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)) {
            $secretCandidates.Add([ordered]@{ path = $relative; pattern = $pattern })
        }
    }
}

$secretSummaryPath = Join-Path $infraRoot "evidence\security-remediation\final-worktree-secret-scan.json"
if (-not (Test-Path -LiteralPath $secretSummaryPath)) {
    throw "Final classified secret scan evidence is missing."
}
$secretSummary = Get-Content -Raw -LiteralPath $secretSummaryPath | ConvertFrom-Json

$validators = Get-Content -Raw -LiteralPath (Join-Path $infraRoot "validator-public\validators.json") |
    ConvertFrom-Json
$expectedGenesis = (Get-Content -Raw -LiteralPath (Join-Path $infraRoot "genesis\genesis.sha256")).Trim().Split(" ")[0].ToLowerInvariant()
$actualGenesis = (Get-FileHash -LiteralPath (Join-Path $infraRoot "genesis\genesis.json") -Algorithm SHA256).Hash.ToLowerInvariant()
$nodeRows = @()
foreach ($hostInfo in @(
    @{ host = "besu-validator-1"; service = "besu.service" },
    @{ host = "besu-validator-2"; service = "besu.service" },
    @{ host = "besu-validator-3"; service = "besu.service" },
    @{ host = "besu-validator-4"; service = "besu.service" },
    @{ host = "experiment-client"; service = "besu-rpc.service" }
)) {
    $response = & ssh.exe -o BatchMode=yes $hostInfo.host "sudo -n systemctl is-active $($hostInfo.service); /opt/besu/bin/besu --version | head -n 1"
    if ($LASTEXITCODE -ne 0) { throw "SSH audit failed for $($hostInfo.host)" }
    $nodeRows += [ordered]@{
        host = $hostInfo.host
        service = $hostInfo.service
        active = ($response[0] -eq "active")
        besu_version = $response[1]
    }
}
$chain = Invoke-Rpc -Method "eth_chainId"
$height = Invoke-Rpc -Method "eth_blockNumber"
$peers = Invoke-Rpc -Method "net_peerCount"
$validatorSet = Invoke-Rpc -Method "qbft_getValidatorsByBlockNumber" -Params @("latest")
Start-Sleep -Seconds 6
$heightAfter = Invoke-Rpc -Method "eth_blockNumber"
$expectedAddresses = @($validators | ForEach-Object { $_.address.ToLowerInvariant() } | Sort-Object)
$observedAddresses = @($validatorSet.result | ForEach-Object { $_.ToLowerInvariant() } | Sort-Object)

$result = [ordered]@{
    stage = "A"
    checked_at_utc = [DateTime]::UtcNow.ToString("o")
    git_head = (git -C $repoRoot rev-parse HEAD).Trim()
    git_status = $gitStatus
    cached_diff = $cachedDiff
    worktree_diff = $worktreeDiff
    tracked_file_count = $tracked.Count
    secret_candidate_count = $secretCandidates.Count
    secret_candidates = @($secretCandidates)
    classified_secret_summary = $secretSummary
    private_tracked = @(git -C $repoRoot ls-files -- "infra/**/private/**" "infra/**/secrets/**" "deployment/**/private/**" "deployment/**/secrets/**")
    genesis_expected_sha256 = $expectedGenesis
    genesis_actual_sha256 = $actualGenesis
    nodes = $nodeRows
    chain_id_hex = $chain.result
    block_number_hex = $height.result
    block_number_after_hex = $heightAfter.result
    peer_count_hex = $peers.result
    validator_addresses = $observedAddresses
    validator_count = $observedAddresses.Count
    validators_match_manifest = (@(Compare-Object $expectedAddresses $observedAddresses).Count -eq 0)
}
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $evidenceDir "audit.json") -Encoding UTF8
if ($secretSummary.committable_true_secret_count -ne 0 -or
    $secretSummary.tracked_true_secret_count -ne 0 -or
    $secretSummary.reachable_history_true_secret_count -ne 0 -or
    $secretSummary.active_object_true_secret_count -ne 0 -or
    $secretSummary.unclassified_count -ne 0 -or
    $result.private_tracked.Count -ne 0) {
    throw "Classified secret scan admission failed; see audit.json"
}
if ($result.genesis_expected_sha256 -ne $result.genesis_actual_sha256) { throw "Genesis hash mismatch" }
if ($result.chain_id_hex -ne "0x78c36ae1" -or $result.validator_count -ne 4 -or -not $result.validators_match_manifest) { throw "Frozen chain identity mismatch" }
if ([Convert]::ToInt32($result.peer_count_hex.Substring(2), 16) -ne 4) { throw "Unexpected peer count" }
if ([Convert]::ToInt64($result.block_number_after_hex.Substring(2), 16) -le
    [Convert]::ToInt64($result.block_number_hex.Substring(2), 16)) { throw "Block height did not increase" }
if (@($nodeRows | Where-Object { -not $_.active -or $_.besu_version -notmatch 'v26\.5\.0' }).Count -ne 0) { throw "Besu service audit failed" }
$result
