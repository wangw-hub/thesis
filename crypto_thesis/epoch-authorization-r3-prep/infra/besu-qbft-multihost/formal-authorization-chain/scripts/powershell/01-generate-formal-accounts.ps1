param([Parameter(Mandatory = $true)][string]$SecretRoot)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$chainRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if ((Resolve-Path $SecretRoot).Path -like "$chainRoot*") { throw 'Secret root must be outside the repository.' }
$roles = @('bootstrap-funder','admin','owner','authorizer','revocation','auditor','rpc-node')
$python = @'
from eth_account import Account
from pathlib import Path
import json, sys
root=Path(sys.argv[1]); roles=sys.argv[2:]
out=[]
for role in roles:
    directory=root/role; directory.mkdir(parents=True, exist_ok=True)
    key_file=directory/'key.hex'
    account=Account.from_key(key_file.read_text().strip()) if key_file.exists() else Account.create()
    if not key_file.exists(): key_file.write_text(account.key.hex()+'\n', encoding='ascii')
    out.append({'role':role.upper().replace('-','_'),'address':account.address})
print(json.dumps(out))
'@
$json = & python -c $python $SecretRoot @($roles)
if ($LASTEXITCODE -ne 0) { throw 'Account generation failed.' }
$accounts = $json | ConvertFrom-Json
if (@($accounts | ForEach-Object { $_.address } | Select-Object -Unique).Count -ne $roles.Count) { throw 'Generated addresses are not unique.' }
$publicDir = Join-Path $chainRoot 'accounts'
New-Item -ItemType Directory -Force -Path $publicDir | Out-Null
$accounts | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $publicDir 'public-role-addresses.json')
[ordered]@{ chain_id = 2026072901; roles = $accounts; bootstrap_has_business_role = $false } | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 (Join-Path $publicDir 'account-governance-manifest.json')
