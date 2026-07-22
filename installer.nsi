; NSIS Installer Script para Detector de Mascarillas
; Instrucciones: Instala NSIS desde https://nsis.sourceforge.io/Download
; Luego ejecuta: "C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi

!include "MUI2.nsh"
!include "x64.nsh"

; Variables del instalador
!define APP_NAME "Detector de Mascarillas"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Tu Nombre/Universidad"
!define APP_EXE "DetectorMascarillas.exe"
!define INSTALL_DIR "$PROGRAMFILES\DetectorMascarillas"

; Configuración básica
Name "${APP_NAME} ${APP_VERSION}"
OutFile "DetectorMascarillas_Installer.exe"
InstallDir "${INSTALL_DIR}"
InstallDirRegKey HKLM "Software\${APP_NAME}" ""

; Usar compresión
SetCompressor /SOLID lzma

; ============= INTERFAZ =============
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "Spanish"

; ============= SECCIONES =============
Section "Instalar Aplicación"
  SetOutPath "${INSTALL_DIR}"
  
  ; Copiar ejecutable y archivos
  File "dist\${APP_EXE}"
  File "best_mask_mrisdi.pt"
  File "yolo11n.pt"
  File "yolov8m-mask.pt"
  File "yolov8n.pt"
  
  ; Copiar carpetas
  SetOutPath "${INSTALL_DIR}\templates"
  File /r "templates\*.*"
  
  SetOutPath "${INSTALL_DIR}\static"
  File /r "static\*.*"
  
  ; Crear acceso directo en Inicio
  SetOutPath "${INSTALL_DIR}"
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "${INSTALL_DIR}\${APP_EXE}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\Desinstalar.lnk" "$INSTDIR\Uninstall.exe"
  
  ; Crear acceso directo en Escritorio
  CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "${INSTALL_DIR}\${APP_EXE}"
  
  ; Guardar información de instalación para desinstalación
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  
  ; Crear desinstalador
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  MessageBox MB_OK "¡Instalación completada! Encontrarás un acceso directo en el Escritorio."
SectionEnd

; ============= DESINSTALADOR =============
Section "Uninstall"
  ; Eliminar archivos
  RMDir /r "${INSTALL_DIR}"
  
  ; Eliminar accesos directos
  RMDir /r "$SMPROGRAMS\${APP_NAME}"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  
  ; Eliminar información del registro
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
SectionEnd
