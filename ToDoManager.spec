# -*- mode: python ; coding: utf-8 -*-

datas = []
binaries = []
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtSvg',
]

excludes = [
    'PySide6.Qt3DCore', 'PySide6.Qt3DRender', 'PySide6.Qt3DInput',
    'PySide6.QtWebEngine', 'PySide6.QtWebEngineCore', 'PySide6.QtWebChannel',
    'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets',
    'PySide6.QtCharts', 'PySide6.QtDataVisualization',
    'PySide6.QtQuick', 'PySide6.QtQml', 'PySide6.QtQuickWidgets',
    'PySide6.QtBluetooth', 'PySide6.QtNfc', 'PySide6.QtPositioning',
    'PySide6.QtSensors', 'PySide6.QtSerialPort', 'PySide6.QtSql',
    'PySide6.QtTest', 'PySide6.QtXml', 'PySide6.QtNetwork',
    'PySide6.QtOpenGL', 'PySide6.QtOpenGLWidgets',
    'tkinter', 'unittest', 'xmlrpc', 'pydoc',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ToDoManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',
)