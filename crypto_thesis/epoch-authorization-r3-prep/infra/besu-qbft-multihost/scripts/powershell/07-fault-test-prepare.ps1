$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$infraRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$required = @(
    'scripts\powershell\fault-stop-one-validator.ps1',
    'scripts\powershell\fault-recover-validator.ps1',
    'scripts\powershell\fault-stop-rpc.ps1',
    'scripts\powershell\fault-recover-rpc.ps1',
    'scripts\remote\collect-node-state.sh'
)
$rows = foreach ($relative in $required) {
    $path = Join-Path $infraRoot $relative
    if (-not (Test-Path -LiteralPath $path)) { throw "Missing fault-test artifact: $relative" }
    if ($path.EndsWith('.ps1')) {
        $tokens = $null
        $errors = $null
        [void][System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$tokens, [ref]$errors)
        if (@($errors).Count -ne 0) { throw "PowerShell syntax error in ${relative}: $($errors[0].Message)" }
    }
    [ordered]@{
        path = $relative
        sha256 = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}
$summary = [ordered]@{
    stage = 7
    passed = $true
    destructive_tests_executed = $false
    scripts_require_explicit_execute_switch = $true
    artifacts = @($rows)
    completed_at_utc = [DateTime]::UtcNow.ToString('o')
}
$evidenceDir = Join-Path $infraRoot 'evidence\faults'
New-Item -ItemType Directory -Force -Path $evidenceDir | Out-Null
$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $evidenceDir 'preparation-summary.json') -Encoding UTF8
$summary
