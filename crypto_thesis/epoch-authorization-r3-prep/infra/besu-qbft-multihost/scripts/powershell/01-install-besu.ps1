$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$infraRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$projectRoot = Split-Path -Parent (Split-Path -Parent $infraRoot)
$sourcePackage = Join-Path $projectRoot 'blockchain\besu-26.5.0.zip'
$downloadsDir = Join-Path $infraRoot 'downloads'
$packagePath = Join-Path $downloadsDir 'besu-26.5.0.zip'
$shaPath = "$packagePath.sha256"
$remoteScriptPath = Join-Path $infraRoot 'scripts\remote\install-besu-26.5.0.sh'
$evidenceDir = Join-Path $infraRoot 'evidence\installation'
$expectedSha256 = '9ddbe9e94662459898ff7b3ff4439821eeeee3bc2ff961378604202fa7da09e6'
$officialUrl = 'https://github.com/besu-eth/besu/releases/download/26.5.0/besu-26.5.0.zip'
$releasePage = 'https://github.com/besu-eth/besu/releases/tag/26.5.0'
$hosts = @('besu-validator-1', 'besu-validator-2', 'besu-validator-3', 'besu-validator-4', 'experiment-client')

New-Item -ItemType Directory -Force -Path $downloadsDir, $evidenceDir | Out-Null
if (-not (Test-Path -LiteralPath $sourcePackage -PathType Leaf)) {
    throw "Validated source package does not exist: $sourcePackage"
}
$sourceHash = (Get-FileHash -LiteralPath $sourcePackage -Algorithm SHA256).Hash.ToLowerInvariant()
if ($sourceHash -ne $expectedSha256) {
    throw "Source package hash mismatch: expected=$expectedSha256 actual=$sourceHash"
}

if (Test-Path -LiteralPath $packagePath) {
    $existingHash = (Get-FileHash -LiteralPath $packagePath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($existingHash -ne $expectedSha256) {
        throw "Refusing to overwrite a different package at $packagePath"
    }
} else {
    Copy-Item -LiteralPath $sourcePackage -Destination $packagePath
}
$packageHash = (Get-FileHash -LiteralPath $packagePath -Algorithm SHA256).Hash.ToLowerInvariant()
[System.IO.File]::WriteAllText($shaPath, "$packageHash  besu-26.5.0.zip`n", [System.Text.UTF8Encoding]::new($false))

$packageInfo = Get-Item -LiteralPath $packagePath
$metadata = [ordered]@{
    version = '26.5.0'
    release_page = $releasePage
    original_download_url = $officialUrl
    file_name = $packageInfo.Name
    file_size_bytes = $packageInfo.Length
    sha256 = $packageHash
    official_release_checksum = $expectedSha256
    checksum_verified = ($packageHash -eq $expectedSha256)
    controller_source = $sourcePackage
    recorded_at_utc = [DateTime]::UtcNow.ToString('o')
}
$metadataPath = Join-Path $evidenceDir 'download-metadata.json'
$metadata | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $metadataPath -Encoding UTF8

$remoteScript = (Get-Content -Raw -LiteralPath $remoteScriptPath -Encoding UTF8) -replace "`r", ''
$results = [System.Collections.Generic.List[object]]::new()

function Invoke-RemoteInstaller {
    param(
        [Parameter(Mandatory)][string]$HostAlias,
        [Parameter(Mandatory)][string]$Payload,
        [Parameter(Mandatory)][string]$ExpectedHash
    )
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = 'ssh.exe'
    $psi.Arguments = "$HostAlias bash -s -- $ExpectedHash"
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

foreach ($hostAlias in $hosts) {
    $startedAt = [DateTime]::UtcNow.ToString('o')
    & scp.exe -q -- $packagePath "${hostAlias}:/tmp/besu-26.5.0.zip"
    if ($LASTEXITCODE -ne 0) {
        throw "Package transfer failed for $hostAlias with exit code $LASTEXITCODE"
    }
    $execution = Invoke-RemoteInstaller -HostAlias $hostAlias -Payload $remoteScript -ExpectedHash $expectedSha256
    $record = "host=$hostAlias`nstarted_at_utc=$startedAt`nexit_code=$($execution.ExitCode)`n--- stdout ---`n$($execution.StdOut)`n--- stderr ---`n$($execution.StdErr)"
    $recordPath = Join-Path $evidenceDir "$hostAlias.txt"
    [System.IO.File]::WriteAllText($recordPath, $record, [System.Text.UTF8Encoding]::new($false))
    $remoteHashMatch = [regex]::Match($execution.StdOut, '(?m)^package_sha256=([0-9a-f]{64})$')
    $result = [ordered]@{
        host = $hostAlias
        exit_code = $execution.ExitCode
        remote_package_sha256 = if ($remoteHashMatch.Success) { $remoteHashMatch.Groups[1].Value } else { $null }
        evidence = $recordPath
        evidence_sha256 = (Get-FileHash -LiteralPath $recordPath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    $results.Add([pscustomobject]$result)
    $results | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $evidenceDir 'hash-verification.json') -Encoding UTF8
    if ($execution.ExitCode -ne 0) {
        throw "Besu installation failed on $hostAlias. See $recordPath"
    }
    if ($result.remote_package_sha256 -ne $expectedSha256) {
        throw "Remote package hash evidence missing or mismatched on $hostAlias"
    }
}

$results
