# encoding:utf-8
# tablo ön izleme
# Veriler pandas formatında ve signal yöntemiyle geldiği için işlemler uzun sürüyor. 
# Gelen verilerin numpy array olarak değiştirilmesi gerekir.

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from _previewForm import Ui_PreviewWindow


class Preview(QMainWindow):
    signal = pyqtSignal(list)
    def __init__(self):
        super(Preview, self).__init__()

        self.ui = Ui_PreviewWindow()
        self.ui.setupUi(self)

        # #table kolonlar ve indexler
        # self.ColumnName = ['Pers. Kod','Ad','Soyad','T.C.', 'Unvan','İşe Başlama T.','İşten Ayrılış T.',
        # 'SGK Firma','SGK Şube','Şehir','Lokasyon','Departman','Dönem','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
        # self.ColumnWidth = [100,200,200,125,150,120,120,150,150,150,150,150,135,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
        # stylesheet = "::section{Background-color:rgb(c);border-radius:16px;font: 75 10pt "'MS Shell Dlg 2'";}"
        # self.ui.tableProductsPreview.horizontalHeader().setStyleSheet(stylesheet)
        # self.ui.tableProductsPreview.setColumnCount(len(self.ColumnName))
        # self.ui.tableProductsPreview.setHorizontalHeaderLabels(self.ColumnName)
        # for index, width in enumerate(self.ColumnWidth):
        #     self.ui.tableProductsPreview.setColumnWidth(index,width)
    
   
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super(Preview, self).keyPressEvent(event)