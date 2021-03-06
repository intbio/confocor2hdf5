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
import sys, os
#from shutil import copyfile
from PyQt5 import QtGui, QtCore, QtWidgets
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
import phconvert as phc
from fcsfiles import ConfoCor3Raw
import numpy as np
from autoCompBox import autoCompBox


def creation_date(path_to_file,formated=True):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    """
    if formated:
        return QtCore.QFileInfo(path_to_file).lastModified().toLocalTime().toString('dd.MM.yyyy\nhh:mm:ss')
    else:
        return QtCore.QFileInfo(path_to_file).lastModified().toMSecsSinceEpoch()
    
def GetHumanReadable(size,precision=2):
    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1 #increment the index of the suffix
        size = size/1024.0 #apply the division
    return "%.*f%s"%(precision,size,suffixes[suffixIndex])

class FileMenu(QtWidgets.QWidget):
    '''
    Provides Widget for opening multiple files
    '''
    def __init__(self,workDir=None,parent=None):        
        super(FileMenu, self).__init__(parent)
        
        self.settings = QtCore.QSettings()
        #self.settings.setValue("sampleNames", ['FACT','notFact'])
        try:
            self.last_dir_opened = self.settings.value("last_folder", ".")
        except:
            self.last_dir_opened = QtCore.QDir.currentPath()
        
        self.setAcceptDrops(True)
        self.filters="confocor raw files (*.raw)"
        self.parent=parent
        self.laneWidgetList=[]
        self.sort_by_time=[]
        self.ch0_name_list=[]
        self.dataFrame=[]
        self.numFiles=0

        self.foldersScrollArea = QtWidgets.QScrollArea(self)
        self.foldersScrollArea.setWidgetResizable(True)

        self.foldersScrollAreaWidget = QtWidgets.QWidget()
        self.foldersScrollAreaWidget.setGeometry(QtCore.QRect(0, 0, 380, 280))
        self.folderLayout = QtWidgets.QGridLayout(self.foldersScrollAreaWidget)
        self.folderLayout.setAlignment(QtCore.Qt.AlignTop)
        self.foldersScrollArea.setWidget(self.foldersScrollAreaWidget)
        self.folderLayout.addWidget(header())
        
       
        
        openFiles = QtWidgets.QPushButton("Open RAW files")
        openFiles.clicked.connect(self.openFile)
        
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.addWidget(openFiles)
        self.mainLayout.addWidget(self.foldersScrollArea)
        
        
        #self.setMaximumWidth(500)
        self.setGeometry(600, 500, 600, 400)
        self.setWindowTitle('RAW to hdf5') 
    

    def openFile(self):
        filename=QtWidgets.QFileDialog.getOpenFileNames(self,'Open RAW files',directory=self.last_dir_opened,
                                                        filter="Confocor RAW files (*.raw)")
        if filename[0]:
            self.loadFiles(filename[0])
        self.last_dir_opened=QtWidgets.QFileDialog().directory().absolutePath()
        self.settings.setValue("last_folder", QtWidgets.QFileDialog().directory().absolutePath())
            
    def loadFiles(self, filelist):
        ids={}
        for name in filelist:
            t=ConfoCor3Raw(name)
            if not (t.measurement_identifier in ids):
                ids[t.measurement_identifier]={t.channel:name}
            else:
                ids[t.measurement_identifier] [t.channel]=name
        
        for ex_id, data in ids.items(): 
            if (len(data)==2) and not (data[0] in self.ch0_name_list):
                menuitem=fileMenuItem(data[0],data[1],fileMenu=self,mainwindow=self)
                self.laneWidgetList.append(menuitem)
                self.ch0_name_list.append(data[0])
                self.sort_by_time.append(creation_date(data[0],formated=False))
                self.dataFrame.append([len(self.ch0_name_list),creation_date(data[0],formated=False),os.path.basename(data[0]),menuitem])
        #sorting by date
        print(self.dataFrame)
        [self.folderLayout.addWidget(x) for _,x in sorted(zip(self.sort_by_time,self.laneWidgetList))[::-1]]
                 
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
                if '.raw' in str(url.toLocalFile()):
                    links.append(str(url.toLocalFile()))
            if links:
                self.loadFiles(links)
        else:
            event.ignore()    
    def closeEvent(self, event):
        for widget in self.laneWidgetList:
            try:
                widget.eW.close()
            except:
                pass
            
 

class header(QtWidgets.QWidget):
    def __init__(self):
        super(header, self).__init__()
        self.Layout = QtWidgets.QGridLayout(self)
        self.Layout.setSpacing(0)
        self.Layout.setContentsMargins(0,0,0,0)
        self.Layout.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        timestamp=QtWidgets.QLabel('Date Time')   
        timestamp.setFixedWidth(100)
          
        size=QtWidgets.QLabel('Size')  
        size.setFixedWidth(100)   
                     
        r_button = QtWidgets.QLabel('Name')  
        r_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        
        self.Layout.addWidget(timestamp,0,0)
        self.Layout.addWidget(size,0,1)
        self.Layout.addWidget(r_button,0,2)
        
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
        timestamp.setFixedWidth(100)
        timestamp.setStyleSheet("border: 1px solid grey")
          
        size=QtWidgets.QLabel('%s\n%s'%(GetHumanReadable(QtCore.QFileInfo(self.ch0_filename).size()),
                                        GetHumanReadable(QtCore.QFileInfo(self.ch1_filename).size())))
        size.setStyleSheet("border: 1px solid grey")
        size.setFixedWidth(100)                
        self.r_button = QtWidgets.QPushButton('ch1: %s \nch2: %s'%(os.path.basename(self.ch0_filename), os.path.basename(self.ch1_filename)))
        self.r_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        #self.r_button.setFixedWidth(50)
        self.r_button.setStyleSheet("text-align: left;padding: 3px;background-color: red")    
        self.r_button.clicked.connect(self.runTask)
               
        
        self.Layout.addWidget(timestamp,0,0)
        self.Layout.addWidget(size,0,1)
        self.Layout.addWidget(self.r_button,0,2)
    def markSaved(self):
        self.r_button.setStyleSheet("text-align: left;padding: 3px;background-color: green")
    def runTask(self):   
        self.eW=exportWidget(self.ch0_filename,self.ch1_filename,self.mainwindow.settings)   
        self.eW.saved.connect(self.markSaved)  
        self.eW.show()
        
class exportWidget(QtWidgets.QWidget):
    saved = QtCore.pyqtSignal()
    '''
    Provides Widget for opening multiple files
    '''
    def __init__(self,ch0_filename,ch1_filename,settings,parent=None):
        self.settings=settings

        super(exportWidget, self).__init__(parent)
        self.Layout = QtWidgets.QGridLayout(self)
        #self.Layout.setSpacing(0)
        #self.Layout.setContentsMargins(0,0,0,0)
        self.filenames=[ch0_filename,ch1_filename]
        self.setWindowTitle('ch1: %s \nch2: %s'%(os.path.basename(ch0_filename), os.path.basename(ch1_filename))) 
        #self.Layout.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        
        label=QtWidgets.QLabel('Sample name*:')
        label.setWordWrap(True)
        #label.setFixedWidth(80)
        self.Layout.addWidget(label,0,0)
        self.sampleNameWidget=autoCompBox(self.settings,'sampleNames')
        self.sampleNameWidget.setEditable(True)
        self.sampleNameWidget.setToolTip('Insert sample name here \n e.g. Human nucleosome + FACT')
        self.Layout.addWidget(self.sampleNameWidget,0,1)
        
        label=QtWidgets.QLabel('Buffer name*:')
        label.setWordWrap(True)
        self.Layout.addWidget(label,1,0)
        self.bufferNameWidget=autoCompBox(self.settings,'bufferNames')
        self.bufferNameWidget.setEditable(True)
        self.bufferNameWidget.setToolTip('Insert buffer name here \n e.g. TE 150mM')
        self.Layout.addWidget(self.bufferNameWidget,1,1)
        
        label=QtWidgets.QLabel('Author*:')
        label.setWordWrap(True)
        self.Layout.addWidget(label,2,0)
        self.authorWidget=autoCompBox(self.settings,'authorNames')
        self.authorWidget.setEditable(True)
        self.authorWidget.setToolTip('Insert your name here')
        self.Layout.addWidget(self.authorWidget,2,1)
        
        label=QtWidgets.QLabel('Donor name:')
        label.setWordWrap(True)
        self.Layout.addWidget(label,3,0)
        self.donorNameWidget=autoCompBox(self.settings,'donorNames')
        self.donorNameWidget.setEditable(True)
        self.Layout.addWidget(self.donorNameWidget,3,1)
        
        label=QtWidgets.QLabel('Acceptor name:')
        label.setWordWrap(True)
        self.Layout.addWidget(label,4,0)
        self.acceptorNameWidget=autoCompBox(self.settings,'acceptorNames')
        self.acceptorNameWidget.setEditable(True)
        self.Layout.addWidget(self.acceptorNameWidget,4,1)
        
        label=QtWidgets.QLabel('Press right mouse btn. to remove item from list')
        label.setWordWrap(True)
        self.Layout.addWidget(label,0,2,1,2)
        #self.descriptionWidget=autoCompBox(self.settings,'sampleNames')
        #self.descriptionWidget.setEditable(True)
        #self.descriptionWidget.setText( os.path.basename(ch0_filename)[:-4])
        #self.descriptionWidget.setToolTip('This field should UNIQUELY \n describe the experiment')
        #self.Layout.addWidget(self.descriptionWidget,0,3)
        
        label=QtWidgets.QLabel('Affiliation:')
        label.setWordWrap(True)
        self.Layout.addWidget(label,1,2)
        self.affiliationWidget=autoCompBox(self.settings,'affiliationNames')
        self.affiliationWidget.setEditable(True)
        self.Layout.addWidget(self.affiliationWidget,1,3)
        
        label=QtWidgets.QLabel('Excitation w.l.:')
        label.setWordWrap(True)
        self.Layout.addWidget(label,2,2)
        self.excitationWLWidget=QtWidgets.QSpinBox()
        self.excitationWLWidget.setMinimum(400)
        self.excitationWLWidget.setMaximum(800)
        self.excitationWLWidget.setValue(514)
        self.excitationWLWidget.setSingleStep(1)
        self.Layout.addWidget(self.excitationWLWidget,2,3)
        
        label=QtWidgets.QLabel('Donor w.l.:')
        label.setWordWrap(True)
        self.Layout.addWidget(label,3,2)
        self.donorWLWidget=QtWidgets.QSpinBox()
        self.donorWLWidget.setMinimum(400)
        self.donorWLWidget.setMaximum(800)
        self.donorWLWidget.setSingleStep(1)
        self.donorWLWidget.setValue(580)
        self.Layout.addWidget(self.donorWLWidget,3,3)
        
        label=QtWidgets.QLabel('Acceptor w.l.:')
        label.setWordWrap(True)
        self.Layout.addWidget(label,4,2)
        self.acceptorWLWidget=QtWidgets.QSpinBox()
        self.acceptorWLWidget.setMinimum(400)
        self.acceptorWLWidget.setMaximum(800)
        self.acceptorWLWidget.setValue(650)
        self.acceptorWLWidget.setSingleStep(1)
        self.Layout.addWidget(self.acceptorWLWidget,4,3)
        
        
        self.r_button = QtWidgets.QPushButton('Save h5 file')
        self.r_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.r_button.setStyleSheet("text-align: left;padding: 3px")    
        self.r_button.setFixedWidth(100)
        self.r_button.setFixedHeight(30)
        
        label=QtWidgets.QLabel('All fields marked with asterisk (*) must be filled in')
        label.setWordWrap(True)
        self.Layout.addWidget(label,5,1,1,2)
        
        
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
            description = self.sampleNameWidget.currentText().encode('ascii')
           

            author = self.authorWidget.currentText().encode('ascii')
            author_affiliation = self.affiliationWidget.currentText().encode('ascii')

            sample_name = self.sampleNameWidget.currentText().encode('ascii')
            buffer_name = self.bufferNameWidget.currentText().encode('ascii')
            dye_names = '%s, %s'%(self.donorNameWidget.currentText().encode('ascii'),self.acceptorNameWidget.currentText().encode('ascii'))   # Comma separates names of fluorophores
        except:
            error_dialog = QtWidgets.QErrorMessage(self)
            error_dialog.setWindowModality(QtCore.Qt.WindowModal)
            error_dialog.showMessage('Only ASCII symbols allowed (only English)')
            return
        
        if not author or not sample_name or not buffer_name:
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
        
        sample = dict(
            sample_name = sample_name,
            buffer_name = buffer_name,
            dye_names = dye_names)
        try:
            provenance = dict(
                filename=self.filenames[0].encode('ascii'),
                creation_time = creation_date(self.filenames[0]).encode('ascii'))
        except:
            provenance={}

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
            identity=identity,
            sample=sample,
            provenance=provenance
        )
        try:
            last_dir_saved = self.settings.value("last_save_folder", ".")
        except:
            last_dir_saved = QtCore.QDir.currentPath()
        fname=os.path.join(last_dir_saved,"%s.h5"%self.sampleNameWidget.currentText())
        print(fname)
        
        filename=QtWidgets.QFileDialog.getSaveFileName(self,'Save smFRET data file',directory=fname,filter="hdf5 files (*.h5)")        
        
        if filename[0]:
            phc.hdf5.save_photon_hdf5(data, h5_fname=str(filename[0]), overwrite=True)
            self.settings.setValue("last_save_folder", os.path.dirname(filename[0]))
            self.saved.emit()
            self.close()
        
        
        
def main():
    
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName("Biological Faculty")
    app.setOrganizationDomain("bioeng.org")
    app.setApplicationName("Raw2HDF")
    ex = FileMenu()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()    

