# bridge.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Recopilar todos los archivos necesarios
a = Analysis(
    ['bridge.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('estrategias/*.py', 'estrategias'),  # Incluir estrategias
        ('config.py', '.'),                   # Incluir configuración
        ('templates_db.json', '.'),           # Base de datos (si existe)
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'werkzeug',
        'jinja2',
        'markupsafe',
        'click',
        'itsdangerous',
        'json',
        'time',
        'datetime',
        'threading',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BridgeHuellas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Mostrar ventana de consola (útil para ver errores)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Crear también una versión con ventana oculta (para usuarios finales)
exe_hidden = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BridgeHuellas_Silencioso',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Sin ventana de consola (corre en background)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Crear instalador para distribuir
coll = COLLECT(
    exe,
    exe_hidden,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PuenteHuellas'
)