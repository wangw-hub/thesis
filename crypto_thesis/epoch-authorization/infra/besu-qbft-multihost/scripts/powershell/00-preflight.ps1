$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$topologyPath = Join-Path $root "inventory\frozen-topology.json"
$remoteScript = Join-Path $root "scripts\remote\collect-preflight.sh"
$evidence = Join-Path $root "evidence\preflight"
$logs = Join-Path $root "logs"
New-Item -ItemType Directory -Force -Path $evidence, $logs | Out-Null

$topology = Get-Content -Raw -LiteralPath $topologyPath -Encoding UTF8 | ConvertFrom-Json
$scriptText = Get-Content -Raw -LiteralPath $remoteScript -Encoding UTF8
$scriptText = $scriptText -replace "`r", ""
$results = @()
$failures = [System.Collections.Generic.List[string]]::new()

function Invoke-RemoteBash {
    param(
        [Parameter(Mandatory=$true)][string]$Alias,
        [Parameter(Mandatory=$true)][string]$Mode,
        [Parameter(Mandatory=$true)][string]$Payload
    )

    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = "ssh.exe"
    $startInfo.Arguments = "-o BatchMode=yes -o ConnectTimeout=10 $Alias `"bash -s -- $Mode`""
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardInput = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $process = [System.Diagnostics.Process]::Start($startInfo)
    $process.StandardInput.Write($Payload)
    $process.StandardInput.Close()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    return [pscustomobject]@{
        ExitCode = $process.ExitCode
        StdOut = $stdout
        StdErr = $stderr
    }
}

foreach ($hostEntry in $topology.hosts) {
    $alias = $hostEntry.ssh_alias
    $started = [DateTime]::UtcNow.ToString("o")
    $jsonInvocation = Invoke-RemoteBash -Alias $alias -Mode "--json" -Payload $scriptText
    $jsonExit = $jsonInvocation.ExitCode
    $jsonText = $jsonInvocation.StdOut.Trim()
    Set-Content -LiteralPath (Join-Path $evidence "$alias.json") -Value $jsonText -Encoding UTF8
    if ($jsonExit -ne 0) {
        $failures.Add("$alias JSON collection failed with exit code ${jsonExit}: $($jsonInvocation.StdErr.Trim())")
        break
    }
    try {
        $report = $jsonText | ConvertFrom-Json
    } catch {
        $failures.Add("$alias returned invalid JSON: $($_.Exception.Message)")
        break
    }

    $textInvocation = Invoke-RemoteBash -Alias $alias -Mode "--text" -Payload $scriptText
    $textExit = $textInvocation.ExitCode
    Set-Content -LiteralPath (Join-Path $evidence "$alias.txt") -Value ($textInvocation.StdOut + $textInvocation.StdErr) -Encoding UTF8
    if ($textExit -ne 0) {
        $failures.Add("$alias text collection failed with exit code ${textExit}: $($textInvocation.StdErr.Trim())")
        break
    }

    $expectedIpPattern = [regex]::Escape($hostEntry.ip)
    if ($report.hostname -ne $hostEntry.hostname) { $failures.Add("$alias hostname mismatch: $($report.hostname)") }
    if ($report.whoami -ne "thesis") { $failures.Add("$alias user mismatch: $($report.whoami)") }
    if ($report.os_release.ID -ne "ubuntu" -or $report.os_release.VERSION_ID -ne "24.04") {
        $failures.Add("$alias is not Ubuntu 24.04")
    }
    if ($report.java_major -ne 21) { $failures.Add("$alias Java major is $($report.java_major)") }
    if (-not $report.sudo_noninteractive) { $failures.Add("$alias sudo -n failed") }
    if (-not (($report.ipv4 -join "`n") -match $expectedIpPattern)) { $failures.Add("$alias missing frozen IP $($hostEntry.ip)") }
    foreach ($target in $topology.hosts.ip) {
        if (-not $report.peer_reachability.$target) { $failures.Add("$alias cannot reach $target") }
    }
    foreach ($port in $topology.required_ports) {
        if ($report.ports_in_use."$port") { $failures.Add("$alias port $port is already in use") }
    }
    if ($report.besu_processes.Count -gt 0) { $failures.Add("$alias has an existing Besu process") }
    if ($report.besu_units.Count -gt 0) { $failures.Add("$alias has an existing Besu unit") }
    foreach ($path in "/etc/besu", "/var/lib/besu") {
        if ($report.besu_paths.$path.exists) { $failures.Add("$alias has existing asset $path") }
    }
    $optBesu = $report.besu_paths.'/opt/besu'
    if ($optBesu.is_symlink -or $optBesu.entries.Count -gt 0) {
        $failures.Add("$alias has a non-empty or linked existing /opt/besu asset")
    }
    foreach ($command in "python3", "unzip", "sha256sum") {
        if (-not $report.commands.$command) { $failures.Add("$alias is missing command $command") }
    }
    $results += [pscustomobject]@{
        host = $alias
        started_at_utc = $started
        exit_code = $jsonExit
        machine_id = $report.machine_id
        json_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $evidence "$alias.json")).Hash.ToLower()
        text_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $evidence "$alias.txt")).Hash.ToLower()
    }
    if ($failures.Count -gt 0) { break }
}

if ($results.Count -eq $topology.hosts.Count) {
    $uniqueMachineIds = @($results.machine_id | Sort-Object -Unique)
    if ($uniqueMachineIds.Count -ne $topology.hosts.Count) {
        $failures.Add("machine-id values are not unique")
    }
}

$summary = [ordered]@{
    stage = 0
    collected_at_utc = [DateTime]::UtcNow.ToString("o")
    git_commit = (& git -C (Resolve-Path (Join-Path $root "..\..")).Path rev-parse HEAD).Trim()
    git_dirty = [bool](& git -C (Resolve-Path (Join-Path $root "..\..")).Path status --porcelain)
    hosts_completed = $results.Count
    hosts_expected = $topology.hosts.Count
    failures = @($failures)
    passed = $failures.Count -eq 0 -and $results.Count -eq $topology.hosts.Count
    evidence = $results
}
$summaryPath = Join-Path $evidence "summary.json"
$summary | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $summaryPath -Encoding UTF8
if (-not $summary.passed) {
    throw "Stage 0 preflight failed. See $summaryPath"
}
$summary
