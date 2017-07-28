# -*- mode: python -*-

block_cipher = None


a = Analysis(['miner.py'],
             pathex=['F:\\Documents\\Learning\\Python\\orchestrator'],
             binaries=[],
             datas=[],
             hiddenimports=['email', 'email.message', 'email.mime.message',
             'email.mime.image', 'email.mime.text', 'email.mime.multipart',
             'email.mime.audio', 'email.mime.multipart'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='miner',
          debug=False,
          strip=False,
          upx=True,
          console=True )
