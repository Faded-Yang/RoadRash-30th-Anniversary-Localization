@echo off
setlocal
cd /d "%~dp0"
echo ==================================================
echo   Road Rash 30th Anniversary - Localization
echo ==================================================
echo.
if not exist "installer.exe.gz.b64" (
  echo [ERROR] installer.exe.gz.b64 not found next to this script.
  pause & exit /b 1
)
set "TMPEXE=%TEMP%\rr_loc_installer.exe"
echo Unpacking installer...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$b=[IO.File]::ReadAllText((Join-Path (Get-Location) 'installer.exe.gz.b64')); $gz=[Convert]::FromBase64String($b); $ms=New-Object IO.MemoryStream (,$gz); $g=New-Object IO.Compression.GZipStream($ms,[IO.Compression.CompressionMode]::Decompress); $o=New-Object IO.MemoryStream; $g.CopyTo($o); [IO.File]::WriteAllBytes('%TMPEXE%',$o.ToArray())"
if errorlevel 1 ( echo [ERROR] unpack failed & pause & exit /b 1 )
start "" "%TMPEXE%"
exit /b 0
