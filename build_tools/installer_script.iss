[Setup]
; Basic Application Information
AppName=Dead Link Checker
AppVersion=2.0.1
AppPublisher=arif98741
AppPublisherURL=https://devtobox.com
AppSupportURL=https://github.com/arif98741/deadlink-checker-python/issues
AppUpdatesURL=https://github.com/arif98741/deadlink-checker-python/releases
AppCopyright=Copyright Â© 2026 arif98741. All rights reserved.

; Installation Directories
DefaultDirName={autopf}\DeadLinkChecker
DefaultGroupName=Dead Link Checker
DisableProgramGroupPage=no
AllowNoIcons=yes

; License and Info
LicenseFile=..\docs\LICENSE.txt
InfoBeforeFile=..\docs\QUICKSTART.md
InfoAfterFile=installation_complete.txt

; Output Configuration
OutputDir=..\installer_output
OutputBaseFilename=DeadLinkChecker_Setup_v2.0.1_x64
; SetupIconFile=icon.ico

; Compression
Compression=lzma2/max
SolidCompression=yes

; Visual Style
WizardStyle=modern
; WizardImageFile=installer_banner.bmp
; WizardSmallImageFile=installer_small.bmp

; Architecture
ArchitecturesInstallIn64BitMode=x64

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Uninstall
UninstallDisplayIcon={app}\DeadLinkChecker.exe
UninstallDisplayName=Dead Link Checker v2.0.1

; Wizard Pages (Full Installation Experience)
DisableWelcomePage=no
DisableDirPage=no
DisableReadyPage=no
DisableFinishedPage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Create a &Quick Launch shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "startmenu"; Description: "Create Start &Menu shortcuts"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
; Main executable (source has version, but install without version for cleaner shortcuts)
Source: "dist\DeadLinkChecker_v2.0.1.exe"; DestDir: "{app}"; DestName: "DeadLinkChecker.exe"; Flags: ignoreversion

; Documentation
Source: "..\docs\QUICKSTART.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

; Create reports directory
Source: "..\reports\.gitkeep"; DestDir: "{app}\reports"; Flags: ignoreversion

[Dirs]
Name: "{app}\reports"; Permissions: users-modify

[Icons]
; Start Menu shortcuts (always created)
Name: "{group}\Dead Link Checker"; Filename: "{app}\DeadLinkChecker.exe"; Comment: "Analyze and report broken links on websites"
Name: "{group}\User Guide"; Filename: "{app}\QUICKSTART.md"; Comment: "Quick start guide"
Name: "{group}\Uninstall Dead Link Checker"; Filename: "{uninstallexe}"; Comment: "Uninstall Dead Link Checker"

; Desktop shortcut (if selected)
Name: "{autodesktop}\Dead Link Checker"; Filename: "{app}\DeadLinkChecker.exe"; Tasks: desktopicon; Comment: "Analyze and report broken links"

; Quick Launch shortcut (if selected)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Dead Link Checker"; Filename: "{app}\DeadLinkChecker.exe"; Tasks: quicklaunchicon

[Run]
; Option to run the application after installation
Filename: "{app}\DeadLinkChecker.exe"; Description: "Launch Dead Link Checker now"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\reports"

[Messages]
; Custom messages for professional feel
WelcomeLabel1=Welcome to Dead Link Checker Setup
WelcomeLabel2=This wizard will guide you through the installation of Dead Link Checker v2.0.1.%n%nDead Link Checker is a professional tool for analyzing and reporting broken links on websites. It helps you maintain website quality by identifying dead, broken, or problematic links.%n%nClick Next to continue.
ClickNext=Click Next to continue, or Cancel to exit Setup.
SelectDirLabel3=Setup will install Dead Link Checker in the following folder.
SelectDirBrowseLabel=To continue, click Next. If you would like to select a different folder, click Browse.
DiskSpaceMBLabel=At least [mb] MB of free disk space is required.
ConfirmUninstall=Are you sure you want to completely remove Dead Link Checker and all of its components?
UninstallStatusLabel=Please wait while Dead Link Checker is removed from your computer.
FinishedHeadingLabel=Completing Dead Link Checker Setup
FinishedLabelNoIcons=Setup has finished installing Dead Link Checker on your computer.
FinishedLabel=Setup has finished installing Dead Link Checker on your computer. The application may be launched by selecting the installed shortcuts.

[Code]
// Custom welcome message
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

// Show progress during installation
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Installation completed successfully
    Log('Installation completed successfully');
  end;
end;


