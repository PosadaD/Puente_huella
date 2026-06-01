; instalador.iss
[Setup]
AppName=Puente de Huellas
AppVersion=1.0
DefaultDirName={pf}\PuenteHuellas
DefaultGroupName=Puente Huellas
UninstallDisplayIcon={app}\BridgeHuellas_Background.exe
Compression=lzma2
SolidCompression=yes
OutputDir=.
OutputBaseFilename=Instalar_Puente_Huellas

[Files]
Source: "dist\BridgeHuellas_Background.exe"; DestDir: "{app}"
Source: "dist\*"; DestDir: "{app}"
Source: "templates_db.json"; DestDir: "{app}"

[Icons]
Name: "{group}\Puente Huellas"; Filename: "{app}\BridgeHuellas_Background.exe"
Name: "{group}\Desinstalar"; Filename: "{uninstallexe}"
Name: "{autostart}\Puente Huellas"; Filename: "{app}\BridgeHuellas_Background.exe"

[Run]
Filename: "{app}\BridgeHuellas_Background.exe"; Description: "Iniciar Puente de Huellas"; Flags: postinstall nowait