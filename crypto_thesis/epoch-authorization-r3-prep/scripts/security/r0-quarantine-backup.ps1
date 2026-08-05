$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$quarantineRoot = "D:\Research\crypto_thesis\security-quarantine"
$snapshotName = "epoch-authorization_" + [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssZ")
$snapshotRoot = Join-Path $quarantineRoot $snapshotName
$worktreeBackup = Join-Path $snapshotRoot "worktree"
$gitBackup = Join-Path $snapshotRoot "git-metadata"
New-Item -ItemType Directory -Force -Path $worktreeBackup, $gitBackup | Out-Null

function Invoke-RobocopyBackup {
    param([Parameter(Mandatory)][string]$Source, [Parameter(Mandatory)][string]$Destination, [string[]]$Extra = @())
    & robocopy.exe $Source $Destination /E /COPY:DAT /DCOPY:DAT /R:1 /W:1 /XJ @Extra | Out-Null
    if ($LASTEXITCODE -gt 7) { throw "robocopy failed from $Source to $Destination with exit code $LASTEXITCODE" }
}

Invoke-RobocopyBackup -Source $repoRoot -Destination $worktreeBackup -Extra @("/XD", ".git")
Invoke-RobocopyBackup -Source (Join-Path $repoRoot ".git") -Destination $gitBackup

$reports = @(
    "infra\besu-qbft-multihost\reports\stage-a-infrastructure-freeze.md",
    "infra\besu-qbft-multihost\evidence\infrastructure-freeze\audit.json",
    "infra\besu-qbft-multihost\evidence\infrastructure-freeze\hard-stop-secret-tracked.json"
)
$manifest = [ordered]@{
    created_at_utc = [DateTime]::UtcNow.ToString("o")
    source_repository = $repoRoot
    backup_path = $snapshotRoot
    git_head = (git -C $repoRoot rev-parse HEAD).Trim()
    git_status = @(git -C $repoRoot status --short)
    remote = @(git -C $repoRoot remote -v)
    branches = @(git -C $repoRoot branch --all)
    tags = @(git -C $repoRoot tag --list)
    stash = @(git -C $repoRoot stash list)
    retained_audit_evidence = $reports
}
$files = Get-ChildItem -LiteralPath $snapshotRoot -Recurse -File | ForEach-Object {
    [ordered]@{
        path = $_.FullName.Substring($snapshotRoot.Length + 1)
        bytes = $_.Length
        sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}
$manifest["file_count"] = @($files).Count
$manifest["files"] = @($files)
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $snapshotRoot "backup-manifest.json") -Encoding UTF8
& icacls.exe $snapshotRoot /inheritance:r /grant:r "$env:USERNAME:(OI)(CI)F" | Out-Null
if ($LASTEXITCODE -ne 0) { throw "failed to restrict quarantine directory ACL" }
[ordered]@{ snapshot = $snapshotRoot; manifest = (Join-Path $snapshotRoot "backup-manifest.json"); file_count = @($files).Count } | ConvertTo-Json
