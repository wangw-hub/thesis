$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$infraRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$projectRoot = Split-Path -Parent (Split-Path -Parent $infraRoot)
$configPath = Join-Path $infraRoot 'genesis\qbftConfigFile.json'
$parameterPath = Join-Path $infraRoot 'genesis\parameter-freeze.json'
$genesisPath = Join-Path $infraRoot 'genesis\genesis.json'
$genesisShaPath = Join-Path $infraRoot 'genesis\genesis.sha256'
$publicDir = Join-Path $infraRoot 'validator-public'
$privateDir = Join-Path $infraRoot 'private\stage2-generated'
$privateExtractRoot = Join-Path $privateDir 'besu-qbft-stage2-2026072801'
$evidenceDir = Join-Path $infraRoot 'evidence\genesis'
$generateScriptPath = Join-Path $infraRoot 'scripts\remote\generate-qbft-network.sh'
$cleanupScriptPath = Join-Path $infraRoot 'scripts\remote\cleanup-stage2-staging.sh'
$remoteConfig = '/tmp/besu-qbftConfigFile-2026072801.json'
$remoteArchive = '/tmp/besu-qbft-stage2-2026072801.tar.gz'
$localArchive = Join-Path $privateDir 'besu-qbft-stage2-2026072801.tar.gz'

foreach ($target in @($genesisPath, $localArchive)) {
    if (Test-Path -LiteralPath $target) {
        throw "Refusing to overwrite existing stage2 material: $target"
    }
}
if (Test-Path -LiteralPath $privateDir) {
    if (@(Get-ChildItem -Force -LiteralPath $privateDir).Count -gt 0) {
        throw "Refusing to reuse non-empty stage2 private directory: $privateDir"
    }
}

& git.exe check-ignore -q -- 'infra/besu-qbft-multihost/private/probe.key'
if ($LASTEXITCODE -ne 0) {
    throw 'Private directory is not protected by .gitignore'
}

$config = Get-Content -Raw -LiteralPath $configPath -Encoding UTF8 | ConvertFrom-Json
$parameters = Get-Content -Raw -LiteralPath $parameterPath -Encoding UTF8 | ConvertFrom-Json
if ($config.genesis.config.chainId -ne $parameters.chainId -or
    $config.blockchain.nodes.count -ne 4 -or
    $config.genesis.config.qbft.blockperiodseconds -ne $parameters.blockperiodseconds) {
    throw 'QBFT configuration conflicts with parameter freeze'
}

New-Item -ItemType Directory -Force -Path $privateDir, $publicDir, $evidenceDir | Out-Null
& scp.exe -q -- $configPath "experiment-client:${remoteConfig}"
if ($LASTEXITCODE -ne 0) { throw 'Failed to transfer QBFT configuration' }

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
    $process.StandardInput.Write(($Payload -replace "`r", ''))
    $process.StandardInput.Close()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    [pscustomobject]@{ ExitCode = $process.ExitCode; StdOut = $stdout; StdErr = $stderr }
}

$generatePayload = Get-Content -Raw -LiteralPath $generateScriptPath -Encoding UTF8
$generation = Invoke-RemoteBash -Payload $generatePayload
$generationLog = "exit_code=$($generation.ExitCode)`n--- stdout ---`n$($generation.StdOut)`n--- stderr ---`n$($generation.StdErr)"
$generationLogPath = Join-Path $evidenceDir 'generation.txt'
[System.IO.File]::WriteAllText($generationLogPath, $generationLog, [System.Text.UTF8Encoding]::new($false))
if ($generation.ExitCode -ne 0) { throw "Remote network generation failed. See $generationLogPath" }

$archiveMatch = [regex]::Match($generation.StdOut, '(?m)^archive_sha256=([0-9a-f]{64})$')
if (-not $archiveMatch.Success) { throw 'Remote archive hash evidence is missing' }
& scp.exe -q -- "experiment-client:${remoteArchive}" $localArchive
if ($LASTEXITCODE -ne 0) { throw 'Failed to retrieve generated network archive' }
$localArchiveHash = (Get-FileHash -LiteralPath $localArchive -Algorithm SHA256).Hash.ToLowerInvariant()
if ($localArchiveHash -ne $archiveMatch.Groups[1].Value) { throw 'Generated archive hash mismatch after transfer' }

& tar.exe -xzf $localArchive -C $privateDir
if ($LASTEXITCODE -ne 0) { throw 'Failed to extract generated network archive' }
$generatedGenesis = Join-Path $privateExtractRoot 'genesis.json'
if (-not (Test-Path -LiteralPath $generatedGenesis -PathType Leaf)) { throw 'Extracted genesis.json is missing' }
$keyDirectories = @(Get-ChildItem -Path $privateExtractRoot -Recurse -File -Filter 'key.priv' | ForEach-Object { $_.Directory })
if ($keyDirectories.Count -ne 4) { throw "Expected four validator key directories, found $($keyDirectories.Count)" }
$decodedPath = Join-Path $privateExtractRoot 'decoded-validators.txt'
if (-not (Test-Path -LiteralPath $decodedPath -PathType Leaf)) { throw 'Decoded validator evidence is missing' }
$decodedAddresses = @([regex]::Matches(
    (Get-Content -Raw -LiteralPath $decodedPath -Encoding UTF8).ToLowerInvariant(),
    '0x[0-9a-f]{40}'
) | ForEach-Object { $_.Value })
if ($decodedAddresses.Count -ne 4 -or @($decodedAddresses | Select-Object -Unique).Count -ne 4) {
    throw 'Decoded Genesis validator order is invalid'
}
$directoryByAddress = @{}
foreach ($directory in $keyDirectories) {
    $directoryByAddress[$directory.Name.ToLowerInvariant()] = $directory
}
$keyDirectories = @($decodedAddresses | ForEach-Object {
    if (-not $directoryByAddress.ContainsKey($_)) { throw "Genesis validator $_ has no generated key directory" }
    $directoryByAddress[$_]
})

