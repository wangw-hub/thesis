param([switch]$Execute)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if (-not $Execute) { throw 'Safety stop: rerun with -Execute to perform the planned RPC stop.' }
$infraRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$runId = 'f2_' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
$evidence = Join-Path $infraRoot "evidence\faults\$runId"
New-Item -ItemType Directory -Force -Path $evidence | Out-Null
& ssh.exe -o BatchMode=yes experiment-client 'sudo -n systemctl stop besu-rpc.service'
if ($LASTEXITCODE -ne 0) { throw 'Failed to stop RPC service' }
$unavailable = $false
try {
    Invoke-RestMethod -Uri 'http://192.168.6.133:8545' -Method Post -ContentType 'application/json' -Body '{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}' -TimeoutSec 5 | Out-Null
} catch {
    $unavailable = $true
}
if (-not $unavailable) { throw 'RPC remained reachable after service stop' }
[ordered]@{ test='F2'; rpc_unavailable=$true; stopped_at_utc=[DateTime]::UtcNow.ToString('o') } |
    ConvertTo-Json | Set-Content (Join-Path $evidence 'stop-state.json') -Encoding UTF8
Write-Output $evidence
