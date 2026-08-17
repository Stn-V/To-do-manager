; =====================================================
;  Скрипт установщика для ToDoManager
;  Файл: installer.iss (лежит в корне проекта)
;  Компиляция: Ctrl+F9 в Inno Setup Compiler
; =====================================================

#define MyAppName "ToDoManager"
#define MyAppVersion "1.0"
#define MyAppPublisher "To-Do Manager Team"
#define MyAppExeName "ToDoManager.exe"

[Setup]
; Уникальный ID приложения — НЕ меняйте его при будущих обновлениях,
; чтобы Windows понимал, что это та же самая программа
AppId={{B7F3A2E1-4C9D-4E8A-9F12-3D6E5A8C21B0}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

; Установка в C:\Users\<юзер>\AppData\Local\Programs\ToDoManager
; — там у программы будут права на запись (папка data, tasks.json)
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}

; Не запрашивать права администратора
PrivilegesRequired=lowest

; Куда положить готовый установщик и как его назвать
OutputDir=installer_output
OutputBaseFilename=ToDoManagerSetup
SetupIconFile=app_icon.ico

Compression=lzma2
SolidCompression=yes

; Современный аккуратный вид окон установщика
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Создать ярлык на рабочем столе"; GroupDescription: "Дополнительные ярлыки:"

[Files]
; Копируем собранный exe из папки dist в папку установки
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Ярлык в меню «Пуск» (иконка берётся из самого exe)
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; Ярлык на рабочем столе
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Галочка «Запустить программу сейчас» в конце установки
Filename: "{app}\{#MyAppExeName}"; Description: "Запустить {#MyAppName} сейчас"; Flags: nowait postinstall skipifsilent