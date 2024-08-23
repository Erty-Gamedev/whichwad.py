"""
Programmatically call PyInstaller to build the executable
"""

import PyInstaller.__main__

PyInstaller.__main__.run([
    'whichwad.py',
    '--onefile',
    '-c',
    '-n', 'whichwad',
    '--version-file', 'version_win.txt',
])
