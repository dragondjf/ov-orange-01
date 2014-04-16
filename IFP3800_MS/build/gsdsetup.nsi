;NSIS Modern User Interface
;Setup Script for ifpms win32, private xulrunner
;Written by andy
;Modified by andy
#KH changed by kanhao
;--------------------------------
# var by KH
# Var __DATE__
#--------------------------------  
;Include Modern UI

  !include "MUI2.nsh"
  !include WordFunc.nsh
  !include LogicLib.nsh
  !include "FileFunc.nsh"

;--------------------------------
;General
  !define LANG_ENGLISH 1033
  !define MUI_ICON "chrome\icons\default\ifpms.ico"
  !define MUI_UNICON "chrome\icons\default\uninstall.ico"
  
#KH  !define MUI_HEADERIMAGE
#KH  !define MUI_HEADERIMAGE_BITMAP "chrome\skin\default\Icons\ifpms.png"
#KH  !define MUI_WELCOMEFINISHPAGE_BITMAP "mui-welcome.bmp"
#   BrandingText "光谷.奥源 智能光纤周界安防系统"
  !define VERSION "1.2"
  !define PRODUCT_NAME "gsd"
  !define PRODUCT_VERSION "${VERSION}.$%BUILD%.$%DATE%"
  !define PRODUCT_DESCRIPTION "package ifpms test"
  !define COMPANY_FULLNAME "Onevo Co., Ltd."
  !define COMPANY_WEBSITE "http://www.ov-orange.com/"
  !define PRODUCT_EXECUTE_FILE "gsd.exe"
  !define PRODUCT_REGKEY "Software\${PRODUCT_NAME}"
   
  ;Name and file
  Name "${PRODUCT_NAME}"
  OutFile ".\setup-v${VERSION}-r$%BUILD%-b$%DATE%.exe"
  VIAddVersionKey /LANG=${LANG_ENGLISH} "Comments" "${PRODUCT_DESCRIPTION}"
  VIAddVersionKey /LANG=${LANG_ENGLISH} "CompanyName" "${COMPANY_FULLNAME}"
  VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalTrademarks" "${PRODUCT_NAME} Application is a trademark of ${COMPANY_FULLNAME}"
  VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalCopyright" "漏${COMPANY_FULLNAME}"
  VIAddVersionKey /LANG=${LANG_ENGLISH} "FileDescription" "${PRODUCT_DESCRIPTION}"
  VIAddVersionKey /LANG=${LANG_ENGLISH} "FileVersion" "${PRODUCT_VERSION}"
  VIProductVersion "${PRODUCT_VERSION}"
  ;Default installation folder
  InstallDir "$PROGRAMFILES\${PRODUCT_NAME}"
  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "${PRODUCT_REGKEY}" ""


;--------------------------------
;  Variables
  Var MUI_TEMP
  Var STARTMENU_FOLDER

;--------------------------------
;  Interface Settings

  !define MUI_ABORTWARNING
 
;--------------------------------
;  Pages
  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "chrome\license.txt"
;  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY

  ;Start Menu Folder Page Configuration
  !define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU"
  !define MUI_STARTMENUPAGE_REGISTRY_KEY "${PRODUCT_REGKEY}"
  !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
  !define MUI_STARTMENUPAGE_DEFAULTFOLDER "\${PRODUCT_NAME}"

  !insertmacro MUI_PAGE_STARTMENU Application $STARTMENU_FOLDER
  
  !insertmacro MUI_PAGE_INSTFILES

  !ifdef README_FILE
	!define MUI_FINISHPAGE_SHOWREADME "$PROGRAMFILES\${PRODUCT_NAME}\${README_FILE}"
	!define MUI_FINISHPAGE_SHOWREADME_TEXT "Show Readme"
  !endif

  !define MUI_FINISHPAGE_RUN "$INSTDIR\${PRODUCT_EXECUTE_FILE}"
 #!define MUI_FINISHPAGE_RUN_TEXT "Launch ${PRODUCT_NAME}"
  !define MUI_FINISHPAGE_RUN_TEXT "运行${PRODUCT_NAME}"

  !insertmacro MUI_PAGE_FINISH
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH
  
