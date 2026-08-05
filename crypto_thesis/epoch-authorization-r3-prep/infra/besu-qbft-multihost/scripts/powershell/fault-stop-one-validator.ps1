param(
    [ValidateSet('besu-validator-1','besu-validator-2','besu-validator-3','besu-validator-4')]
    [string]$Target = 'besu-validator-4',
    [switch]$Execute
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if (-not $Execute) { throw 'Safety stop: rerun with -Execute to perform the planned Validator stop.' }
$infraRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$runId = 'f1_' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
$evidence = Join-Path $infraRoot "evidence\faults\$runId"
New-Item -ItemType Directory -Force -Path $evidence | Out-Null
$before = Invoke-RestMethod -Uri 'http://192.168.6.133:8545' -Method Post -ContentType 'application/json' -Body '{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}'
$before | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $evidence 'block-before.json') -Encoding UTF8
& ssh.exe -o BatchMode=yes $Target 'sudo -n systemctl stop besu.service'
if ($LASTEXITCODE -ne 0) { throw "Failed to stop $Target" }
[ordered]@{ test='F1'; target=$Target; stopped=$true; evidence=$evidence; stopped_at_utc=[DateTime]::UtcNow.ToString('o') } |
    ConvertTo-Json | Set-Content (Join-Path $evidence 'stop-state.json') -Encoding UTF8
Write-Output $evidence
