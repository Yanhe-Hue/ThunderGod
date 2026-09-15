param(
    [Parameter(Mandatory=$true)]
    [ValidatePattern('^[D-Zd-z]$')]
    [string]$DriveLetter
)
$ErrorActionPreference = 'Stop'
try {
    $usbVolumes = @(Get-Volume -DriveLetter $DriveLetter -ErrorAction Stop)
    if ($usbVolumes.Count -ne 1 -or $usbVolumes[0].DriveType -ne 'Removable') {
        throw 'Target must be exactly one removable volume.'
    }
    $usbPartitions = @(Get-Partition -DriveLetter $DriveLetter -ErrorAction Stop)
    if ($usbPartitions.Count -ne 1) { throw 'Target partition is ambiguous.' }
    $usbDisk = $usbPartitions[0] | Get-Disk -ErrorAction Stop
    if ($usbDisk.BusType -ne 'USB' -or $usbDisk.IsBoot -or $usbDisk.IsSystem -or $usbDisk.IsReadOnly) {
        throw 'Refusing non-USB, system, boot or read-only disk.'
    }
    if (@(Get-Partition -DiskNumber $usbDisk.Number).Count -ne 1) {
        throw 'Multiple partitions detected. Refusing to format an ambiguous USB disk.'
    }
    # Format the verified volume object, not an unqualified disk or all volumes.
    $usbVolumes[0] | Format-Volume -FileSystem exFAT -NewFileSystemLabel USB_UPDATE -Force -Confirm:$false -ErrorAction Stop | Out-Null
    $formattedVolume = Get-Volume -DriveLetter $DriveLetter -ErrorAction Stop
    if ($formattedVolume.FileSystem -ne 'exFAT') { throw 'exFAT verification failed.' }
    Write-Output 'USB_FORMAT_EXFAT_COMPLETE'
} catch {
    Write-Error $_ -ErrorAction Continue
    exit 1
}
