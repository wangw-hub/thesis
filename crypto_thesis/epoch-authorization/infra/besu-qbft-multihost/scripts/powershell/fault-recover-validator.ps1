param(
    [ValidateSet('besu-validator-1','besu-validator-2','besu-validator-3','besu-validator-4')]
    [string]$Target = 'besu-validator-4',
    [Parameter(Mandatory)][string]$EvidenceDirectory,
    [int]$WaitSeconds = 30,
    [switch]$Execute
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if (-not $Execute) { throw 'Safety stop: rerun with -Execute to recover the planned Validator.' }
if (-not (Test-Path -LiteralPath $EvidenceDirectory)) { throw 'EvidenceDirectory does not exist.' }
& ssh.exe -o BatchMode=yes $Target 'sudo -n systemctl start besu.service'
if ($LASTEXITCODE -ne 0) { throw "Failed to start $Target" }
Start-Sleep -Seconds $WaitSeconds
$after = Invoke-RestMethod -Uri 'http://192.168.6.133:8545' -Method Post -ContentType 'application/json' -Body '{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}'
$after | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $EvidenceDirectory 'block-after.json') -Encoding UTF8
$state = & ssh.exe -o BatchMode=yes $Target 'sudo -n systemctl is-active besu.service'
if ($LASTEXITCODE -ne 0 -or $state.Trim() -ne 'active') { throw "$Target did not recover" }
[ordered]@{ test='F1'; target=$Target; recovered=$true; recovered_at_utc=[DateTime]::UtcNow.ToString('o') } |
    ConvertTo-Json | Set-Content (Join-Path $EvidenceDirectory 'recovery-state.json') -Encoding UTF8
