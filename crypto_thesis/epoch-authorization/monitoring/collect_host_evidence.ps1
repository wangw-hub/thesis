param(
    [Parameter(Mandatory=$true)][string]$OutputPath
)

$ErrorActionPreference = "Stop"
$os = Get-CimInstance Win32_OperatingSystem
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$disk = Get-PhysicalDisk | Select-Object FriendlyName, MediaType, Size
$time = w32tm /query /status 2>&1
$evidence = [ordered]@{
    hostname = $env:COMPUTERNAME
    collected_at_utc = [DateTime]::UtcNow.ToString("o")
    operating_system = $os.Caption
    os_version = $os.Version
    cpu = $cpu.Name
    logical_processors = $cpu.NumberOfLogicalProcessors
    memory_bytes = [int64]$os.TotalVisibleMemorySize * 1024
    disks = @($disk)
    time_sync_status = @($time)
    python_version = (python --version 2>&1 | Out-String).Trim()
}
$evidence | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
