# encoding:utf-8
# Kullanıcı giriş sayfası
# Çeşitli database sistemlerindeki çeşitli kullanıcı girişleri ve geçişleri buradan yapılabilir

from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtCore import  Qt
from _UsersForm import Ui_UsersWindow
from _table import Window
from PyQt5.QtGui import QPixmap
import re
import sys


class Users(QMainWindow):
    def __init__(self):
        super(Users, self).__init__()

        QMainWindow.__init__(self, None, Qt.WindowStaysOnTopHint)
        self.ui = Ui_UsersWindow()
        self.ui.setupUi(self)

        self.ui.txtSifre.setText('Plus_Satin_Al')

        self.w = Window()

        #database bağlantı
        self.KullanaiciAdi = ''
        self.Sifre = ''
        self.w.DBConnect() 
        
        #signals & slots
        self.ui.btnLogin.clicked.connect(self.Login)
        self.w.signal[list].connect(self.showw)
    
    def Login(self):
        KullanaiciAdi = self.ui.txtKullaniciAdi.text()
        Sifre = self.ui.txtSifre.text()
        if not re.match('^\s', KullanaiciAdi) and KullanaiciAdi !="":
            pass

        else:
            icon = ':/resim/kaynakjpg/Actions-view-media-artist-icon.png'
            baslik1 = 'KULLANICI BİLGİLERİ'
            metin1 = 'Kullanıcı Adınızı Giriniz...!'
            ok = 'Tamam'
            self.MesajBoxWarning(baslik1, metin1, ok, icon)
            return

        self.w.ui.txtKullanici.setText(KullanaiciAdi)
        self.w.ui.centralwidget.setEnabled(True)
        self.w.ui.actionCSV_Aktar.setEnabled(True)
        self.w.ui.actionToplu_Y_kleme.setEnabled(True)
        self.w.ui.actionYenile.setEnabled(True)
        self.w.ui.actionExcel.setEnabled(True)
        self.w.ui.actionPDF_Aktar.setEnabled(True)
        self.w.ui.actionCSV_Aktar.setEnabled(True)
        self.w.ui.actionDisplay.setEnabled(True)
        self.w.ui.actionSil.setEnabled(True)
        self.w.ui.actionKayitli_Personeller.setEnabled(True)
        self.w.ui.action_On_Izleme.setEnabled(True)
        self.w.showMaximized()
        self.close()

    def MesajBoxWarning(self, baslik, metin, ok, icon):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        mesajMetin  = '<pre style="font-size:12pt; color: #01040a;">{}<figure>'.format(metin)
        msg.setWindowTitle(baslik)

        pixmap = QPixmap(icon)
        msg.setIconPixmap(pixmap)
        
        msg.setText(mesajMetin)
        msg.setStandardButtons(QMessageBox.Ok)
        buttonOk = msg.button(QMessageBox.Ok)
        buttonOk.setText(ok)
        msg.exec_()

    def showw(self):
        self.show()


def app():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = Users()
    win.show()
    sys.exit(app.exec())


app()


# pyinstaller --onefile -w -i .\dpanic5.ico .\_users.py --hidden-import openpyxl.cell._writer
