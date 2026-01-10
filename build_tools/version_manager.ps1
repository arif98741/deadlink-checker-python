# Version Manager for Dead Link Checker

$versionFile = Join-Path $PSScriptRoot "..\src\deadlink\version.py"
$versionInfoFile = Join-Path $PSScriptRoot "version_info.txt"
$installerFile = Join-Path $PSScriptRoot "installer_script.iss"
$specFile = Join-Path $PSScriptRoot "deadlink_gui.spec"

# 1. Read current version from src/deadlink/version.py
$versionContent = Get-Content $versionFile -Raw
if ($versionContent -match 'VERSION = "(\d+)\.(\d+)\.(\d+)"') {
    $major = $matches[1]
    $minor = $matches[2]
    $patch = [int]$matches[3] + 1
    $newVersion = "$major.$minor.$patch"
    $newVersionFull = "$major.$minor.$patch.0"
    $newVersionTuple = "$major, $minor, $patch, 0"
} else {
    Write-Error "Could not parse version from $versionFile"
    exit 1
}

Write-Host "Updating version to: $newVersion" -ForegroundColor Green

# 2. Update src/deadlink/version.py
$newVersionContent = $versionContent -replace 'VERSION = "\d+\.\d+\.\d+"', "VERSION = `"$newVersion`""
$newVersionContent | Set-Content $versionFile -Encoding UTF8

# 3. Update build_tools/version_info.txt
if (Test-Path $versionInfoFile) {
    $viContent = Get-Content $versionInfoFile -Raw
    $viContent = $viContent -replace 'filevers=\(\d+, \d+, \d+, \d+\)', "filevers=($newVersionTuple)"
    $viContent = $viContent -replace 'prodvers=\(\d+, \d+, \d+, \d+\)', "prodvers=($newVersionTuple)"
    $viContent = $viContent -replace "StringStruct\(u'FileVersion', u'\d+\.\d+\.\d+\.\d+'\)", "StringStruct(u'FileVersion', u'$newVersionFull')"
    $viContent = $viContent -replace "StringStruct\(u'ProductVersion', u'\d+\.\d+\.\d+\.\d+'\)", "StringStruct(u'ProductVersion', u'$newVersionFull')"
    $viContent | Set-Content $versionInfoFile -Encoding UTF8
}

# 4. Update build_tools/installer_script.iss
if (Test-Path $installerFile) {
    $issContent = Get-Content $installerFile -Raw
    $issContent = $issContent -replace 'AppVersion=\d+\.\d+(\.\d+)?', "AppVersion=$newVersion"
    $issContent = $issContent -replace 'OutputBaseFilename=DeadLinkChecker_Setup_v\d+\.\d+\.\d+_x64', "OutputBaseFilename=DeadLinkChecker_Setup_v${newVersion}_x64"
    $issContent = $issContent -replace 'DeadLinkChecker_v\d+\.\d+', "DeadLinkChecker_v$newVersion"
    $issContent = $issContent -replace 'Dead Link Checker v\d+\.\d+', "Dead Link Checker v$newVersion"
    $issContent | Set-Content $installerFile -Encoding UTF8
}

# 5. Update build_tools/deadlink_gui.spec
if (Test-Path $specFile) {
    $specContent = Get-Content $specFile -Raw
    $specContent = $specContent -replace "name='DeadLinkChecker_v\d+\.\d+'", "name='DeadLinkChecker_v$newVersion'"
    $specContent | Set-Content $specFile -Encoding UTF8
}

Write-Host "Version updated successfully to $newVersion" -ForegroundColor Green
return $newVersion
