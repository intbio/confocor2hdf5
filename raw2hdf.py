#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) Grigoriy A. Armeev, 2015
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as·
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License v2 for more details.
# Cheers, Satary.
#
import sys, os,glob,platform,time
from shutil import copyfile
from PyQt5 import QtGui, QtCore, QtWidgets
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
import phconvert as phc
from fcsfiles import ConfoCor3Raw
import numpy as np



def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    """
    if platform.system() == 'Windows':
        return time.strftime("%d.%m.%Y \n%H:%M:%S",time.gmtime(os.path.getctime(path_to_file)))
    else:
        stat = os.stat(path_to_file)
        try:
            return time.strftime("%d.%m.%Y \n%H:%M:%S",time.gmtime(stat.st_birthtime))
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return time.strftime("%d.%m.%Y \n%H:%M:%S", time.gmtime(stat.st_mtime))
            

class FileMenu(QtWidgets.QWidget):
    '''
    Provides Widget for opening multiple files
    '''
    def __init__(self,workDir,parent=None):
        super(FileMenu, self).__init__(parent)
        self.setAcceptDrops(True)
        self.filters="confocor raw files (*.raw)"
        self.parent=parent
        self.laneWidgetList=[]

        self.foldersScrollArea = QtWidgets.QScrollArea(self)
        self.foldersScrollArea.setWidgetResizable(True)

        self.foldersScrollAreaWidget = QtWidgets.QWidget()
        self.foldersScrollAreaWidget.setGeometry(QtCore.QRect(0, 0, 380, 280))
        self.folderLayout = QtWidgets.QGridLayout(self.foldersScrollAreaWidget)
        self.folderLayout.setAlignment(QtCore.Qt.AlignTop)
        self.foldersScrollArea.setWidget(self.foldersScrollAreaWidget)
        
       
        
        openFiles = QtWidgets.QPushButton("Open RAW files")
        openFiles.clicked.connect(self.openFile)
        
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.addWidget(openFiles)
        self.mainLayout.addWidget(self.foldersScrollArea)
        
        self.setMaximumWidth(500)
        self.setGeometry(400, 200, 300, 400)
        self.setWindowTitle('RAW to hdf5') 
    

    def openFile(self):
        filename=QtWidgets.QFileDialog.getOpenFileNames(self,'Open RAW files',filter="Confocor RAW files (*.raw)")
        if filename[0]:
            self.loadFiles(filename[0])
            
    def loadFiles(self, filelist):
        result={}
        ids={}
        for name in filelist:
            t=ConfoCor3Raw(name)
            result[name]=[t.measurement_identifier,t.channel]
            if not (t.measurement_identifier in ids):
                ids[t.measurement_identifier]={t.channel:name}
            else:
                ids[t.measurement_identifier] [t.channel]=name
                
        for ex_id, data in ids.iteritems(): 
            if len(data)==2:
                self.laneWidgetList.append(fileMenuItem(data[0],data[1],fileMenu=self,mainwindow=self.parent))
                self.folderLayout.addWidget(self.laneWidgetList[-1])      
                 
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                if '.raw' in unicode(url.toLocalFile()):
                    links.append(unicode(url.toLocalFile()))
            if links:
                self.loadFiles(links)
        else:
            event.ignore()    
 

class fileMenuItem(QtWidgets.QWidget):
    nameChangedSignal = QtCore.pyqtSignal(QtWidgets.QWidget)
    def __init__(self,ch0_filename,ch1_filename,mainwindow=None,fileMenu=None):
        super(fileMenuItem, self).__init__()
        self.ch0_filename=ch0_filename
        self.ch1_filename=ch1_filename
        self.fileMenu=fileMenu
        self.mainwindow=mainwindow
        
        
        self.Layout = QtWidgets.QGridLayout(self)
        self.Layout.setSpacing(0)
        self.Layout.setContentsMargins(0,0,0,0)
        self.Layout.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        timestamp=QtWidgets.QLabel(creation_date(self.ch0_filename))
        self.r_button = QtWidgets.QPushButton('ch1: %s \nch2: %s'%(os.path.basename(self.ch0_filename), os.path.basename(self.ch1_filename)))
        self.r_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        #self.r_button.setFixedWidth(50)
        self.r_button.setStyleSheet("text-align: left;padding: 3px")    
        self.r_button.clicked.connect(self.runTask)
        
        
        self.Layout.addWidget(timestamp,0,0)
        self.Layout.addWidget(self.r_button,0,1)
    def runTask(self):
        self.eW=exportWidget(self.ch0_filename,self.ch1_filename)
        self.eW.show()
        
class exportWidget(QtWidgets.QWidget):
    '''
    Provides Widget for opening multiple files
    '''
    def __init__(self,ch0_filename,ch1_filename,parent=None):
        super(exportWidget, self).__init__(parent)
        self.Layout = QtWidgets.QGridLayout(self)
        self.Layout.setSpacing(0)
        self.Layout.setContentsMargins(0,0,0,0)
        self.filenames=[ch0_filename,ch1_filename]
        #self.Layout.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        
        label=QtWidgets.QLabel('Sample name*:')
        self.Layout.addWidget(label,0,0)
        self.sampleNameWidget=QtWidgets.QLineEdit()
        self.Layout.addWidget(self.sampleNameWidget,0,1)
        
        label=QtWidgets.QLabel('Buffer name*:')
        self.Layout.addWidget(label,1,0)
        self.bufferNameWidget=QtWidgets.QLineEdit()
        self.Layout.addWidget(self.bufferNameWidget,1,1)
        
        label=QtWidgets.QLabel('Author*:')
        self.Layout.addWidget(label,2,0)
        self.authorWidget=QtWidgets.QLineEdit()
        self.Layout.addWidget(self.authorWidget,2,1)
        
        label=QtWidgets.QLabel('Donor name:')
        self.Layout.addWidget(label,3,0)
        self.donorNameWidget=QtWidgets.QLineEdit('Cy3')
        self.Layout.addWidget(self.donorNameWidget,3,1)
        
        label=QtWidgets.QLabel('Acceptor name:')
        self.Layout.addWidget(label,4,0)
        self.acceptorNameWidget=QtWidgets.QLineEdit('Cy5')
        self.Layout.addWidget(self.acceptorNameWidget,4,1)
        
        label=QtWidgets.QLabel('Description*:')
        self.Layout.addWidget(label,0,2)
        self.descriptionWidget=QtWidgets.QLineEdit()
        self.Layout.addWidget(self.descriptionWidget,0,3)
        
        label=QtWidgets.QLabel('Affiliation:')
        self.Layout.addWidget(label,1,2)
        self.affiliationWidget=QtWidgets.QLineEdit('MSU, Biology Faculty')
        self.Layout.addWidget(self.affiliationWidget,1,3)
        
        label=QtWidgets.QLabel('Excitation w.l.:')
        self.Layout.addWidget(label,2,2)
        self.excitationWLWidget=QtWidgets.QSpinBox()
        self.excitationWLWidget.setMinimum(400)
        self.excitationWLWidget.setMaximum(800)
        self.excitationWLWidget.setValue(514)
        self.excitationWLWidget.setSingleStep(1)
        self.Layout.addWidget(self.excitationWLWidget,2,3)
        
        label=QtWidgets.QLabel('Donor w.l.:')
        self.Layout.addWidget(label,3,2)
        self.donorWLWidget=QtWidgets.QSpinBox()
        self.donorWLWidget.setMinimum(400)
        self.donorWLWidget.setMaximum(800)
        self.donorWLWidget.setSingleStep(1)
        self.donorWLWidget.setValue(580)
        self.Layout.addWidget(self.donorWLWidget,3,3)
        
        label=QtWidgets.QLabel('Acceptor w.l.:')
        self.Layout.addWidget(label,4,2)
        self.acceptorWLWidget=QtWidgets.QSpinBox()
        self.acceptorWLWidget.setMinimum(400)
        self.acceptorWLWidget.setMaximum(800)
        self.acceptorWLWidget.setValue(650)
        self.acceptorWLWidget.setSingleStep(1)
        self.Layout.addWidget(self.acceptorWLWidget,4,3)
        
        
        self.r_button = QtWidgets.QPushButton('Save h5 file')
        self.r_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        #self.r_button.setFixedWidth(50)
        self.r_button.setStyleSheet("text-align: left;padding: 3px")    
        #self.r_button.clicked.connect(self.runTask)
        
        
        self.Layout.addWidget(self.r_button,5,0)
        self.r_button.clicked.connect(self.save)
        
    def save(self):
        ch1raw=ConfoCor3Raw(self.filenames[0])
        ch2raw=ConfoCor3Raw(self.filenames[1])
        
        ch1raw._fh.seek(128)
        times = np.fromfile(ch1raw._fh, dtype='<u4', count=-1)
        times_acceptor = np.cumsum(times.astype('u8'))

        ch2raw._fh.seek(128)
        times = np.fromfile(ch2raw._fh, dtype='<u4', count=-1)
        times_donor = np.cumsum(times.astype('u8'))

        df = np.hstack([np.vstack( [   times_donor, np.zeros(   times_donor.size)] ),
                        np.vstack( [times_acceptor,  np.ones(times_acceptor.size)] )]).T

        # sorting photons
        df_sorted = df[np.argsort(df[:,0])].T

        timestamps=df_sorted[0].astype('int64')
        timestamps_unit = 1.0/ch1raw.frequency
        detectors=df_sorted[1].astype('uint8')
        # [0,1,2,3,4,5,6,7] - timestamps
        # [0,1,1,0,1,0,1,1] - acceptor mask

        try:
            description = self.descriptionWidget.text().encode('ascii')

            author = self.authorWidget.text().encode('ascii')
            author_affiliation = self.affiliationWidget.text().encode('ascii')

            sample_name = self.sampleNameWidget.text().encode('ascii')
            buffer_name = self.bufferNameWidget.text().encode('ascii')
            dye_names = '%s, %s'%(self.donorNameWidget.text().encode('ascii'),self.acceptorNameWidget.text().encode('ascii'))   # Comma separates names of fluorophores
        except:
            error_dialog = QtWidgets.QErrorMessage(self)
            error_dialog.setWindowModality(QtCore.Qt.WindowModal)
            error_dialog.showMessage('Only ASCII symbols allowed (only English)')
            return
        
        if not description or not author or not sample_name or not buffer_name:
            error_dialog = QtWidgets.QErrorMessage(self)
            error_dialog.setWindowModality(QtCore.Qt.WindowModal)
            error_dialog.showMessage('Fill all fields marked with asterix')
            return

        photon_data = dict(
            timestamps=timestamps,
            detectors=detectors,
            timestamps_specs={'timestamps_unit': timestamps_unit})

        setup = dict(
            ## Mandatory fields
            num_pixels = 2,                   # using 2 detectors
            num_spots = 1,                    # a single confoca excitation
            num_spectral_ch = 2,              # donor and acceptor detection 
            num_polarization_ch = 1,          # no polarization selection 
            num_split_ch = 1,                 # no beam splitter
            modulated_excitation = False,     # CW excitation, no modulation 
            excitation_alternated = [False],  # CW excitation, no modulation 
            lifetime = False,                 # no TCSPC in detection
            
            ## Optional fields
            excitation_wavelengths = [self.excitationWLWidget.value()*10e-9],         # List of excitation wavelenghts
            excitation_cw = [True],                    # List of booleans, True if wavelength is CW
            detection_wavelengths = [self.donorWLWidget.value()*10e-9,
                                     self.acceptorWLWidget.value()*10e-9],  # Nominal center wavelength 
                                                       # each for detection ch
        )

        identity = dict(
            author=author,
            author_affiliation=author_affiliation)

        measurement_specs = dict(
            measurement_type = 'smFRET',
            detectors_specs = {'spectral_ch1': [0],  # list of donor's detector IDs
                               'spectral_ch2': [1]}  # list of acceptor's detector IDs
            )

        photon_data['measurement_specs'] = measurement_specs

        data = dict(
            description=description,
            photon_data = photon_data,
            setup=setup,
            identity=identity
        )
        filename=QtWidgets.QFileDialog.getSaveFileName(self,'Save smFRET data file',filter="hdf5 files (*.h5)")        
        if filename[0]:
            phc.hdf5.save_photon_hdf5(data, h5_fname=filename[0], overwrite=True)
        
        
def main():
    
    app = QtWidgets.QApplication(sys.argv)
    workDir=unicode(QtCore.QDir.currentPath())
    ex = FileMenu(workDir)
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()    

