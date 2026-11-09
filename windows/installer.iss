; Instalador de CSF Scraper API
;
; Compilar con:
;   "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" windows\installer.iss
; o abrir este archivo con Inno Setup Compiler y presionar Compile.
;
; Requiere que exista ..\dist\csf-scraper-api.exe. Genéralo primero con:
;   python windows\build_exe.py
;
; El instalador se generará en ..\dist\csf-scraper-api-setup-<version>.exe

#define MyAppName "CSF Scraper API"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Intelisof"
#define MyAppURL "https://intelisof.com.mx/"
#define MyAppExeName "csf-scraper-api.exe"

#define ProjectRoot AddBackslash(SourcePath) + ".."
#define BuiltExe AddBackslash(ProjectRoot) + "dist\" + MyAppExeName
#define AppIcon AddBackslash(SourcePath) + "assets\app.ico"

#if !FileExists(BuiltExe)
  #error "No se encontró dist\csf-scraper-api.exe. Ejecuta primero: python windows\build_exe.py"
#endif

[Setup]
AppId={{A654D90D-1C7B-4D60-94C1-20720B1A42F6}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=..\dist
OutputBaseFilename=csf-scraper-api-setup-{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
CloseApplications=yes
RestartApplications=no
VersionInfoVersion=1.0.0.0
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Instalador de {#MyAppName}
#if FileExists(AppIcon)
SetupIconFile={#AppIcon}
#endif

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "startup"; Description: "Iniciar {#MyAppName} automáticamente al iniciar Windows"; GroupDescription: "Opciones adicionales:"; Flags: unchecked

[Files]
Source: "{#BuiltExe}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Iniciar {#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

[Registry]
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "CsfScraperApi"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: startup

[Run]
Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Description: "Iniciar {#MyAppName} ahora"; Flags: nowait postinstall skipifsilent runasoriginaluser

[UninstallRun]
Filename: "{sys}\taskkill.exe"; Parameters: "/F /IM {#MyAppExeName}"; Flags: runhidden; RunOnceId: "StopCsfScraperApi"
