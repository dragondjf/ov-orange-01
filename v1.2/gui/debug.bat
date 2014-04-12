

if "%OS%" == "Windows_NT" goto NT
:WIN7
RMDIR /S /Q "%HOMEDRIVE%%HOMEPATH%\AppData\Roaming\ov-orange"
RMDIR /S /Q "%HOMEDRIVE%%HOMEPATH%\AppData\Local\ov-orange"
goto start

:NT
RMDIR /S /Q "%HOMEDRIVE%%HOMEPATH%\Application Data\ov-orange"

:start

set PYTHONHOME=%cd%\extensions\pythonext@mozdev.org\python
set PYTHONPATH=%cd%\extensions\pythonext@mozdev.org\pylib

start xulrunner\xulrunner.exe application.ini -jsconsole