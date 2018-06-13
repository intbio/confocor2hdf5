# -*- mode: python -*-

block_cipher = None
needed=[('phconvert\\specs\\photon-hdf5_specs.json',
'C:\\miniconda\\envs\\fretbursts\\Lib\\site-packages\\phconvert\\specs\\photon-hdf5_specs.json','DATA'),
('phconvert\\v04\\specs\\photon-hdf5_specs.json',
'C:\\miniconda\\envs\\fretbursts\\Lib\\site-packages\\phconvert\\v04\\specs\\photon-hdf5_specs.json','DATA'),
('platforms\\qwindows.dll',
'C:\\miniconda\\envs\\fretbursts\\Library\\plugins\\platforms\\qwindows.dll','DATA')]

a = Analysis(['raw2hdf.py'],
             pathex=['C:\\Users\\Grigoriy Armeev\\Documents\\GitHub\\confocor2hdf5'],
             binaries=[],
             datas=[],
             hiddenimports=[],
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
          exclude_binaries=True,
          name='raw2hdf',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          runtime_tmpdir=None )
          

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               needed,
               strip=False,
               upx=True,
               name='raw2hdf')
