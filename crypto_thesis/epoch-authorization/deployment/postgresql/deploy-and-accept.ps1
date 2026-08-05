param(
    [string]$HostAlias = "experiment-client"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$root = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent $root
$evidence = Join-Path $repoRoot "evidence\postgresql"
New-Item -ItemType Directory -Force -Path $evidence | Out-Null

function Send-File {
    param([string]$LocalPath, [string]$RemotePath)
    $content = [IO.File]::ReadAllText($LocalPath).Replace("`r", "")
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = "ssh.exe"
    $start.Arguments = "-o BatchMode=yes $HostAlias `"umask 077; cat > '$RemotePath'`""
    $start.RedirectStandardInput = $true
    $start.RedirectStandardError = $true
    $start.UseShellExecute = $false
    $process = [Diagnostics.Process]::Start($start)
    $process.StandardInput.Write($content)
    $process.StandardInput.Close()
    $process.WaitForExit()
    if ($process.ExitCode -ne 0) {
        throw "Transfer failed: $LocalPath; $($process.StandardError.ReadToEnd())"
    }
}

Send-File (Join-Path $PSScriptRoot "install-postgresql.sh") "/tmp/install-postgresql.sh"
Send-File (Join-Path $PSScriptRoot "schema.sql") "/tmp/epoch-auth-schema.sql"
Send-File (Join-Path $PSScriptRoot "run-stage-b-tests.py") "/tmp/run-stage-b-tests.py"

$install = & ssh.exe -o BatchMode=yes $HostAlias "chmod 700 /tmp/install-postgresql.sh; /tmp/install-postgresql.sh"
if ($LASTEXITCODE -ne 0) { throw "PostgreSQL installation failed" }
$install | Set-Content -LiteralPath (Join-Path $evidence "installation.txt") -Encoding UTF8

& ssh.exe -o BatchMode=yes $HostAlias "chmod 644 /tmp/epoch-auth-schema.sql; sudo -n -u postgres psql -v ON_ERROR_STOP=1 -d epoch_auth -f /tmp/epoch-auth-schema.sql >/dev/null"
if ($LASTEXITCODE -ne 0) { throw "Schema installation failed" }

$concurrency = & ssh.exe -o BatchMode=yes $HostAlias "sudo -n python3 /tmp/run-stage-b-tests.py"
if ($LASTEXITCODE -ne 0) { throw "Concurrency acceptance failed" }
$concurrency | Set-Content -LiteralPath (Join-Path $evidence "concurrency.json") -Encoding UTF8

& ssh.exe -o BatchMode=yes $HostAlias "sudo -n systemctl stop postgresql"
if ($LASTEXITCODE -ne 0) { throw "PostgreSQL stop test failed" }
$failureProbe = & ssh.exe -o BatchMode=yes $HostAlias "sudo -n python3 /tmp/run-stage-b-tests.py >/dev/null 2>&1; test `$? -ne 0"
if ($LASTEXITCODE -ne 0) {
    & ssh.exe -o BatchMode=yes $HostAlias "sudo -n systemctl start postgresql" | Out-Null
    throw "Database outage did not fail closed"
}
& ssh.exe -o BatchMode=yes $HostAlias "sudo -n systemctl start postgresql"
if ($LASTEXITCODE -ne 0) { throw "PostgreSQL recovery failed" }
for ($attempt = 0; $attempt -lt 24; $attempt++) {
    & ssh.exe -o BatchMode=yes $HostAlias "sudo -n -u postgres pg_isready -q"
    if ($LASTEXITCODE -eq 0) { break }
    Start-Sleep -Seconds 5
}
if ($LASTEXITCODE -ne 0) { throw "PostgreSQL did not become ready" }

$persistence = & ssh.exe -o BatchMode=yes $HostAlias "sudo -n -u postgres psql -At -d epoch_auth -c 'SELECT count(*) FROM consumed_nonces'"
if ($LASTEXITCODE -ne 0 -or [int]$persistence -lt 3) { throw "Nonce persistence check failed" }
[ordered]@{
    checked_at_utc = [DateTime]::UtcNow.ToString("o")
    host = $HostAlias
    service_active = $true
    outage_failed_closed = $true
    persisted_rows = [int]$persistence
    concurrency = ($concurrency | ConvertFrom-Json)
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $evidence "acceptance.json") -Encoding UTF8

& ssh.exe -o BatchMode=yes $HostAlias "rm -f /tmp/install-postgresql.sh /tmp/epoch-auth-schema.sql /tmp/run-stage-b-tests.py"
if ($LASTEXITCODE -ne 0) { throw "Remote staging cleanup failed" }
