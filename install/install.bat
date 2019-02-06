@echo off

set mydir=%~dp0
Powershell -Command "& { Start-Process \"%mydir%b_inst.bat\" -verb RunAs}"
