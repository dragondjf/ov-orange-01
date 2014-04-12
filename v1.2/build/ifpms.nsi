; Pencil Launcher
;--------------

Name "ifpms"
Caption "ifpms"
Icon "app\chrome\content\Icons\ifpms.ico"
OutFile "ifpms.exe"

SilentInstall silent
AutoCloseWindow true
ShowInstDetails nevershow

Section ""
    StrCpy $0 '"$EXEDIR\xulrunner\xulrunner.exe" --app "$EXEDIR\app\application.ini"'
    Exec $0
SectionEnd