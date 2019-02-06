@echo off
pushd %~dp0

echo "Ending python processes, if running..."
taskkill /IM pythonw.exe /F
taskkill /IM python.exe /F

rem copy tpo.py
echo "Copying new file"
copy tpo.py "%ProgramFiles(x86)%\Python36-32"

echo "Restarting python process."
start "" "%ProgramFiles(x86)%\Python36-32\pythonw.exe" "%ProgramFiles(x86)%\Python36-32\tpo.py"

exit

