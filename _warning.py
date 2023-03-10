# encoding:utf-8
# burası deneme amaçlı olduğu için kullanışlı değil
# 20. satırdaki 'dont-panic.gif' aldı dosya uygulama.exe ile aynı yerde bulunmalıdır.
# şimdilik 'table' Action seklmelerinde kullanılıyor
# Geliştirilebilir

from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMovie

class AcilisEkrani(QWidget):
    def __init__(self):
        super().__init__()
        QMainWindow.__init__(self, None, Qt.WindowStaysOnTopHint)
        self.setFixedSize(470,350)
        
        # self.setWindowFlags()

        self.animasyon = QLabel(self)
        self.movie = QMovie('dont-panic.gif') # buradaki dosya .exe dosyası ile aynı klasörde olmalıdır.
        self.animasyon.setMovie(self.movie)
        timer = QTimer(self)
        self.baslat()
        timer.singleShot(1500, self.bitir)

        self.show()
    
    def baslat(self):
        self.movie.start()

    def bitir(self):
        self.movie.stop()
        self.close()

