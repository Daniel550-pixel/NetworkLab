[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$requiredCommands = @(
    'Get-NetAdapter',
    'Get-NetIPConfiguration',
    'Get-Service',
    'Test-Connection'
)

$results = foreach ($command in $requiredCommands) {
    $available = $null -ne (Get-Command $command -ErrorAction SilentlyContinue)
    [PSCustomObject]@{
        Command = $command
        Available = $available
    }
}

$python = Get-Command python -ErrorAction SilentlyContinue

[PSCustomObject]@{
    Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    ComputerName = $env:COMPUTERNAME
    PowerShellVersion = $PSVersionTable.PSVersion.ToString()
    PythonAvailable = [bool]$python
    RequiredCommands = $results
} | ConvertTo-Json -Depth 5

if ($results.Available -contains $false) {
    exit 1
}
