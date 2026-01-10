# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../src/deadlink_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        # GUI Framework
        'customtkinter',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        
        # Image Processing
        'PIL',
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageTk',
        
        # PDF Generation
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.pdfgen.canvas',
        'reportlab.lib',
        'reportlab.lib.colors',
        'reportlab.lib.pagesizes',
        'reportlab.lib.styles',
        'reportlab.lib.units',
        'reportlab.lib.enums',
        'reportlab.platypus',
        'reportlab.platypus.tableofcontents',
        
        # Web Scraping
        'bs4',
        'requests',
        'urllib',
        'urllib.parse',
        
        # Standard Library (explicitly include)
        'csv',
        'io',
        'sys',
        'os',
        'threading',
        'queue',
        'datetime',
        'pathlib',
        'webbrowser',
        'dataclasses',
        'typing',
        'collections',
        'concurrent.futures',
        're',
        'argparse',
        'time',
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
    a.zipfiles,
    a.datas,
    [],
    name='DeadLinkChecker_v2.0.1',  # Include version in filename
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console window (buffer issue is now fixed)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
    version='version_info.txt',  # Add version information
)



