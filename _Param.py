# encoding:utf-8
# Puantajlardaki standart parametreler signal yöntemiyle değiştirilebilir.

from PyQt5.QtWidgets import QMainWindow, QMessageBox
from _ParamForm import Ui_ParamWindow
from PyQt5.QtCore import Qt
from _puantaj import Puantaj
from _load import LoadWindow
import re

class Param(QMainWindow):

    def __init__(self):
        super(Param, self).__init__()

        self.ui = Ui_ParamWindow()
        self.ui.setupUi(self)

        self.objCalisma = 'X'
        self.objCalismaDisi = '-'
        self.objHaftaTatili = 'T'
        self.objResmiTatil = 'RS'
        self.objIseGirmedi = 'İŞE GİRMEDİ'
        self.objCikmis = 'ÇIKMIŞ'
        self.ui.txtCalismaGunu.insert(self.objCalisma)
        self.ui.txtCalismaDisi.insert(self.objCalismaDisi)
        self.ui.txtHaftaTatili.insert(self.objHaftaTatili)
        self.ui.txtResmiTatil.insert(self.objResmiTatil)
        self.ui.txtIseGirmedi.insert(self.objIseGirmedi)
        self.ui.txtCikmis.insert(self.objCikmis)

        self.CalismaGunu = self.ui.txtCalismaGunu.text()
        self.CalismaDisi = self.ui.txtCalismaDisi.text()
        self.HaftaTatili = self.ui.txtHaftaTatili.text()
        self.ResmiTatil = self.ui.txtResmiTatil.text()
        self.IseGirmedi = self.ui.txtIseGirmedi.text()
        self.Cikmis = self.ui.txtCikmis.text()

        self.ui.btnDegistir.clicked.connect(self.ParamGonder)
    
    
    def ParamGonder(self):
        self.CalismaGunu = self.ui.txtCalismaGunu.text().strip().replace("i", "İ").upper()
        self.CalismaDisi = self.ui.txtCalismaDisi.text().strip().replace("i", "İ").upper()
        self.HaftaTatili = self.ui.txtHaftaTatili.text().strip().replace("i", "İ").upper()
        self.ResmiTatil = self.ui.txtResmiTatil.text().strip().replace("i", "İ").upper()
        self.IseGirmedi = self.ui.txtIseGirmedi.text().strip().replace("i", "İ").upper()
        self.Cikmis = self.ui.txtCikmis.text().strip().replace("i", "İ").upper()

        LoadParam = [self.CalismaGunu, self.CalismaDisi, self.HaftaTatili, self.ResmiTatil, self.IseGirmedi, self.Cikmis]
        for i in LoadParam:
            if not re.match('^\s', i) and i !="":
                pass
            else:
                QMessageBox.warning(self,'GEÇERSİZ VERİ','Geçerli Veriler Giriniz...!')
                self.Temizle()
                self.Param()
                return 
            
        self.Temizle()
        self.ui.txtCalismaGunu.insert(self.CalismaGunu)
        self.ui.txtCalismaDisi.insert(self.CalismaDisi)
        self.ui.txtHaftaTatili.insert(self.HaftaTatili)
        self.ui.txtResmiTatil.insert(self.ResmiTatil)
        self.ui.txtIseGirmedi.insert(self.IseGirmedi)
        self.ui.txtCikmis.insert(self.Cikmis)

        Puantaj.objCalisma = self.CalismaGunu
        Puantaj.objCalismaDisi = self.CalismaDisi
        Puantaj.objHaftaTatili = self.HaftaTatili
        Puantaj.objResmiTatil = self.ResmiTatil
        Puantaj.objIseGirmedi = self.IseGirmedi
        Puantaj.objCikmis = self.Cikmis

        LoadWindow.objCalisma = self.CalismaGunu
        LoadWindow.objCalismaDisi = self.CalismaDisi
        LoadWindow.objHaftaTatili = self.HaftaTatili
        LoadWindow.objResmiTatil = self.ResmiTatil
        LoadWindow.objIseGirmedi = self.IseGirmedi
        LoadWindow.objCikmis = self.Cikmis

        QMessageBox.warning(self,'PARAMETRELER','Parametreler Güncellendi...!')

        self.close()

    def Param(self):
        self.ui.txtCalismaGunu.insert(self.objCalisma)
        self.ui.txtCalismaDisi.insert(self.objCalismaDisi)
        self.ui.txtHaftaTatili.insert(self.objHaftaTatili)
        self.ui.txtResmiTatil.insert(self.objResmiTatil)
        self.ui.txtIseGirmedi.insert(self.objIseGirmedi)
        self.ui.txtCikmis.insert(self.objCikmis)
    
    def Temizle(self):
        self.ui.txtCalismaGunu.clear()
        self.ui.txtCalismaDisi.clear()
        self.ui.txtHaftaTatili.clear()
        self.ui.txtResmiTatil.clear()
        self.ui.txtIseGirmedi.clear()
        self.ui.txtCikmis.clear()
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super(Param, self).keyPressEvent(event)
    


