param(
    [Parameter(Mandatory)][string]$EvidenceDirectory,
    [int]$WaitSeconds = 30,
    [switch]$Execute
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if (-not $Execute) { throw 'Safety stop: rerun with -Execute to recover the planned RPC service.' }
if (-not (Test-Path -LiteralPath $EvidenceDirectory)) { throw 'EvidenceDirectory does not exist.' }
& ssh.exe -o BatchMode=yes experiment-client 'sudo -n systemctl start besu-rpc.service'
if ($LASTEXITCODE -ne 0) { throw 'Failed to start RPC service' }
Start-Sleep -Seconds $WaitSeconds
$response = Invoke-RestMethod -Uri 'http://192.168.6.133:8545' -Method Post -ContentType 'application/json' -Body '{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}' -TimeoutSec 10
$response | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $EvidenceDirectory 'rpc-recovered.json') -Encoding UTF8
[ordered]@{ test='F2'; rpc_recovered=$true; recovered_at_utc=[DateTime]::UtcNow.ToString('o') } |
    ConvertTo-Json | Set-Content (Join-Path $EvidenceDirectory 'recovery-state.json') -Encoding UTF8
