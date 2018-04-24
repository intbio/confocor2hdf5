# confocor2hdf5
Simple GUI application for bulk conversion of  Zeiss ConfoCor3 raw data files to photon hdf5

Application is written with PyQT5 and depends on [Photon hdf5 converter](http://photon-hdf5.github.io/).

Application purpouse is to convert smFRET raw data files (cw excitation, single FRET pair).

Exported files than can be read with [fretbursts](https://github.com/OpenSMFS/FRETBursts).

If you hate GUIs see [example notebook](confocor2hdf5.ipynb)
## Windows users (as ZEN works only on windows)
Download latest installer from [releases page](https://github.com/intbio/confocor2hdf5/releases)
## Using through conda (use python 3.*)
- `conda install -c conda-forge phconvert pyqt `
- clone this repo
- run `python raw2hdf.py`

## Creating windows installer

- `conda install -c conda-forge pyinstaller`
- change .spec file ('needed' var contains abolute paths)
- `pyinstaller raw2hdf_onedir.spec`
- compile installer with inno setup using iss script