$validators = [System.Collections.Generic.List[object]]::new()
$privateHashes = [System.Collections.Generic.List[string]]::new()
for ($index = 0; $index -lt $keyDirectories.Count; $index++) {
    $directory = $keyDirectories[$index]
    $privateKeyPath = Join-Path $directory.FullName 'key.priv'
    $publicKeyPath = Join-Path $directory.FullName 'key.pub'
    if (-not (Test-Path -LiteralPath $publicKeyPath -PathType Leaf)) { throw "Missing public key in $($directory.FullName)" }
    $address = $directory.Name.ToLowerInvariant() -replace '^0x', ''
    $publicKey = (Get-Content -Raw -LiteralPath $publicKeyPath -Encoding UTF8).Trim().ToLowerInvariant() -replace '^0x', ''
    if ($address -notmatch '^[0-9a-f]{40}$' -or $publicKey -notmatch '^[0-9a-f]{128}$') {
        throw "Invalid generated address or public key format in $($directory.FullName)"
    }
    $privateHash = (Get-FileHash -LiteralPath $privateKeyPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $privateHashes.Add($privateHash)
    $hostAlias = "besu-validator-$($index + 1)"
    $publicCopy = Join-Path $publicDir "$hostAlias.pub"
    [System.IO.File]::WriteAllText($publicCopy, "$publicKey`n", [System.Text.UTF8Encoding]::new($false))
    $validators.Add([pscustomobject][ordered]@{
        index = $index + 1
        host = $hostAlias
        address = "0x$address"
        node_id = $publicKey
        public_key_file = "validator-public/$hostAlias.pub"
        generated_directory = $directory.Name
    })
}
if (@($privateHashes | Select-Object -Unique).Count -ne 4) { throw 'Generated validator private-key hashes are not unique' }
if (@($validators.node_id | Select-Object -Unique).Count -ne 4) { throw 'Generated validator node IDs are not unique' }
if (@($validators.address | Select-Object -Unique).Count -ne 4) { throw 'Generated validator addresses are not unique' }

Copy-Item -LiteralPath $generatedGenesis -Destination $genesisPath
$genesis = Get-Content -Raw -LiteralPath $genesisPath -Encoding UTF8 | ConvertFrom-Json
if ($genesis.config.chainId -ne 2026072801 -or $null -eq $genesis.config.qbft) {
    throw 'Generated genesis does not contain the frozen chainId and QBFT configuration'
}
$genesisHash = (Get-FileHash -LiteralPath $genesisPath -Algorithm SHA256).Hash.ToLowerInvariant()
[System.IO.File]::WriteAllText($genesisShaPath, "$genesisHash  genesis.json`n", [System.Text.UTF8Encoding]::new($false))
$validators | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $publicDir 'validators.json') -Encoding UTF8
[System.IO.File]::WriteAllLines((Join-Path $publicDir 'validator-addresses.txt'), @($validators.address), [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllLines((Join-Path $publicDir 'node-ids.txt'), @($validators.node_id), [System.Text.UTF8Encoding]::new($false))
[pscustomobject]@{ private_key_sha256 = @($privateHashes) } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $privateDir 'private-key-hashes.json') -Encoding UTF8

Copy-Item -LiteralPath $decodedPath -Destination (Join-Path $evidenceDir 'decoded-validators.txt')

$cleanupPayload = Get-Content -Raw -LiteralPath $cleanupScriptPath -Encoding UTF8
$cleanup = Invoke-RemoteBash -Payload $cleanupPayload
$cleanupLogPath = Join-Path $evidenceDir 'remote-cleanup.txt'
[System.IO.File]::WriteAllText($cleanupLogPath, "exit_code=$($cleanup.ExitCode)`n$($cleanup.StdOut)`n$($cleanup.StdErr)", [System.Text.UTF8Encoding]::new($false))
if ($cleanup.ExitCode -ne 0 -or $cleanup.StdOut -notmatch 'stage2_remote_staging=absent') {
    throw "Remote private-material cleanup failed. See $cleanupLogPath"
}

$summary = [ordered]@{
    stage = 2
    passed = $true
    chainId = 2026072801
    genesis_sha256 = $genesisHash
    validator_count = 4
    validator_addresses = @($validators.address)
    node_ids_unique = $true
    private_key_hashes_unique = $true
    remote_private_material_removed = $true
    besu_version = '26.5.0'
    generated_at_utc = [DateTime]::UtcNow.ToString('o')
}
$summary | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $evidenceDir 'summary.json') -Encoding UTF8
$summary
