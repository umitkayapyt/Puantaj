# encoding:utf-8
# Raporlama seçim ekranı 
# Geliştirilebilir

from PyQt5.QtWidgets import QMainWindow
from _displayForm import Ui_DisplayWindow
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt


class Display(QMainWindow):
    signal = pyqtSignal(list)
    def __init__(self):
        super(Display, self).__init__()

        #QMainWindow.__init__(self, None, Qt.WindowStaysOnTopHint)

        self.ui = Ui_DisplayWindow()
        self.ui.setupUi(self)

        Params = ['-Yok-','T.C.', 'Unvan','SGK Firma','SGK Şube','Şehir','Lokasyon','Departman','Dönem']
        self.ui.comboDisParam1.addItems(Params)
        self.ui.comboDisParam2.addItems(Params)
        self.ui.comboDisParam3.addItems(Params)

        self.ui.btnDisplay.clicked.connect(self.EmitFonk)

    def EmitFonk(self): #seçilen parametrelerin gönderilmesi

        param1= self.ui.comboDisParam1.currentText()
        param2= self.ui.comboDisParam2.currentText()
        param3= self.ui.comboDisParam3.currentText()

        ParamList = [param1, param2, param3]
        self.signal.emit(ParamList)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super(Display, self).keyPressEvent(event)