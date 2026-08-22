#define MyAppName "CD2 Matrix Studio"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "CD2 Matrix Studio Community"
#define MyAppExeName "CD2-Matrix-Studio.exe"

[Setup]
AppId={{1CB59997-61A5-4C47-8934-4961A8D08779}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\CD2 Matrix Studio
DefaultGroupName=CD2 Matrix Studio
DisableProgramGroupPage=yes
OutputDir=..\release
OutputBaseFilename=CD2-Matrix-Studio-Setup
SetupIconFile=..\assets\app.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
