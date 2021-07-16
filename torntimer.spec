# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew, gstreamer

block_cipher = None



a = Analysis(['main.py'],
             pathex=['C:\\Users\\Tom\\PycharmProjects\\TornTimer'],
             binaries=[('C:\\Users\\Tom\\PycharmProjects\\TornTimer\\resources\\*.wav', "resources")],
             datas=[('C:\\Users\\Tom\\PycharmProjects\\TornTimer\\torntimer2.kv', ".")],
             hiddenimports=[
				 'webbrowser',
				 '__init__',
				 'data.__init__',
				 'data.screens.__init__',
				 'data.screens.dbmanager',
				 'data.screens.db_kv.__init__',
				 'data.screens.db_kv.backupsd',],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
			 
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
		  a.scripts,
		  a.binaries,
		  a.zipfiles,
		  a.datas,
		  *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins + gstreamer.dep_bins)],
          [],
          exclude_binaries=False,
          name='torntimer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
