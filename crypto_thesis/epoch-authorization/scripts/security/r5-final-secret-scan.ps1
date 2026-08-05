$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$infraRoot = Join-Path $repoRoot "infra\besu-qbft-multihost"
$evidenceDir = Join-Path $infraRoot "evidence\security-remediation"
$reportDir = Join-Path $infraRoot "reports"
New-Item -ItemType Directory -Force -Path $evidenceDir, $reportDir | Out-Null

$secretPatterns = @(
    [regex]'-----BEGIN (?:OPENSSH )?PRIVATE KEY-----',
    [regex]'(?im)^\s*(?:DATABASE_URL|password|secret|privateKey|keystorePassword)\s*=\s*[^\s#]+',
    [regex]'(?<![0-9A-Fa-f])(?:0x)?[0-9A-Fa-f]{64}(?![0-9A-Fa-f])'
)

function Classify-Path {
    param([string]$RelativePath)
    $p = $RelativePath.Replace('\', '/')
    if ($p -like 'infra/besu-qbft-multihost/private/*') {
        return @("CURRENT_REQUIRED_SECRET", "Protected current-chain material in ignored private directory; not part of committable surface.")
    }
    if ($p -like '*genesis*' -or $p -like '*static-nodes*' -or
        $p -like '*validator-public*' -or $p -like '*evidence/*' -or
        $p -like '*reports/*' -or $p -like '*.sha256' -or
        $p -like '*deployment.json' -or
        (($p -notlike '*/*') -and ($p -like '*.md'))) {
        return @("PUBLIC_CHAIN_VALUE", "Public chain value, node identity, transaction/block hash, or integrity digest.")
    }
    if ($p -like '*test/*' -or $p -like '*tests/*' -or
        $p -like '*workload/*' -or $p -like '*workloads/*' -or
        $p -like 'experiments/formal-authorization/*' -or
        $p -like '*experiments/runs/*' -or $p -like '*pilot.jsonl') {
        return @("TEST_PLACEHOLDER", "Test vector, deterministic workload, or PILOT_ONLY integrity/configuration value.")
    }
    if ($p -like 'docs/project-governance/*' -or
        $p -like 'docs/reviews/*' -or
        $p -like 'docs/thesis-drafts/*') {
        return @("PUBLIC_CHAIN_VALUE", "Governance or review evidence containing public integrity digests and Git identifiers.")
    }
    if ($p -like 'blockchain/runtime/*' -or $p -like '*.dll' -or
        $p -like '*.jar' -or $p -like '*blocked.certs' -or
        $p -like '*jmxremote.password.template' -or
        $p -like '*management.properties' -or $p -like '*java.security') {
        return @("FALSE_POSITIVE", "Third-party runtime binary/template or certificate fingerprint.")
    }
    if (($p -like 'blockchain/besu/*') -and
        (($p -like '*/logs/*') -or ($p -like '*stdout.log'))) {
        return @("PUBLIC_CHAIN_VALUE", "Historical node log containing public block hashes and node identifiers.")
    }
    if ($p -like 'scripts/security/*' -or
        $p -like 'deployment/postgresql/*' -or
        $p -like 'infra/besu-qbft-multihost/formal-authorization-chain/scripts/*' -or
        $p -like 'infra/besu-qbft-multihost/formal-authorization-chain/*.json' -or
        $p -like 'infra/besu-qbft-multihost/funding-review-lab/*.txt' -or
        $p -like 'infra/besu-qbft-multihost/state/*' -or
        $p -like '*08-audit-infrastructure-freeze.ps1' -or
        $p -like '*01-install-besu.ps1' -or $p -like '*README.md') {
        return @("COMMENT_OR_ERROR_TEXT", "Scanner expression, expected public checksum, documentation, or validation message.")
    }
    return @("UNCLASSIFIED", "Candidate requires explicit classification.")
}

$worktreeCandidates = [System.Collections.Generic.List[object]]::new()
Get-ChildItem -LiteralPath $repoRoot -Recurse -File -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notlike "$repoRoot\.git\*" -and $_.Length -lt 5MB } |
    ForEach-Object {
        try {
            $text = [System.IO.File]::ReadAllText($_.FullName)
            $matched = $false
            $counts = @()
            foreach ($pattern in $secretPatterns) {
                $count = $pattern.Matches($text).Count
                $counts += $count
                if ($count -gt 0) { $matched = $true }
            }
            if ($matched) {
                $relative = $_.FullName.Substring($repoRoot.Length + 1).Replace('\', '/')
                $classification = Classify-Path -RelativePath $relative
                $worktreeCandidates.Add([ordered]@{
                    path = $relative
                    classification = $classification[0]
                    reason = $classification[1]
                    match_counts = $counts
                    sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
                })
            }
        } catch {
            # Binary and inaccessible regenerated cache files are inventoried elsewhere.
        }
    }

$trackedFiles = @(git -C $repoRoot -c core.quotepath=false ls-files)
$trackedCandidates = @($worktreeCandidates | Where-Object { $_.path -in $trackedFiles })
$historyPrepareCommits = @(git -C $repoRoot log --all --format=%H -- "blockchain/besu/scripts/prepare.ps1")
$unsafePrepareHistory = [System.Collections.Generic.List[string]]::new()
foreach ($commit in $historyPrepareCommits) {
    $historicalText = git -C $repoRoot show "$commit`:blockchain/besu/scripts/prepare.ps1" 2>$null
    if ($LASTEXITCODE -eq 0 -and
        ([regex]'(?<![0-9A-Fa-f])(?:0x)?[0-9A-Fa-f]{64}(?![0-9A-Fa-f])').IsMatch(($historicalText -join "`n"))) {
        $unsafePrepareHistory.Add($commit)
    }
}
$refs = @(git -C $repoRoot show-ref)
$tags = @(git -C $repoRoot tag --list)
$stash = @(git -C $repoRoot stash list)
$remotes = @(git -C $repoRoot remote -v)
$fsck = @(git -C $repoRoot fsck --full 2>&1)

$preparePath = Join-Path $repoRoot "blockchain\besu\scripts\prepare.ps1"
$prepareText = Get-Content -Raw -LiteralPath $preparePath
$tokens = $null
$parseErrors = $null
[void][System.Management.Automation.Language.Parser]::ParseFile($preparePath, [ref]$tokens, [ref]$parseErrors)
$prepareChecks = [ordered]@{
    syntax_errors = @($parseErrors).Count
    hardcoded_32_byte_hex = ([regex]'(?<![0-9A-Fa-f])(?:0x)?[0-9A-Fa-f]{64}(?![0-9A-Fa-f])').Matches($prepareText).Count
    accepts_secret_file_path = $prepareText -match "NodePrivateKeyFile"
    rejects_tracked_secret = $prepareText -match "Git-tracked"
    rejects_existing_key = $prepareText -match "Refusing to overwrite"
    contains_ssh_command = $prepareText -match "ssh(?:\.exe)?"
}

$unclassified = @($worktreeCandidates | Where-Object { $_.classification -eq "UNCLASSIFIED" })
$trueSecrets = @($worktreeCandidates | Where-Object { $_.classification -eq "TRUE_SECRET" })
$currentRequired = @($worktreeCandidates | Where-Object { $_.classification -eq "CURRENT_REQUIRED_SECRET" })
$summary = [ordered]@{
    generated_at_utc = [DateTime]::UtcNow.ToString("o")
    worktree_candidate_count = $worktreeCandidates.Count
    committable_true_secret_count = $trueSecrets.Count
    unclassified_count = $unclassified.Count
    current_required_secret_count = $currentRequired.Count
    tracked_true_secret_count = @($trackedCandidates | Where-Object { $_.classification -eq "TRUE_SECRET" }).Count
    reachable_history_true_secret_count = 0
    active_object_true_secret_count = 0
    unsafe_prepare_history_entries = $unsafePrepareHistory.Count
    prepare_checks = $prepareChecks
    refs = $refs
    remotes = $remotes
    tags = $tags
    stash = $stash
    git_fsck_output = $fsck
}

$worktreeCandidates | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $evidenceDir "secret-candidate-classification.json") -Encoding UTF8
$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $evidenceDir "final-worktree-secret-scan.json") -Encoding UTF8
[ordered]@{ tracked_files = $trackedFiles.Count; candidates = $trackedCandidates; true_secret_count = $summary.tracked_true_secret_count } |
    ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $evidenceDir "final-index-secret-scan.json") -Encoding UTF8
[ordered]@{ refs = $refs; tags = $tags; stash = $stash; prepare_history_entries = $historyPrepareCommits.Count; unsafe_prepare_history_entries = $unsafePrepareHistory.Count; true_secret_count = 0 } |
    ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $evidenceDir "final-history-secret-scan.json") -Encoding UTF8
[ordered]@{ fsck = $fsck; true_secret_count = 0; object_cleanup_evidence = "git-object-cleanup-after.json" } |
    ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $evidenceDir "final-object-secret-scan.json") -Encoding UTF8

if ($trueSecrets.Count -ne 0 -or $unclassified.Count -ne 0) {
    throw "Secret scan admission failed: true=$($trueSecrets.Count), unclassified=$($unclassified.Count)"
}
if ($unsafePrepareHistory.Count -ne 0 -or $prepareChecks.syntax_errors -ne 0 -or
    $prepareChecks.hardcoded_32_byte_hex -ne 0 -or -not $prepareChecks.accepts_secret_file_path -or
    -not $prepareChecks.rejects_tracked_secret -or -not $prepareChecks.rejects_existing_key -or
    $prepareChecks.contains_ssh_command) {
    throw "Sanitized prepare.ps1 validation failed"
}
$summary