;--------------------------------
;  Languages files
  !insertmacro MUI_LANGUAGE "English"
  !insertmacro MUI_LANGUAGE "SimpChinese"
  !insertmacro MUI_LANGUAGE "TradChinese"

;--------------------------------
;Installer Sections
Section "Main Section" SecMain

    SetOutPath "$INSTDIR"
    File /r "chrome"
	IfFileExists "$INSTDIR\custom.conf.bak" 0 +2
	Rename "$INSTDIR\custom.conf.bak" "$INSTDIR\chrome\etc\custom.conf"
		
 	SetOutPath "$INSTDIR"
	File /r "defaults"
	
	SetOutPath "$INSTDIR"
	File /r "extensions"
	
    SetOutPath "$INSTDIR"
	File /nonfatal /r "log"	
	
	SetOutPath "$INSTDIR"
	File /nonfatal /r "sample"
    
	SetOutPath "$INSTDIR"
    File /r "xulrunner"
	File "application.ini"
	File "gsd.exe"
	File "debug.bat"
	File "show_wave.bat"
	
    !ifdef README_FILE
    File "doc\${README_FILE}"
    !endif

    ;Store installation folder
    WriteRegStr HKCU "${PRODUCT_REGKEY}" "" $INSTDIR

    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayName" "${PRODUCT_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "Publisher" "${COMPANY_FULLNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "HelpLink" "${COMPANY_WEBSITE}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayVersion " "${PRODUCT_VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "UninstallString" "$INSTDIR\Uninstall.exe"

    ;Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application

    ;Create shortcuts
    CreateDirectory "$SMPROGRAMS\$STARTMENU_FOLDER"
    CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\${PRODUCT_NAME}.lnk" "$INSTDIR\${PRODUCT_EXECUTE_FILE}"
    CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\${PRODUCT_EXECUTE_FILE}"

    !ifdef README_FILE
      CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\Readme.lnk" "$INSTDIR\${README_FILE}"
    !endif

    !insertmacro MUI_STARTMENU_WRITE_END

SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecMain ${LANG_ENGLISH} "Main section."

  ;Assign language strings to sections
  ;!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  ;  !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} $(DESC_SecMain)
  ;!insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ;DELETE YOUR OWN FILES HERE...
MessageBox MB_YESNO|MB_ICONINFORMATION "是否保存配置文件和日志文件? " IDYES  +2
      RMDir /r "$INSTDIR"
	  	  
Rename "$INSTDIR\chrome\etc\custom.conf" "$INSTDIR\custom.conf.bak" 
RMDir /r "$INSTDIR\chrome"
#CreateDirectory "$INSTDIR\chrome\content\etc\"
RMDir /r "$INSTDIR\defaults"
RMDir /r "$INSTDIR\extensions"
RMDir /r "$INSTDIR\sample"
RMDir /r "$INSTDIR\xulrunner"
Delete "$INSTDIR\application.ini"
Delete "$INSTDIR\gsd.exe"
Delete "$INSTDIR\debug.bat"
Delete "$INSTDIR\show_wave.bat"
Delete "$INSTDIR\Uninstall.exe"

	  
  !insertmacro MUI_STARTMENU_GETFOLDER Application $MUI_TEMP

  Delete "$SMPROGRAMS\$MUI_TEMP\Uninstall.lnk"
  Delete "$SMPROGRAMS\$MUI_TEMP\${PRODUCT_NAME}.lnk"
  Delete "$SMPROGRAMS\Startup\${PRODUCT_NAME}.lnk"
  Delete "$DESKTOP\${PRODUCT_NAME}.lnk"

  !ifdef README_FILE
    Delete "$SMPROGRAMS\$MUI_TEMP\Readme.lnk"
  !endif

  ;Delete empty start menu parent diretories
  StrCpy $MUI_TEMP "$SMPROGRAMS\$MUI_TEMP"

  startMenuDeleteLoop:
	ClearErrors
    RMDir $MUI_TEMP
    GetFullPathName $MUI_TEMP "$MUI_TEMP\.."

    IfErrors startMenuDeleteLoopDone

    StrCmp $MUI_TEMP $SMPROGRAMS startMenuDeleteLoopDone startMenuDeleteLoop
  startMenuDeleteLoopDone:

  DeleteRegKey /ifempty HKCU "${PRODUCT_REGKEY}"

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"

SectionEnd
