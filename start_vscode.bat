rem @echo off

::set PATH=%PATH:C:\Linkout\bin;=%
:: call %~dp0envnode.bat

::set PYTHON=C:\local\Python27\python.exe

call envmsys
start "" C:\local\VSCode\Code.exe "%~dp0"
