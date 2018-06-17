from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import  Qt, QEvent


class autoCompBox(QComboBox):
    def __init__(self,settings,key):
        QComboBox.__init__(self)
        self.settings=settings
        self.key=key
        try:
            self.settingsList = self.settings.value(key, [], str)
            for item in self.settingsList:
                if item != '':
                    self.addItem(item)
        except:
            pass
        self.v=self.view()
        self.v.pressed.connect(self.remove)
        self.currentIndexChanged.connect(self.rearrange)
        
    def remove(self, view):
        if QApplication.mouseButtons()==Qt.RightButton:
            self.removeItem(view.row())
            itemlist=[self.itemText(i) for i in range(self.count())]
            self.settings.setValue(self.key, itemlist)
            
    def rearrange(self,index):
        if self.count()!=0:
            itemlist=[self.itemText(i) for i in range(self.count())]
            itemlist.insert(0,itemlist.pop(index))
            self.settings.setValue(self.key, itemlist)

    def event(self, event):
        if (event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return) or (event.type() == 9):
            if not self.currentText().upper() in [self.itemText(i).upper() for i in range(self.count())]:
                self.addItem(self.currentText())
                itemlist=[self.itemText(i) for i in range(self.count())][-20:]
                self.settings.setValue(self.key, itemlist)

        return QComboBox.event(self, event)
