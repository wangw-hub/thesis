$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$infraRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$privateRoot = Join-Path $infraRoot 'private\stage2-generated\besu-qbft-stage2-2026072801'
$publicDir = Join-Path $infraRoot 'validator-public'
$decodedPath = Join-Path $privateRoot 'decoded-validators.txt'
$summaryPath = Join-Path $infraRoot 'evidence\genesis\summary.json'

$decodedAddresses = @([regex]::Matches(
    (Get-Content -Raw -LiteralPath $decodedPath -Encoding UTF8).ToLowerInvariant(),
    '0x[0-9a-f]{40}'
) | ForEach-Object { $_.Value })
if ($decodedAddresses.Count -ne 4 -or @($decodedAddresses | Select-Object -Unique).Count -ne 4) {
    throw 'Decoded Genesis validator order is invalid'
}

$keyDirectories = @(Get-ChildItem -Path $privateRoot -Recurse -File -Filter 'key.priv' | ForEach-Object { $_.Directory })
$directoryByAddress = @{}
foreach ($directory in $keyDirectories) {
    $directoryByAddress[$directory.Name.ToLowerInvariant()] = $directory
}

$validators = [System.Collections.Generic.List[object]]::new()
for ($index = 0; $index -lt $decodedAddresses.Count; $index++) {
    $address = $decodedAddresses[$index]
    if (-not $directoryByAddress.ContainsKey($address)) { throw "Missing key material for $address" }
    $directory = $directoryByAddress[$address]
    $publicKey = (Get-Content -Raw -LiteralPath (Join-Path $directory.FullName 'key.pub') -Encoding UTF8).Trim().ToLowerInvariant() -replace '^0x', ''
    if ($publicKey -notmatch '^[0-9a-f]{128}$') { throw "Invalid public key for $address" }
    $hostAlias = "besu-validator-$($index + 1)"
    [System.IO.File]::WriteAllText((Join-Path $publicDir "$hostAlias.pub"), "$publicKey`n", [System.Text.UTF8Encoding]::new($false))
    $validators.Add([pscustomobject][ordered]@{
        index = $index + 1
        host = $hostAlias
        address = $address
        node_id = $publicKey
        public_key_file = "validator-public/$hostAlias.pub"
        generated_directory = $directory.Name
    })
}

$validators | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $publicDir 'validators.json') -Encoding UTF8
[System.IO.File]::WriteAllLines((Join-Path $publicDir 'validator-addresses.txt'), @($validators.address), [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllLines((Join-Path $publicDir 'node-ids.txt'), @($validators.node_id), [System.Text.UTF8Encoding]::new($false))

$summary = Get-Content -Raw -LiteralPath $summaryPath -Encoding UTF8 | ConvertFrom-Json
$summary.validator_addresses = @($validators.address)
$summary | Add-Member -NotePropertyName validator_order_source -NotePropertyValue 'QBFT extraData decode order' -Force
$summary | Add-Member -NotePropertyName mapping_reconciled_at_utc -NotePropertyValue ([DateTime]::UtcNow.ToString('o')) -Force
$summary | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $summaryPath -Encoding UTF8
$validators
