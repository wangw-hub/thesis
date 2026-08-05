$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$infraRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$relativePaths = @(
    'downloads\besu-26.5.0.zip',
    'downloads\besu-26.5.0.zip.sha256',
    'scripts\powershell\01-install-besu.ps1',
    'scripts\powershell\New-Stage1ArtifactManifest.ps1',
    'scripts\remote\install-besu-26.5.0.sh',
    'evidence\installation\download-metadata.json',
    'evidence\installation\hash-verification.json',
    'evidence\installation\besu-validator-1.txt',
    'evidence\installation\besu-validator-2.txt',
    'evidence\installation\besu-validator-3.txt',
    'evidence\installation\besu-validator-4.txt',
    'evidence\installation\experiment-client.txt',
    'reports\stage-1-besu-installation.md'
)

$artifacts = foreach ($relativePath in $relativePaths) {
    $absolutePath = Join-Path $infraRoot $relativePath
    if (-not (Test-Path -LiteralPath $absolutePath -PathType Leaf)) {
        throw "Stage 1 artifact is missing: $absolutePath"
    }
    $file = Get-Item -LiteralPath $absolutePath
    [ordered]@{
        path = $relativePath.Replace('\', '/')
        size_bytes = $file.Length
        sha256 = (Get-FileHash -LiteralPath $absolutePath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}

$manifest = [ordered]@{
    stage = 1
    generated_at_utc = [DateTime]::UtcNow.ToString('o')
    self_excluded = 'evidence/installation/artifact-sha256.json'
    artifacts = @($artifacts)
}
$manifestPath = Join-Path $infraRoot 'evidence\installation\artifact-sha256.json'
$manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
Get-Content -Raw -LiteralPath $manifestPath -Encoding UTF8 | ConvertFrom-Json | Out-Null
$manifest
