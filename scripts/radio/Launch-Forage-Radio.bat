@echo off
REM Forage Radio PowerShell Launcher
REM This version uses -NoExit so the window stays open even if the script errors or finishes.

powershell.exe -NoExit -ExecutionPolicy Bypass -File "%~dp0Forage-Radio.ps1" %*