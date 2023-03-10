# encoding:utf-8
# main dosyası
# Tablo burada oluşturuluyor. Diğer pencerelerdeki etkileşimli işlemler burada sonuçlanır.

import os
from pathlib import Path
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QMenu, QMainWindow, QListWidgetItem
from PyQt5.QtCore import QEvent, QRegExp, Qt, QDate, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QRegExpValidator, QPixmap
from _tableForm import Ui_MainWindow
from _load import LoadWindow
from _puantaj import Puantaj
from _Param import Param
from _display import Display
from _preview import Preview
from _calendar import Takvim
from _warning import AcilisEkrani
from _DBpersonel import KayitliPersonel
from contextlib import closing
from pandas import offsets, date_range, to_datetime, DataFrame, unique, ExcelWriter, DateOffset, Timestamp
from datetime import datetime as dt
from dateutil import relativedelta
import numpy as np
import re
import sqlite3
import locale
from pandas.tseries.holiday import *

locale.setlocale(locale.LC_ALL,'Turkish_Turkey.1254')
locale.setlocale(locale.LC_TIME, "tr")

class Window(QMainWindow):
    signal = pyqtSignal(list)

    def __init__(self):
        super(Window, self).__init__()
       
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.DBConnect() #database bağlantı
        
        #diğer tabloların içe aktarılması
        self.GenelTatil = Takvim()
        self.load = LoadWindow()
        self.param = Param()
        self.display = Display()
        self.preview = Preview()
        self.kayitliPersoneller = KayitliPersonel()

        self.StatusTime = 4000

        #table kolonlar ve indexler
        self.ColumnName = ['Pers. Kod','Ad','Soyad','T.C.', 'Unvan','İşe Başlama T.','İşten Ayrılış T.',
        'SGK Firma','SGK Şube','Şehir','Lokasyon','Departman','Dönem','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
        self.ColumnWidth = [100,200,200,125,150,120,120,150,150,150,150,150,135,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
        stylesheet = "::section{Background-color:rgb(c);border-radius:16px;font: 75 10pt "'MS Shell Dlg 2'";}"
        self.ui.tableProducts.horizontalHeader().setStyleSheet(stylesheet)
        self.ui.tableProducts.setColumnCount(len(self.ColumnName))
        self.ui.tableProducts.setHorizontalHeaderLabels(self.ColumnName)
        for index, width in enumerate(self.ColumnWidth):
            self.ui.tableProducts.setColumnWidth(index,width)

        #Combobox işlemler / current ve datalar
        self.Aylar =Takvim.Aylar()
        self.Gunler = Takvim.Gunler()
        self.yillar = Takvim.Yillar()
        self.ui.comboAy.addItems(self.Aylar)
        self.ui.comboYil.addItems(self.yillar)
        self.ui.comboYil.setCurrentIndex(23)
        self.ui.comboTatilGunu_1.addItems(self.Gunler)
        self.ui.comboTatilGunu_2.addItems(self.Gunler)
        self.ui.comboTatilGunu_1.setCurrentIndex(0)
        self.ui.comboTatilGunu_2.setCurrentIndex(1)

        #Tc karakter standartlar
        val=QRegExpValidator(QRegExp(r'[0-9]+')) 
        self.ui.txtTC.setValidator(val)

        #tarih karakter standartlar
        self.vals=QRegExpValidator(QRegExp("(^(((0[1-9]|1[0-9]|2[0-8])[\/](0[1-9]|1[012]))|((29|30|31)[\/](0[13578]|1[02]))|((29|30)[\/](0[4,6,9]|11)))[\/](19|[2-9][0-9])\d\d$)|(^29[\/]02[\/](19|[2-9][0-9])(00|04|08|12|16|20|24|28|32|36|40|44|48|52|56|60|64|68|72|76|80|84|88|92|96)$)"))
        self.ui.dateIStenAyrilis.setValidator(self.vals) 

############################################################## Signals & Slots #####################################################################
        
        self.ui.listItems.installEventFilter(self)
        self.ui.txtTC.installEventFilter(self)

        # self.ui.txtTC.editingFinished.connect(self.KalanIzin)

        # self.ui.txtTC.editingFinished.connect(self.BilgiGetir)
        # self.ui.txtIzinTuru.editingFinished.connect(self.KalanIzin)
        self.ui.btnSave.clicked.connect(self.Datagonder)
        self.ui.btnAdd.clicked.connect(self.Datagonder)
        self.ui.btnPersonelEkle.clicked.connect(self.DataBasePersonelEkle)
        self.ui.btnSatirEkle.clicked.connect(self.usteSatirEkle)
        self.ui.btnAltaSatirEkle.clicked.connect(self.AltaSatirEkle)
        self.ui.btnUsttekiSatiriKopyala.clicked.connect(self.UsttekiSatiriKopyala)
        self.ui.btnSatirSil.clicked.connect(self.SatirSil)
        self.ui.btnSatirKopyala.clicked.connect(self.SeciliSatiriEnAltaKopyala)
        self.ui.btnAltaSatirKopyala.clicked.connect(self.AlttakiSatiriKopyalaEkle)
        self.ui.btnKolonEkle.clicked.connect(self.KolonEkle)
        self.ui.btnKolonSil.clicked.connect(self.KolonSil)
        self.ui.dateIStenAyrilis.editingFinished.connect(self.IstenAyrilisSignals)
        self.ui.btnClear.clicked.connect(self.Temizle)
        self.preview.ui.btn_ExcelAktir.clicked.connect(self.ExcelAktar)
        self.ui.actionToplu_Y_kleme.triggered.connect(self.OpenLoadPage)
        self.ui.actionKayitli_Personeller.triggered.connect(self.OpenKayitliPersonel)
        self.ui.actionDisplay.triggered.connect(self.OpenDisplayPage)
        self.ui.actionExcel.triggered.connect(self.ExcelAktar)
        self.ui.actionPDF_Aktar.triggered.connect(self.PDFAktar)
        self.ui.actionCSV_Aktar.triggered.connect(self.CSVAktar)
        self.ui.actionYenile.triggered.connect(self.TabloyuYenile)
        self.ui.action_On_Izleme.triggered.connect(self.OpenPreview)
        self.ui.actionSil.triggered.connect(self.TabloSil)
        self.ui.actionKullaniciDegistir.triggered.connect(self.OpenKullaniciDegistir)
        self.load.signal[list].connect(self.ConvertList_DictAndLoadTable)
        self.display.signal[list].connect(self.disPlayStats)
        self.kayitliPersoneller.signal[list].connect(self.DataBaseAlinanKayitlar)
        self.ui.actionParametreler.triggered.connect(self.OpenParam)
        self.ui.comboAy.currentIndexChanged['QString'].connect(self.BilgilerEkrani)
        self.ui.comboYil.currentIndexChanged['QString'].connect(self.BilgilerEkrani)
        self.ui.comboTatilGunu_1.currentIndexChanged['QString'].connect(self.KalanIzin)
        self.ui.comboTatilGunu_2.currentIndexChanged['QString'].connect(self.KalanIzin)

############################################################# Toblo Edit İşlemleri ###############################################################
     
    def usteSatirEkle (self):
        rowCount = self.ui.tableProducts.rowCount()
        if rowCount > 0:
            seciliSatir = self.ui.tableProducts.currentRow()
            self.ui.tableProducts.insertRow(seciliSatir)

    def AltaSatirEkle (self):
        rowCount = self.ui.tableProducts.rowCount()
        if rowCount > 0:
            seciliSatir = self.ui.tableProducts.currentRow()+1
            self.ui.tableProducts.insertRow(seciliSatir)

    def SatirSil (self):
        rowCount = self.ui.tableProducts.rowCount()
        if rowCount > 0:
            baslik = 'Siliniyor..'
            metin = 'Silmek İstediğine Emin misin?'
            evet = 'Evet'
            hayir = 'Hayır'
            result = self.MesajBoxSoru(baslik, metin, evet, hayir)
            if result == evet:
                seciliSatir = self.ui.tableProducts.currentRow()
                self.ui.tableProducts.removeRow(seciliSatir)
            
    def SeciliSatiriEnAltaKopyala(self):
        rowCount = self.ui.tableProducts.rowCount()
        if rowCount > 0:
            current = self.ui.tableProducts.currentRow()
            rowCount = self.ui.tableProducts.rowCount()
            self.ui.tableProducts.insertRow(rowCount)
            columnCount = self.ui.tableProducts.columnCount()
            
            for i in range(columnCount):
                if not self.ui.tableProducts.item(current, i) is None:
                    self.ui.tableProducts.setItem(rowCount, i, QTableWidgetItem(self.ui.tableProducts.item(current, i).text()))
    
    def UsttekiSatiriKopyala(self):
        rowCount = self.ui.tableProducts.rowCount()
        if rowCount > 0:
            current = self.ui.tableProducts.currentRow()
            self.ui.tableProducts.insertRow(current)
            # rowCount = self.ui.tableProducts.rowCount()
            columnCount = self.ui.tableProducts.columnCount()
                    
            for i in range(columnCount):
                if not self.ui.tableProducts.item(current-1, i) is None:
                    self.ui.tableProducts.setItem(current, i, QTableWidgetItem(self.ui.tableProducts.item(current-1, i).text()))
                    
    def AlttakiSatiriKopyalaEkle(self):
        rowCount = self.ui.tableProducts.rowCount()
        if rowCount > 0:
            self.ui.tableProducts.insertRow(self.ui.tableProducts.rowCount())
            rowCount = self.ui.tableProducts.rowCount()
            columnCount = self.ui.tableProducts.columnCount()
                    
            for i in range(columnCount):
                if not self.ui.tableProducts.item(rowCount-2, i) is None:
                    self.ui.tableProducts.setItem(rowCount-1, i, QTableWidgetItem(self.ui.tableProducts.item(rowCount-2, i).text()))

    def KolonEkle(self):
        rowCount = self.ui.tableProducts.rowCount()
        seciliKolon = self.ui.tableProducts.currentColumn()
        if (rowCount > 0) and (seciliKolon > 0):
            baslik = 'Kolon Ekle..'
            metin = 'Eklemek İstediğine Emin misin?\nTekrar Kayıt Yaptığında Sütunlar Kaymış Olacak '
            evet = 'Evet'
            hayir = 'Hayır'
            result = self.MesajBoxSoru(baslik, metin, evet, hayir)
            if result == evet:
                self.ui.tableProducts.insertColumn(seciliKolon)
                baslik1 = 'Dikkat..!'
                metin1 = 'Artık Yeni Kayıt Yapma..!'
                ok = 'Anladık...'
                icon = 'kaynakjpg/Jeltz-icon.png'
                self.MesajBoxWarning(baslik1, metin1, ok, icon)
                self.ui.btnAdd.setEnabled(False)
                self.ui.actionToplu_Y_kleme.setEnabled(False)
                self.ui.actionYenile.setEnabled(False)
                self.ui.actionExcel.setEnabled(False)
                self.ui.actionPDF_Aktar.setEnabled(False)
                self.ui.actionCSV_Aktar.setEnabled(False)
                self.ui.actionDisplay.setEnabled(False)

    def KolonSil(self):
        rowCount = self.ui.tableProducts.rowCount()
        seciliKolon = self.ui.tableProducts.currentColumn()
        if (rowCount > 0) and (seciliKolon > 0):
            baslik = 'Siliniyor..'
            metin = 'Silmek İstediğine Emin misin?\nTekrar Kayıt Yaptığında Sütunlar Kaymış Olacak '
            evet = 'Evet'
            hayir = 'Hayır'
            result = self.MesajBoxSoru(baslik, metin, evet, hayir)
            if result == evet:
                seciliKolon = self.ui.tableProducts.currentColumn()
                self.ui.tableProducts.removeColumn(seciliKolon)
                baslik1 = 'Dikkat..!'
                metin1 = 'Artık Yeni Kayıt Yapma..!'
                ok = 'Anladık...'
                icon = 'kaynakjpg/Jeltz-icon.png'
                self.MesajBoxWarning(baslik1, metin1, ok, icon)
                self.ui.btnAdd.setEnabled(False)
                self.ui.actionToplu_Y_kleme.setEnabled(False)
                self.ui.actionYenile.setEnabled(False)
                self.ui.actionExcel.setEnabled(False)
                self.ui.actionPDF_Aktar.setEnabled(False)
                self.ui.actionCSV_Aktar.setEnabled(False)
                self.ui.actionDisplay.setEnabled(False)
        
    def TablodakiVeriler(self):
        basliklar = []
        
        for i in range(self.ui.tableProducts.model().columnCount()):
            basliklar.append(self.ui.tableProducts.horizontalHeaderItem(i).text())
        
        df = DataFrame(columns=basliklar)

        for j in range(self.ui.tableProducts.rowCount()):
            for clm in range(self.ui.tableProducts.columnCount()):
                obj = self.ui.tableProducts.item(j,clm)
                if obj is not None and obj.text() != '':
                    df.at[j, basliklar[clm]] = self.ui.tableProducts.item(j, clm).text()
        return df

    def ConvertList_DictAndLoadTable(self, df): # dosyadan gelen veriler tabloya işlenmesi
        self.ui.tableProducts.setColumnCount(len(self.ColumnName))
        self.ui.tableProducts.setHorizontalHeaderLabels(self.ColumnName)
        for index, width in enumerate(self.ColumnWidth):
            self.ui.tableProducts.setColumnWidth(index,width)
        
        keys = self.ColumnName
       
        dct = []
        for key, values, i in zip(keys, df, range(len(keys))):
            if len(values)==44: #ay 31 çekiyorsa
                dct+=[{
                    keys[0]:values[0], keys[1]:values[1], keys[2]:values[2], keys[3]:values[3],
                    keys[4]:values[4], keys[5]:values[5], keys[6]:values[6], keys[7]:values[7],
                    keys[8]:values[8], keys[9]:values[9], keys[10]:values[10], keys[11]:values[11],
                    keys[12]:values[12], keys[13]:values[13], keys[14]:values[14], keys[15]:values[15],
                    keys[16]:values[16], keys[17]:values[17], keys[18]:values[18], keys[19]:values[19],
                    keys[20]:values[20], keys[21]:values[21], keys[22]:values[22], keys[23]:values[23],
                    keys[24]:values[24], keys[25]:values[25], keys[26]:values[26], keys[27]:values[27],
                    keys[28]:values[28], keys[29]:values[29], keys[30]:values[30], keys[31]:values[31],
                    keys[32]:values[32], keys[33]:values[33], keys[34]:values[34], keys[35]:values[35],
                    keys[36]:values[36], keys[37]:values[37], keys[38]:values[38], keys[39]:values[39],
                    keys[40]:values[40], keys[41]:values[41], keys[42]:values[42], keys[43]:values[43]            
            }]
                rowCount = self.ui.tableProducts.rowCount()
                self.ui.tableProducts.insertRow(rowCount)
                for y in dct:
                    for i, key in enumerate(keys):
                        self.ui.tableProducts.setItem(rowCount, i, QTableWidgetItem(y[key]))
                    

            if len(values)==43: #ay 30 çekiyorsa
                dct+=[{
                    keys[0]:values[0], keys[1]:values[1], keys[2]:values[2], keys[3]:values[3],
                    keys[4]:values[4], keys[5]:values[5], keys[6]:values[6], keys[7]:values[7],
                    keys[8]:values[8], keys[9]:values[9], keys[10]:values[10], keys[11]:values[11],
                    keys[12]:values[12], keys[13]:values[13], keys[14]:values[14], keys[15]:values[15],
                    keys[16]:values[16], keys[17]:values[17], keys[18]:values[18], keys[19]:values[19],
                    keys[20]:values[20], keys[21]:values[21], keys[22]:values[22], keys[23]:values[23],
                    keys[24]:values[24], keys[25]:values[25], keys[26]:values[26], keys[27]:values[27],
                    keys[28]:values[28], keys[29]:values[29], keys[30]:values[30], keys[31]:values[31],
                    keys[32]:values[32], keys[33]:values[33], keys[34]:values[34], keys[35]:values[35],
                    keys[36]:values[36], keys[37]:values[37], keys[38]:values[38], keys[39]:values[39],
                    keys[40]:values[40], keys[41]:values[41], keys[42]:values[42]            
            }]

                rowCount = self.ui.tableProducts.rowCount()
                self.ui.tableProducts.insertRow(rowCount)
                for y in dct:
                    for i, key in enumerate(keys[:-1]):
                        self.ui.tableProducts.setItem(rowCount, i, QTableWidgetItem(y[key]))
            
            if len(values)==42: #ay 29 çekiyorsa
                dct+=[{
                    keys[0]:values[0], keys[1]:values[1], keys[2]:values[2], keys[3]:values[3],
                    keys[4]:values[4], keys[5]:values[5], keys[6]:values[6], keys[7]:values[7],
                    keys[8]:values[8], keys[9]:values[9], keys[10]:values[10], keys[11]:values[11],
                    keys[12]:values[12], keys[13]:values[13], keys[14]:values[14], keys[15]:values[15],
                    keys[16]:values[16], keys[17]:values[17], keys[18]:values[18], keys[19]:values[19],
                    keys[20]:values[20], keys[21]:values[21], keys[22]:values[22], keys[23]:values[23],
                    keys[24]:values[24], keys[25]:values[25], keys[26]:values[26], keys[27]:values[27],
                    keys[28]:values[28], keys[29]:values[29], keys[30]:values[30], keys[31]:values[31],
                    keys[32]:values[32], keys[33]:values[33], keys[34]:values[34], keys[35]:values[35],
                    keys[36]:values[36], keys[37]:values[37], keys[38]:values[38], keys[39]:values[39],
                    keys[40]:values[40], keys[41]:values[41]            
            }]

                rowCount = self.ui.tableProducts.rowCount()
                self.ui.tableProducts.insertRow(rowCount)
                for y in dct:
                    for i, key in enumerate(keys[:-2]):
                        self.ui.tableProducts.setItem(rowCount, i, QTableWidgetItem(y[key]))

            if len(values)==41: #ay 28 çekiyorsa
                dct+=[{
                    keys[0]:values[0], keys[1]:values[1], keys[2]:values[2], keys[3]:values[3],
                    keys[4]:values[4], keys[5]:values[5], keys[6]:values[6], keys[7]:values[7],
                    keys[8]:values[8], keys[9]:values[9], keys[10]:values[10], keys[11]:values[11],
                    keys[12]:values[12], keys[13]:values[13], keys[14]:values[14], keys[15]:values[15],
                    keys[16]:values[16], keys[17]:values[17], keys[18]:values[18], keys[19]:values[19],
                    keys[20]:values[20], keys[21]:values[21], keys[22]:values[22], keys[23]:values[23],
                    keys[24]:values[24], keys[25]:values[25], keys[26]:values[26], keys[27]:values[27],
                    keys[28]:values[28], keys[29]:values[29], keys[30]:values[30], keys[31]:values[31],
                    keys[32]:values[32], keys[33]:values[33], keys[34]:values[34], keys[35]:values[35],
                    keys[36]:values[36], keys[37]:values[37], keys[38]:values[38], keys[39]:values[39],
                    keys[40]:values[40]            
            }]

                rowCount = self.ui.tableProducts.rowCount()
                self.ui.tableProducts.insertRow(rowCount)
                for y in dct:
                    for i, key in enumerate(keys[:-3]):
                        self.ui.tableProducts.setItem(rowCount, i, QTableWidgetItem(y[key]))
    
    def ExcelAktar(self):
        rowCount = self.ui.tableProducts.rowCount()
        if rowCount > 0:
            baslik = 'Excel Dosyası'
            metin = 'Tablodaki Veriler Excele aktarılsın mı?'
            evet = 'Evet'
            hayir = 'Hayır'
            result = self.MesajBoxSoru(baslik, metin, evet, hayir)
            if result == evet:
                df = self.TablodakiVeriler()
                path = os.path.join(os.path.expanduser("~"), "Desktop", "Puantaj.xlsx")
                df.to_excel(path, index=False)
                baslik = 'EXCEL DOSYASI'
                metin = 'Puantaj.xlsx Masaüstünde Oluşturuldu'
                ok = 'Ok.'
                icon = ":/resim/kaynakjpg/hitchhikeguidetogalaxy1_config.png"
                self.MesajBoxWarning(baslik, metin, ok, icon)
        
        else:
            self.acilis = AcilisEkrani()

    def PDFAktar(self):
        rowCount = self.ui.tableProducts.rowCount()
        if rowCount > 0:
            baslik = 'PDF Dosyası'
            metin = 'Tablodaki Veriler PDF aktarılsın mı?'
            evet = 'Evet'
            hayir = 'Hayır'
            result = self.MesajBoxSoru(baslik, metin, evet, hayir)
            if result == evet:
                df = self.TablodakiVeriler()
                pathHTML = os.path.join(os.path.expanduser("~"), "Desktop", "Puantaj.html")
                df.to_html(pathHTML) #burası PDF dosyasına çevrilmeli
        else:
            self.acilis = AcilisEkrani()
    
    def CSVAktar(self):
        rowCount = self.ui.tableProducts.rowCount()
        if rowCount > 0:
            baslik = 'CSV Dosyası'
            metin = 'Tablodaki Veriler Csv aktarılsın mı?'
            evet = 'Evet'
            hayir = 'Hayır'
            result = self.MesajBoxSoru(baslik, metin, evet, hayir)
            if result == evet:
                df = self.TablodakiVeriler()
                pathHTML = os.path.join(os.path.expanduser("~"), "Desktop", "Puantaj.csv")
                df.to_csv(pathHTML)
        else:
            self.acilis = AcilisEkrani()
    
    def TabloSil(self): 
        rowCount = self.ui.tableProducts.rowCount()
        if rowCount > 0 :
            baslik = 'TABLO SİLME İŞLEMİ!!'
            metin = 'Tablodaki Veriler Silinsin mi?'
            evet = 'Evet'
            hayir = 'Hayır'
            result = self.MesajBoxSoru(baslik, metin, evet, hayir)
            if result == evet:
                # for j in range(self.ui.tableProducts.rowCount()):
                #     seciliSatir = self.ui.tableProducts.currentRow()
                #     self.ui.tableProducts.removeRow(seciliSatir)
                while (self.ui.tableProducts.rowCount() > 0):
                    self.ui.tableProducts.removeRow(0)
                    
                    self.ui.btnAdd.setEnabled(True)
                    self.ui.actionToplu_Y_kleme.setEnabled(True)
                    self.ui.actionYenile.setEnabled(True)
                    self.ui.actionExcel.setEnabled(True)
                    self.ui.actionPDF_Aktar.setEnabled(True)
                    self.ui.actionCSV_Aktar.setEnabled(True)
                    self.ui.actionDisplay.setEnabled(True)
                    self.ui.tableProducts.setColumnCount(len(self.ColumnName))
                    self.ui.tableProducts.setHorizontalHeaderLabels(self.ColumnName)
                    for index, width in enumerate(self.ColumnWidth):
                        self.ui.tableProducts.setColumnWidth(index,width)
                    
        elif rowCount == 0:
            return             

    def TabloyuYenile(self):
        rowCount = self.ui.tableProducts.rowCount()
        if rowCount > 0 :
            self.load.close()
            self.display.close()
            self.param.close()
                
            df = self.TablodakiVeriler()
            self.load.ui.comboAyLoad.setCurrentIndex(self.ui.comboAy.currentIndex())
            self.load.ui.comboYilLoad.setCurrentIndex(self.ui.comboYil.currentIndex())
            self.load.ui.comboTatilGunu_1Load.setCurrentIndex(self.ui.comboTatilGunu_1.currentIndex())
            self.load.ui.comboTatilGunu_2Load.setCurrentIndex(self.ui.comboTatilGunu_2.currentIndex())
            df.drop(df.iloc[:,12:], inplace=True, axis=1) #dönemden sonrası atıldı
            while (self.ui.tableProducts.rowCount() > 0):
                    self.ui.tableProducts.removeRow(0)
            self.load.TabloyuYenile(df)
            donem = self.ui.comboYil.currentText()+"-"+self.ui.comboAy.currentText()
            baslik = 'Puantaj Yeniden Oluşturuldu'
            metin = "{} dönemine göre tekrar oluşturuldu.".format(donem)
            ok = 'Tamam'
            icon = ":/resim/kaynakjpg/hitchhikeguidetogalaxy1_config.png"
            self.MesajBoxWarning(baslik, metin, ok, icon)
        
        elif rowCount == 0:
            self.acilis = AcilisEkrani()
    
    def disPlayStats(self, params): #raporların oluşması
        kullanici = self.ui.txtKullanici.text()
        df = self.TablodakiVeriler()
        kontrol1 = [i for i in params if i=='-Yok-'] #yok'lar
        kontrol2 = [i for i in params if i!='-Yok-'] #seçilenler

        baslik1 = 'GEÇERSİZ İŞLEM'
        metin1 = 'Excell dosyan açık olabilir \n\nya da seçtiğin parametrelerde eksik değerler var..!\n\nEğer şova kalktıysan ne yaptığını aşadağıdaki adrese mail at:\n\nraifefendiler@gmail.com'
        ok = 'Ok...!'
        icon = 'kaynakjpg/Jeltz-icon.png'

        if len(kontrol2) == len(set(kontrol2)):
            pass
        else:
            metin = 'Parametreleri benzersiz seçmelisin..'
            self.MesajBoxWarning(baslik1, metin, ok, icon)
            return

        try:
            if len(kontrol1)==0: #eğer elimde 3 tane seçili varsa
                unq1 = df[kontrol2[0]].unique() # ilk parametre ele alındı
                unq2 = df[kontrol2[1]].unique() # ikinci parametre ele alındı
                unq3 = df[kontrol2[2]].unique() # üçüncü parametre ele alındı
                path = os.path.join(os.path.expanduser("~"), "Desktop", "Rapor.xlsx")
                with ExcelWriter  (path) as f:
                    anaRapor = df.to_excel(f, kullanici, index=False)
                    for i  in unq1:
                        rpr1 = df.loc[df[kontrol2[0]] == i] #ilk paramtrenin unique değerlerine göre tablolar oluşturuldu
                        rpr1.to_excel(f, (kontrol2[0]+" "+i), index=False)
                    for j in unq2:
                        rpr2 = df.loc[df[kontrol2[1]] == j] #ikinci paramtrenin unique değerlerine göre tablolar oluşturuldu
                        rpr2.to_excel(f, (kontrol2[1]+" "+j), index=False)
                    for k in unq3:
                        rpr3 = df.loc[df[kontrol2[2]] == k] #ikinci paramtrenin unique değerlerine göre tablolar oluşturuldu
                        rpr3.to_excel(f, (kontrol2[2]+" "+k), index=False)
                baslik = ' OLUŞTURULDU...!'
                metin1 = 'Rapor Oluşturuldu...!'
                ok = 'Tamam'
                icon = ":/resim/kaynakjpg/Microsoft-Office-Excel-icon.png"
                self.MesajBoxWarning(baslik, metin1, ok, icon)
        except:
            self.MesajBoxWarning(baslik1, metin1, ok, icon)
            return

        try:
            if len(kontrol1)==1: #eğer elimde 2 tane seçili varsa
                unq1 = df[kontrol2[0]].unique() # ilk parametre ele alındı
                unq2 = df[kontrol2[1]].unique() # ikinci parametre ele alındı
                path = os.path.join(os.path.expanduser("~"), "Desktop", "Rapor.xlsx")
                with ExcelWriter  (path) as f:
                    anaRapor = df.to_excel(f, kullanici, index=False)
                    for i  in unq1:
                        rpr1 = df.loc[df[kontrol2[0]] == i] #ilk paramtrenin unique değerlerine göre tablolar oluşturuldu
                        rpr1.to_excel(f, (kontrol2[0]+" "+i), index=False)

                    for j in unq2:
                        rpr2 = df.loc[df[kontrol2[1]] == j] #ikinci paramtrenin unique değerlerine göre tablolar oluşturuldu
                        rpr2.to_excel(f, (kontrol2[1]+" "+j), index=False)
                baslik = ' OLUŞTURULDU...!'
                metin1 = 'Rapor Oluşturuldu...!'
                ok = 'Tamam'
                icon = ":/resim/kaynakjpg/Microsoft-Office-Excel-icon.png"
                self.MesajBoxWarning(baslik, metin1, ok, icon)

        except:
            self.MesajBoxWarning(baslik1, metin1, ok, icon)
            return

        try:
            if len(kontrol1)==2: #eğer elimde 1 tane seçili varsa
                unq1 = df[kontrol2[0]].unique() 
                path = os.path.join(os.path.expanduser("~"), "Desktop", "Rapor.xlsx")
                with ExcelWriter  (path) as f:
                    anaRapor = df.to_excel(f, kullanici, index=False)
                    for i in unq1:
                        rpr1 = df.loc[df[kontrol2[0]] == i]
                        rpr1.to_excel(f,(kontrol2[0]+" "+i), index=False)
                baslik = ' OLUŞTURULDU...!'
                metin1 = 'Rapor Oluşturuldu...!'
                ok = 'Tamam'
                icon = ":/resim/kaynakjpg/Microsoft-Office-Excel-icon.png"
                self.MesajBoxWarning(baslik, metin1, ok, icon)

        except:
            self.MesajBoxWarning(baslik1, metin1, ok, icon)
            return
        
        try:
            if len(kontrol1)==3: #eğer elimde 0 tane seçili varsa
                path = os.path.join(os.path.expanduser("~"), "Desktop", "Rapor.xlsx")
                with ExcelWriter  (path) as f:
                    anaRapor = df.to_excel(f, kullanici, index=False)
                baslik = ' OLUŞTURULDU...!'
                metin1 = 'Rapor Oluşturuldu...!'
                ok = 'Tamam'
                icon = ":/resim/kaynakjpg/Microsoft-Office-Excel-icon.png"
                self.MesajBoxWarning(baslik, metin1, ok, icon)
        except:
            self.MesajBoxWarning(baslik1, metin1, ok, icon)
            return

############################################################# İzin Kutusu İşlemleri ve Eventler  #########################################################################
    
    def IzinEkle(self):
        currentIndex = self.ui.listItems.currentRow() #seçili olan
        izinTuru = self.ui.txtIzinTuru.text()
        izinTuru = izinTuru.strip()
        izinTuru = izinTuru.replace("i", "İ").upper()
        text = self.ui.dateIzinBaslangic.text()+"-"+self.ui.dateIzinBitis.text()+" "+ str.upper(izinTuru)
        if izinTuru and text is not None:
            self.ui.listItems.insertItem(currentIndex, text)   #seçili olana ekle

        personelKod = self.ui.txtPersKod.text()
        ad = self.ui.txtAd.text()
        if ad.startswith('i'):
            ad = 'İ' + ad [1:]
        ad = ad.capitalize()
        soyad = self.ui.txtSoyad.text().replace("i", "İ").upper()
        tc = self.ui.txtTC.text()
        unvan = self.ui.txtUnvan.text()
        IzinBaslaT = self.ui.dateIzinBaslangic.text()
        IzinBitisTarh = self.ui.dateIzinBitis.text()
        self.DataBaseIzinEkle(personelKod, ad, soyad, tc, unvan, IzinBaslaT, IzinBitisTarh, izinTuru)
        
        self.KalanIzin()
        self.ui.listItems.sortItems(Qt.SortOrder.AscendingOrder)
        self.ui.txtIzinTuru.clear()
        self.ui.statusbar.showMessage("{}-{} tarihleri arasına {} eklendi".format(self.ui.dateIzinBaslangic.text(),self.ui.dateIzinBitis.text(),str.upper(izinTuru)), self.StatusTime)
        self.ui.statusbar.setStyleSheet("color:rgb(0,0,255)")

    def IzinSil(self):
        index = self.ui.listItems.currentRow()
        item = self.ui.listItems.item(index)
        if item is None:
            return

        baslik = 'İZİN SİLME'
        metin = item.text() + " Tarih Aralığı İzinler Silinsin mi?  "
        evet = 'Evet'
        hayir = 'Hayır'
        result = self.MesajBoxSoru(baslik, metin, evet, hayir)
        if result == evet:
            item = self.ui.listItems.takeItem(index)
            seciliIzin = item.text()
            self.DataBaseIzinSil(seciliIzin)

            del item
            self.KalanIzin()
            self.ui.statusbar.showMessage("Seçili İzin Silindi", self.StatusTime)
            self.ui.statusbar.setStyleSheet("color:rgb(255,0,0)")

    def IzinYukari(self):
        index = self.ui.listItems.currentRow()
        if index >=1:
            item = self.ui.listItems.takeItem(index)
            self.ui.listItems.insertItem(index-1, item)
            self.ui.listItems.setCurrentItem(item)

    def IzinAsagi(self):
        index = self.ui.listItems.currentRow()
        if index < self.ui.listItems.count()-1:
            item = self.ui.listItems.takeItem(index)
            self.ui.listItems.insertItem(index+1, item)
            self.ui.listItems.setCurrentItem(item)

    def SeciliIzinTatilDenetle(self, *arg):
        pj=Puantaj(*arg)
        index = self.ui.listItems.currentItem().text()
        nesne1 = re.match(".+-",index)
        nesne1 = nesne1.group()
        nesne1 = to_datetime(nesne1[:-1], format="%d.%m.%Y")
        nesne2 = re.search("-.+\s",index)
        nesne2 = nesne2.group()
        nesne2 = to_datetime(nesne2[1:-1],format="%d.%m.%Y")

        GirilenIzinKapsamiGunleri = date_range(start=nesne1.date(), end=nesne2.date(),freq="D")

        resmi = [p.strftime('%d-%B-%Y-%A') for p in GirilenIzinKapsamiGunleri if p in pj.SeciliDonemResmiTatillerIsGunleri()[1]]
        tatil = [p.strftime('%d-%B-%Y-%A') for p in GirilenIzinKapsamiGunleri if p in pj.SeciliDonemResmiTatillerIsGunleri()[0]]
        farks = [i for i in GirilenIzinKapsamiGunleri if i not in pj.SeciliDonemResmiTatillerIsGunleri()[2]]
        HtNrm = [i for i in GirilenIzinKapsamiGunleri if i in pj.HaftaTatilleriNormal()]

        if resmi:
            baslik1 = 'Resmi Tatil Günleri Ücretli İzin Kapsamındadır'
            metin1 = 'Aşağıdaki tarihler RESMİ TATİL gününe denk gelmektedir.\n\n{}'.format(str(resmi)).replace(",","\n")
            ok = 'Tamam'
            icon = ":/resim/kaynakjpg/Marvin-icon.png"
            self.MesajBoxWarning(baslik1, metin1, ok, icon)
        
        if (len(tatil)!=(len(GirilenIzinKapsamiGunleri) - len(farks)) or len(tatil)==(len(GirilenIzinKapsamiGunleri) - len(farks))) and HtNrm!=[]:
            baslik1 = 'Hafta Tatil Günleri Ücretli İzin Kapsamındadır'
            metin1 = 'Aşağıdaki tarihler HAFTA TATİL gününe denk gelmektedir.\n\n{}'.format(str(tatil)).replace(",","\n")
            ok = 'Tamam'
            icon = ":/resim/kaynakjpg/Marvin-icon.png"
            self.MesajBoxWarning(baslik1, metin1, ok, icon)

        if (len(tatil)!=(len(GirilenIzinKapsamiGunleri) - len(farks)) or len(tatil)==(len(GirilenIzinKapsamiGunleri) - len(farks))) and HtNrm==[]:
            baslik1 = 'Normal Çalışma Günler ya da Dönem Dışı'
            metin1 = 'İzinler Sadece Çalışma Günlerini Kapsamaktadır \nya da Dönem Dışı'
            ok = 'Tamam'
            icon = ":/resim/kaynakjpg/Marvin-icon.png"
            self.MesajBoxWarning(baslik1, metin1, ok, icon)
        
    def eventFilter(self, kaynak, aksiyon):
        if aksiyon.type() == QEvent.ContextMenu and kaynak is self.ui.listItems: #kayıtı izinlerin üzerindeki işlemler
            menu = QMenu()
            menu.addAction("Yukarı         ", self.IzinYukari)
            menu.addAction("Aşağı          ", self.IzinAsagi)
            menu.addAction("Sil            ", self.IzinSil)
            menu.addAction("Denetle        ", self.Datagonder)
            menu.exec_(aksiyon.globalPos())
            # if menu.exec_(aksiyon.globalPos()):
            #     item = kaynak.itemAt(aksiyon.pos())
            return True

        if self.ui.txtTC == kaynak and aksiyon.type() == QEvent.KeyPress: #Tc girildikten sonraki işlem
            if aksiyon.key() == Qt.Key_Tab:
                QTimer.singleShot(0, self.evenTabTc)
        
        if self.ui.listItems == kaynak and aksiyon.type() == QEvent.KeyPress: #Del tuşu ile izin silme
            if aksiyon.key() == Qt.Key_Delete:
                QTimer.singleShot(0, self.IzinSil)
      
        return super().eventFilter(kaynak, aksiyon)
    
    def closeEvent(self, aksiyon):
        baslik = 'ÇIKIŞ'
        metin = "UYGULAMA KAPATILSIN MI?"
        evet = 'Evet'
        hayir = 'Hayır'
        result = self.MesajBoxSoru(baslik, metin, evet, hayir)
        if result == evet:
            #QMainWindow.closeEvent(self, event)
            self.load.close()
            self.param.close()
            self.display.close()
            self.kayitliPersoneller.close()
            self.preview.close()
            while (self.ui.tableProducts.rowCount() > 0):
                    self.ui.tableProducts.removeRow(0)
            aksiyon.accept()
            #self.close()
        else:
            aksiyon.ignore()

    def keyPressEvent(self, Escape):

        if Escape.key() == Qt.Key_Escape:
            self.load.close()
            self.param.close()
            self.display.close()
            self.kayitliPersoneller.close()
            self.preview.close()
            self.close()
            
        else:
            super(Window, self).keyPressEvent(Escape)

    def evenTabTc(self):
        self.IzinBilgiGetir()
        self.BilgiGetir()
        self.KalanIzin()
    
    def IzinKayitKontrol(self, *arg):
        pj=Puantaj(*arg)
        
        if 1 <= len(self.ui.dateIStenAyrilis.text()) < 10:
            baslik = 'Tarih Formatı Geçersiz'
            metin = 'İşten Ayrılış Tarihi Geçersiz'
            ok = 'Ok.'
            icon = 'kaynakjpg/Jeltz-icon.png'
            self.MesajBoxWarning(baslik, metin, ok, icon)
            return
        
        if self.ui.dateIStenAyrilis.text() == "" or self.ui.dateIStenAyrilis.text() == " ":
            bosFormat = "02.01.1753"
        else:
            bosFormat = self.ui.dateIStenAyrilis.text().strip()
        izinTuru = self.ui.txtIzinTuru.text()

        if not re.match('^\s', izinTuru) and izinTuru !="": 
            DateIseBaslamaTarihi = to_datetime(self.ui.dateIseBaslama.text(),format="%d.%m.%Y")
            DateIstenAyrilisTarihi = to_datetime(bosFormat,format="%d.%m.%Y")

            for x,y in zip(pj.KayitliIzinSlicing()[0], pj.KayitliIzinSlicing()[1]):
                start = to_datetime(x,format="%d.%m.%Y")
                end = to_datetime(y,format="%d.%m.%Y")
                KayitliIzinKapsamiGunleri = date_range(start=start.date(), end=end.date(),freq="D")
                
                for z in KayitliIzinKapsamiGunleri:
                    if z in pj.GirilenIzinDatalar()[2]:
                        baslik1 = 'ÇİFT KAYIT...!'
                        metin1 = 'Girdiğiniz Tarih Aralığında Başka Kayıt Var...!'
                        ok = 'Tamam'
                        icon = ":/resim/kaynakjpg/Jeltz-icon.png"
                        self.MesajBoxWarning(baslik1, metin1, ok, icon)
                        return 
            
            if pj.GirilenIzinDatalar()[1] < pj.GirilenIzinDatalar()[0]:
                baslik1 = 'YANLIŞ KAYIT...!'
                metin1 = 'Bitiş Tarihi Başlangıç Tarihinden Küçük...!'
                ok = 'Tamam'
                icon = ":/resim/kaynakjpg/Jeltz-icon.png"
                self.MesajBoxWarning(baslik1, metin1, ok, icon)
                return
                
            baslama = (DateIseBaslamaTarihi - offsets.Day(1))
            bitis = (DateIstenAyrilisTarihi + offsets.Day(1))
            for gunler in  pj.GirilenIzinDatalar()[2]:
                if gunler <= baslama:
                    baslik1 = 'YANLIŞ KAYIT...!'
                    metin1 = 'İşe Giriş Tarihinden Önce Kayıt giremezsiniz..!'
                    ok = 'Tamam'
                    icon = ":/resim/kaynakjpg/Jeltz-icon.png"
                    self.MesajBoxWarning(baslik1, metin1, ok, icon)
                    return

                if (not self.ui.dateIStenAyrilis.text() in {"02.01.1753","2.01.1753","02.1.1753","2.1.1753"," ",""}) and gunler >= bitis:
                    baslik1 = 'YANLIŞ KAYIT...!'
                    metin1 = 'İşten Ayrılış Tarihinden sonra Kayıt giremezsiniz..!'
                    ok = 'Tamam'
                    icon = ":/resim/kaynakjpg/Jeltz-icon.png"
                    self.MesajBoxWarning(baslik1, metin1, ok, icon)
                    return
        
            else:
                resmi = [p.strftime('%d-%B-%Y-%A') for p in pj.GirilenIzinDatalar()[2] if p in pj.SeciliDonemResmiTatillerIsGunleri()[1]]
                tatil = [p.strftime('%d-%B-%Y-%A') for p in pj.GirilenIzinDatalar()[2] if p in pj.SeciliDonemResmiTatillerIsGunleri()[0]]
                HtNrm = [i for i in pj.GirilenIzinDatalar()[2] if i in pj.HaftaTatilleriNormal()]
                farks = [i for i in pj.GirilenIzinDatalar()[2] if i not in pj.SeciliDonemResmiTatillerIsGunleri()[2]]

                           
                if resmi:
                    baslik = 'Resmi Tatil Günleri Ücretli İzin Kapsamındadır'
                    metin = 'Aşağıdaki tarihler RESMİ TATİL gününe denk gelmektedir.\nDevam Edilsin mi?\n\n{}'.format(str(resmi)).replace(",","\n")
                    evet = 'Evet'
                    hayir = 'Hayır'
                    result = self.MesajBoxSoru(baslik, metin, evet, hayir)
                    if result == evet:
                        pass
                    else:
                        return
                        
                if (len(tatil)!=(len(pj.GirilenIzinDatalar()[2]) - len(farks)) or len(tatil)==(len(pj.GirilenIzinDatalar()[2]) - len(farks))) and HtNrm!=[]:
                    baslik = 'Hafta Tatil Günleri Ücretli İzin Kapsamındadır'
                    metin = 'Aşağıdaki tarihler HAFTA TATİL gününe denk gelmektedir.\nDevam Edilsin mi?\n\n{}'.format(str(tatil)).replace(",","\n")
                    evet = 'Evet'
                    hayir = 'Hayır'
                    result = self.MesajBoxSoru(baslik, metin, evet, hayir)
                    if result == evet:
                        pass
                    else:
                        return
                
                self.IzinEkle()

    def KalanIzin(self):
        self.ui.txtKalanIzin.clear()
        self.ui.txtKidem.clear()

        vmatch = np.vectorize(lambda x: bool(re.match('^Y',x)))
        veri = self.ui.txtTC.text()
        sql = 'Select Tc, IzinBaslaT, IzinBitisTarh, IzinTuru FROM izinler'
        sorgu = self.DBsorgu(sql)
        KullanilanYillikIzinTarihleri = []
        for i in sorgu:
            if (str(i[0]) == veri):
                data = np.array(list(i))
                sel = vmatch(data)
                if True in sel:
                    KullanilanYillikIzinTarihleri += [list(i[1:-1])]

        Days = ['W-SAT', 'W-SUN', 'W-MON', 'W-TUE', 'W-WED', 'W-THU', 'W-FRI', 'None']
        HaftaTatilleri = [Days[self.ui.comboTatilGunu_1.currentIndex()]] + [Days[self.ui.comboTatilGunu_2.currentIndex()]]
        HaftaTatilleri = list(set(HaftaTatilleri))
        HaftaIci = list(set(Days[:-1]) - set(HaftaTatilleri))
        HaftaTatilleri = [i for i in HaftaTatilleri if i!='None' ]

        KullanilanToplamYillikIzinGunleri = 0
        ToplamIzinGunleri = 0
        ToplamTatilGunleri = 0
        
        for gun in KullanilanYillikIzinTarihleri:
            start = to_datetime(gun[0], format="%d.%m.%Y")
            end = to_datetime(gun[1], format="%d.%m.%Y")
            intGu = len(date_range(start=start, end=end, freq='D'))
            ToplamIzinGunleri += intGu

            if len(HaftaTatilleri) == 2:
                siralaTatil1 = date_range(start=start, end=end, freq=HaftaTatilleri[0])
                siralaTatil2 = date_range(start=start, end=end, freq=HaftaTatilleri[1])
                GenelTatilGunleriTS = self.GenelTatil.holidays(start=start, end=end)
                tatiller1 = siralaTatil1.union(GenelTatilGunleriTS)
                tatiller2 = siralaTatil2.union(GenelTatilGunleriTS)
                tatil = tatiller1.union(tatiller2)
                intT = len(tatil)
                ToplamTatilGunleri += intT

            if len(HaftaTatilleri) == 1:
                siralaTatil = date_range(start=start, end=end, freq=HaftaTatilleri[0])
                GenelTatilGunleriTS = self.GenelTatil.holidays(start=start, end=end)
                tatiller = siralaTatil.union(GenelTatilGunleriTS)
                intT = len(tatiller)
                ToplamTatilGunleri += intT 
            
            if len(HaftaTatilleri) == 0:
                GenelTatilGunleriTS = self.GenelTatil.holidays(start=start, end=end)
                intT = len(GenelTatilGunleriTS)
                ToplamTatilGunleri += intT 

        YillikIzinGunleri = ToplamIzinGunleri - ToplamTatilGunleri
        KullanilanToplamYillikIzinGunleri += YillikIzinGunleri
               
        IseBaslamaTarihi = dt.strptime(self.ui.dateIseBaslama.text(),"%d.%m.%Y") #işe başlama tarihi date
        MinKidemTarihi = IseBaslamaTarihi + DateOffset(years=1) #1 yıllık kıdem - işe başlama tarihinden sonra yıl dönümü

        if len(self.ui.dateIStenAyrilis.text()) == 10:
            IstenAyrilisTari = dt.strptime(self.ui.dateIStenAyrilis.text(),"%d.%m.%Y")
            BugununTarihi = IstenAyrilisTari
        else:
            BugununTarihi = dt.today() #bugünün tarihi

        farkgun = BugununTarihi - MinKidemTarihi #bugünün tarihi yıl dönümünden fazla mı
        KidemDetayFark = relativedelta.relativedelta(BugununTarihi, IseBaslamaTarihi)
        KidemYil = KidemDetayFark.years
        KidemAy = KidemDetayFark.months
        KidemGun = KidemDetayFark.days

        HakedilenYillik = 0
        if farkgun.days >= 0: #bugünün tarihi yıl dönümünden fazla mı
            # farkYil = BugununTarihi.year - IseBaslamaTarihi.year
           
            # Kidem = IseBaslamaTarihi + DateOffset(years=farkYil) #yıl farkı kadar kıdem
            # fark = Kidem.year - IseBaslamaTarihi.year
            
            if 5>= KidemYil >=1:
                HakedilenYillik +=  KidemYil * 14
                KalanYillikIizin = HakedilenYillik - KullanilanToplamYillikIzinGunleri
                self.ui.txtKalanIzin.setText('{} Gün Yıllık İzin'.format(str(KalanYillikIizin)))
                self.ui.txtKidem.setText('{} Yıl {} Ay {} Gün Kıdem'.format(KidemYil, KidemAy, KidemGun))
            
            elif 14>= KidemYil >=6:
                ikinciAsama = KidemYil - 5
                HakedilenYillik +=  (KidemYil * 14) + (ikinciAsama * 6)
                KalanYillikIizin = HakedilenYillik - KullanilanToplamYillikIzinGunleri
                self.ui.txtKalanIzin.setText('{} Gün Yıllık İzin'.format(str(KalanYillikIizin)))
                self.ui.txtKidem.setText('{} Yıl {} Ay {} Gün Kıdem'.format(KidemYil, KidemAy, KidemGun))
            
            elif KidemYil >=15:
                ikinciAsama = KidemYil - 5
                ucuncuAsama = KidemYil - 14
                HakedilenYillik +=  (KidemYil * 14) + (ikinciAsama * 6) + (ucuncuAsama * 6)
                KalanYillikIizin = HakedilenYillik - KullanilanToplamYillikIzinGunleri
                self.ui.txtKalanIzin.setText('{} Gün Yıllık İzin'.format(str(KalanYillikIizin)))
                self.ui.txtKidem.setText('{} Yıl {} Ay {} Gün Kıdem'.format(KidemYil, KidemAy, KidemGun))
            
        else:
            KalanYillikIizin = HakedilenYillik - KullanilanToplamYillikIzinGunleri
            self.ui.txtKalanIzin.setText('{} Gün Yıllık İzin'.format(str(KalanYillikIizin)))
            self.ui.txtKidem.setText('{} Yıl {} Ay {} Gün Kıdem'.format(KidemYil, KidemAy, KidemGun))

############################################################# puantajlar ve Datalar ################################################################

    def IstenAyrilisSignals(self): #../.../.... formatındaki işten ayrılış '.' formatına çevrildi
        dateF = self.ui.dateIStenAyrilis.text().replace("/", ".")
        self.ui.dateIStenAyrilis.setText(dateF)
        if self.ui.dateIStenAyrilis.text() ==" ":
            self.ui.dateIStenAyrilis.setText('')

        DateIseBaslamaTarihi = to_datetime(self.ui.dateIseBaslama.text(),format="%d.%m.%Y")
        DateIstenAyrilisTarihi = to_datetime(self.ui.dateIStenAyrilis.text(),format="%d.%m.%Y")
        if DateIstenAyrilisTarihi < DateIseBaslamaTarihi:
            baslik1 = 'YANLIŞ KAYIT...!'
            metin1 = 'İşe Giriş Tarihinden Önce Kayıt giremezsiniz..!'
            ok = 'Tamam'
            icon = ":/resim/kaynakjpg/Jeltz-icon.png"
            self.MesajBoxWarning(baslik1, metin1, ok, icon)
            self.ui.dateIStenAyrilis.clear()
            return

    def AlinanKayitlar(self): #mevcut girilen veriler

        personelKod = self.ui.txtPersKod.text()
        ad = str.capitalize(self.ui.txtAd.text())
        soyad = str.upper(self.ui.txtSoyad.text())
        tc = self.ui.txtTC.text()
        unvan = self.ui.txtUnvan.text()
        iseBaslamaTarihi = self.ui.dateIseBaslama.text()

        if 1 <= len(self.ui.dateIStenAyrilis.text()) < 10:
            baslik = 'Tarih Formatı Geçersiz'
            metin = 'İşten Ayrılış Tarihi Geçersiz'
            ok = 'Ok.'
            icon = 'kaynakjpg/Jeltz-icon.png'
            self.MesajBoxWarning(baslik, metin, ok, icon)
            return

        if self.ui.dateIStenAyrilis.text()=="02.01.1753" or self.ui.dateIStenAyrilis.text()=="2.01.1753" or self.ui.dateIStenAyrilis.text()=="02.1.1753" or self.ui.dateIStenAyrilis.text()=="2.1.1753":
            İstenAyrilisTarihi=""
        else:
            İstenAyrilisTarihi = self.ui.dateIStenAyrilis.text().strip()

        SGKFirma = self.ui.txtSGK_Firma.text()
        SGKSube = self.ui.txtSGK_Sb.text()
        sehir = self.ui.txtSehir.text()
        lokasyon = self.ui.txtLokasYon.text()
        departman = self.ui.txtDepartman.text()
        
        donem = self.ui.comboYil.currentText()+"-"+self.ui.comboAy.currentText()
        self.ui.txtExtClmn.insert(donem)
        extcomun = self.ui.txtExtClmn.text()

        liste = [personelKod, ad, soyad, tc, unvan, iseBaslamaTarihi, İstenAyrilisTarihi, SGKFirma, SGKSube, sehir, lokasyon, departman, extcomun]

        return liste

    def Datagonder(self): #mevcut girilen verilerin istenlen evente göre (izin eklemede - izin denetlemede - puantaj oluşturmada)
        dateIseBaslama = self.ui.dateIseBaslama.text()
        dateIStenAyrilis = self.ui.dateIStenAyrilis.text().strip()
        GeciciKayitlar = [self.ui.listItems.item(x).text() for x in range(self.ui.listItems.count())]
        dateIzinBaslangic = self.ui.dateIzinBaslangic.text()
        dateIzinBitis = self.ui.dateIzinBitis.text()
        ComboTatil1Current = self.ui.comboTatilGunu_1.currentIndex()
        ComboTatil2Current = self.ui.comboTatilGunu_2.currentIndex()
        ComboTatil1Count = self.ui.comboTatilGunu_1.count()
        ComboTatil2Count = self.ui.comboTatilGunu_2.count()
        SeciliYil = self.ui.comboYil.currentText()
        SeciliAyIndex = (self.ui.comboAy.currentIndex()+1)

        rbt = self.sender()

        if rbt.text()=='İZİN\nEKLE':
            return self.IzinKayitKontrol(dateIseBaslama, dateIStenAyrilis, GeciciKayitlar, dateIzinBaslangic, 
        dateIzinBitis, ComboTatil1Current, ComboTatil2Current, ComboTatil1Count, ComboTatil2Count, SeciliYil, SeciliAyIndex)
        if rbt.text()==' PUANTAJ\n OLUŞTUR':
            return self.KayitPuantaj(dateIseBaslama, dateIStenAyrilis, GeciciKayitlar, dateIzinBaslangic, 
        dateIzinBitis, ComboTatil1Current, ComboTatil2Current, ComboTatil1Count, ComboTatil2Count, SeciliYil, SeciliAyIndex)
        else:
            return self.SeciliIzinTatilDenetle(dateIseBaslama, dateIStenAyrilis, GeciciKayitlar, dateIzinBaslangic, dateIzinBitis, 
            ComboTatil1Current, ComboTatil2Current, ComboTatil1Count, ComboTatil2Count, SeciliYil, SeciliAyIndex)

    def KayitPuantaj(self, *arg): #mevcut girilen verilerden kayıtlı puantaj oluşturma
        pj=Puantaj(*arg)

        Tc = self.ui.txtTC.text()
        if len(Tc) != 11:
            baslik1 = 'TC Kimlik No Hatalı...!'
            metin1 = 'TC Kimlik Numarası 11 Haneli Olmalıdır...!'
            ok = 'Tamam'
            icon = ":/resim/kaynakjpg/Jeltz-icon.png"
            self.MesajBoxWarning(baslik1, metin1, ok, icon)
            return

        if 1 <= len(self.ui.dateIStenAyrilis.text()) < 10:
            baslik = 'Tarih Formatı Geçersiz'
            metin = 'İşten Ayrılış Tarihi Geçersiz'
            ok = 'Ok.'
            icon = 'kaynakjpg/Jeltz-icon.png'
            self.MesajBoxWarning(baslik, metin, ok, icon)
            return
        
        liste = self.AlinanKayitlar()

        ad = str.capitalize(self.ui.txtAd.text())
        soyad = str.upper(self.ui.txtSoyad.text())
        donem = self.ui.comboYil.currentText()+"-"+self.ui.comboAy.currentText()

        liste = liste+pj.PuantajOlustur()

        if not re.match('^\s', ad) and (ad and soyad !=""):

            baslik = '{} DÖNEM PUANTAJI'.format(donem)
            metin = '{} {}    için Kayıt Oluşturulsun mu?'.format(ad,soyad)
            evet = 'Evet'
            hayir = 'Hayır'
            result = self.MesajBoxSoru(baslik, metin, evet, hayir)
            if result == evet:
                rowCount = self.ui.tableProducts.rowCount()
                self.ui.tableProducts.insertRow(rowCount)
                for x,y in enumerate(liste):
                    if y!="":
                        self.ui.tableProducts.setItem(rowCount,x,QTableWidgetItem(y))
                        #self.ui.tableProducts.item(rowCount, x).setBackground(QColor(100,100,150))
                       
                    # else:
                    #     self.ui.tableProducts.setItem(rowCount,x,QTableWidgetItem("--"))
                
                self.ui.statusbar.showMessage("{} {} Adlı Kişinin {} Dönem Puantajı Oluşturuldu".format(ad,soyad,donem), self.StatusTime)
                self.ui.statusbar.setStyleSheet("color:rgb(0,0,255)")
                            
                # self.ui.txtAd.clear()
                # self.ui.txtSoyad.clear()
                # self.ui.txtTC.clear()
                # self.ui.dateIStenAyrilis.clear()
                # self.ui.listItems.clear()
            self.ui.txtExtClmn.clear()
            self.ui.txtIzinTuru.clear()
        
    def BilgilerEkrani(self, secili):
        self.ui.statusbar.showMessage('{} Seçildi          {}'.format(secili,100*'/'), self.StatusTime)
        self.ui.statusbar.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";\n"
"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")

    def Temizle(self): #girilen mevcut verileri temizler
        self.ui.txtPersKod.clear()
        self.ui.txtAd.clear()
        self.ui.txtSoyad.clear()
        self.ui.txtTC.clear()
        self.ui.txtUnvan.clear()
        self.ui.txtSGK_Firma.clear()
        self.ui.txtSGK_Sb.clear()
        self.ui.txtSehir.clear()
        self.ui.txtLokasYon.clear()
        self.ui.txtDepartman.clear()
        self.ui.txtExtClmn.clear()
        self.ui.txtIzinTuru.clear()
        self.ui.listItems.clear()
        self.ui.txtKalanIzin.clear()
        self.ui.dateIStenAyrilis.clear()
        self.ui.statusbar.showMessage("Bütün Bilgiler Temizlendi", self.StatusTime)
        self.ui.statusbar.setStyleSheet("color:rgb(255,0,0)")
    
############################################################### database islemleri ##################################################################

    def DataBasePersonelEkle(self):
        personelKod = self.ui.txtPersKod.text()
        if not re.match('^\s', self.ui.txtAd.text()) and (self.ui.txtAd.text() !=""):
            ad = self.ui.txtAd.text()
            if ad.startswith('i'):
                ad = 'İ' + ad [1:]
            ad = ad.capitalize()

        else:
            baslik = 'İsim Eksik..!'
            metin = 'Personel İsmi Giriniz...'
            ok = 'Ok.'
            icon = 'kaynakjpg/Jeltz-icon.png'
            self.MesajBoxWarning(baslik, metin, ok, icon)
            return
        
        if not re.match('^\s', self.ui.txtSoyad.text()) and (self.ui.txtSoyad.text() !=""):
            soyad = self.ui.txtSoyad.text().replace("i", "İ").upper()

        else:
            baslik = 'Soyad Eksik!'
            metin = 'Personel Soyad Giriniz..'
            ok = 'Ok.'
            icon = 'kaynakjpg/Jeltz-icon.png'
            self.MesajBoxWarning(baslik, metin, ok, icon)
            return
        
        if not re.match('^\s', self.ui.txtTC.text()) and (self.ui.txtTC.text() !="") and (len(self.ui.txtTC.text())==11):
            sql = 'Select Tc FROM personel'
            sorguTc = self.DBsorgu(sql)
            if sorguTc:
                for i in sorguTc:
                    if i[0] == int(self.ui.txtTC.text()):
                        baslik = 'Çift Kayıt'
                        metin = 'Aynı kişi için çift kayıt Yapılamaz!!'
                        ok = 'Ok.'
                        icon = 'kaynakjpg/Jeltz-icon.png'
                        self.MesajBoxWarning(baslik, metin, ok, icon)
                        return
                        
                    else:
                        tc = int(self.ui.txtTC.text())
                # else:
                #     tc = int(self.ui.txtTC.text())
         
        else:
            baslik = 'TC No Eksik!'
            metin = '11 Haneli TC Numarası Giriniz..'
            ok = 'Ok.'
            icon = 'kaynakjpg/Jeltz-icon.png'
            self.MesajBoxWarning(baslik, metin, ok, icon)
            return

        tc = int(self.ui.txtTC.text())
        unvan = self.ui.txtUnvan.text()
        iseBaslamaTarihi = self.ui.dateIseBaslama.text()

        if 1 <= len(self.ui.dateIStenAyrilis.text()) < 10:
            baslik = 'Tarih Formatı Geçersiz'
            metin = 'İşten Ayrılış Tarihi Geçersiz'
            ok = 'Ok.'
            icon = 'kaynakjpg/Jeltz-icon.png'
            self.MesajBoxWarning(baslik, metin, ok, icon)
            return

        if self.ui.dateIStenAyrilis.text()=="02.01.1753" or self.ui.dateIStenAyrilis.text()=="2.01.1753" or self.ui.dateIStenAyrilis.text()=="02.1.1753" or self.ui.dateIStenAyrilis.text()=="2.1.1753":
            İstenAyrilisTarihi=""
        else:
            İstenAyrilisTarihi = self.ui.dateIStenAyrilis.text().strip()

        SGKFirma = self.ui.txtSGK_Firma.text()
        SGKSube = self.ui.txtSGK_Sb.text()
        sehir = self.ui.txtSehir.text()
        lokasyon = self.ui.txtLokasYon.text()
        departman = self.ui.txtDepartman.text()
      
        sqlEkle = "insert into personel (PersKod, Ad, Soyad, Tc, Unvan, IseBaslamT, IstenAyrilisT, SGKFirma, SGKSube, Sehir, Lokasyon, Departman) values (?,?,?,?,?,?,?,?,?,?,?,?)"
        self.DBsorguArg(sqlEkle, personelKod, ad, soyad, tc, unvan, iseBaslamaTarihi, İstenAyrilisTarihi, SGKFirma, SGKSube, sehir, lokasyon, departman)
        self.ui.statusbar.showMessage('{} {} İsimli Personel Veritabanına Kayıt Edildi'.format(ad,soyad),self.StatusTime)
        self.kayitliPersoneller.ui.listItemsKayitliPers.clear()
        self.kayitliPersoneller.PersonelListele()
        self.kayitliPersoneller.PersonelBilgileriTextItem()
                
    def DataBaseIzinEkle(self, personelKod, ad, soyad, tc, unvan, IzinBaslaT, IzinBitisTarh, Izinturu): 
        sql = 'Select Tc FROM personel'
        sorguTc = self.DBsorgu(sql)

        if not re.match('^\s', self.ui.txtTC.text()) and (self.ui.txtTC.text() !="") and (len(self.ui.txtTC.text())==11):
            for i in sorguTc:
                if i[0] == int(self.ui.txtTC.text()):
                    sqlIzin = "insert into izinler (PersKod, Ad, Soyad, Tc, Unvan, IzinBaslaT, IzinBitisTarh, IzinTuru, id ) values (?,?,?,?,?,?,?,?,?)"
                    self.DBsorguArg(sqlIzin, personelKod, ad, soyad, tc, unvan, IzinBaslaT, IzinBitisTarh, Izinturu, None)
                    self.ui.statusbar.showMessage('{} {} İsimli Personele İzin Kayıt İşlemi Gerçekleşti'.format(ad,soyad),self.StatusTime)
                    self.kayitliPersoneller.ui.listItemsKayitliPers.clear()
                    self.kayitliPersoneller.PersonelListele()
                    self.kayitliPersoneller.PersonelBilgileriTextItem()
                                    
    def DataBaseIzinSil(self, arg):
        seciliIzin = arg
        #seciliIzin = self.ui.listItemsKayitliPersIzinler.currentItem().text()
        #dt = self.ui.listItemsKayitliPers.currentItem().data(Qt.UserRole)

        tc = self.ui.txtTC.text()
        nesne1 = re.match(".+-",seciliIzin)
        nesne1 = nesne1.group()
        IzinBaslaT = nesne1[:-1]
        nesne2 = re.search("-.+\s",seciliIzin)
        nesne2 = nesne2.group()
        IzinBitisTarh = nesne2[1:-1]
        nesne3 = re.search("\s.+",seciliIzin)
        nesne3 = nesne3.group()
        Izinturu = nesne3[1:]
        sqlTC = 'Select Tc FROM personel'
        obj = self.DBsorgu(sqlTC)
        if not re.match('^\s', self.ui.txtTC.text()) and (self.ui.txtTC.text() !="") and (len(self.ui.txtTC.text())==11):
            for i in obj:
                if (i[0] == int(self.ui.txtTC.text())):
                    sql = "Delete from izinler where Tc = ? and IzinBaslaT=? and IzinBitisTarh=? and IzinTuru=?"
                    self.DBsorguArg(sql, tc, IzinBaslaT, IzinBitisTarh, Izinturu)
                    baslik = 'SQL Kayıt Silme'
                    metin = 'izinler silindi'
                    ok = 'Tamam'
                    icon = ":/resim/kaynakjpg/hitchhikeguidetogalaxy1_config.png"
                    self.MesajBoxWarning(baslik, metin, ok, icon)
                    self.ui.listItems.clear()
                    self.IzinBilgiGetir()
                    self.kayitliPersoneller.ui.listItemsKayitliPers.clear()
                    self.kayitliPersoneller.PersonelListele()
                    self.kayitliPersoneller.PersonelBilgileriTextItem()
                                    
    def BilgiGetir(self):
        veri = self.ui.txtTC.text()
        if len(veri) != 11:
            baslik1 = 'TC Kimlik No Hatalı...!'
            metin1 = 'TC Kimlik Numarası 11 Haneli Olmalıdır...!'
            ok = 'Tamam'
            icon = ":/resim/kaynakjpg/Jeltz-icon.png"
            self.MesajBoxWarning(baslik1, metin1, ok, icon)
            
        sql = 'Select * FROM personel'
        sorgu = self.DBsorgu(sql)
        for i in sorgu:
            if (str(i[3]) == veri):
                self.ui.txtPersKod.setText(i[0])
                self.ui.txtAd.setText(i[1])
                self.ui.txtSoyad.setText(i[2])
                self.ui.txtTC.setText(str(i[3]))
                self.ui.txtUnvan.setText(str(i[4]))
                textBaslama = str(i[5]).split('.')
                self.ui.dateIseBaslama.setDate(QDate(int(textBaslama[2]), int(textBaslama[1]), int(textBaslama[0])))
                self.ui.dateIStenAyrilis.setText(str(i[6]))
                self.ui.txtSGK_Firma.setText(str(i[7]))
                self.ui.txtSGK_Sb.setText(str(i[8]))
                self.ui.txtSehir.setText(str(i[9]))
                self.ui.txtLokasYon.setText(str(i[10]))
                self.ui.txtDepartman.setText(str(i[11]))

    def IzinBilgiGetir(self): 
        veri = self.ui.txtTC.text()
        sql = 'Select * FROM izinler'
        self.ui.listItems.clear()
        sorgu = self.DBsorgu(sql)
        for i in sorgu:
            if (str(i[3]) == veri):
                #currentIndex = self.ui.listItems.currentRow()
                veri_ice = QListWidgetItem()
                veri_ice.setData(Qt.UserRole, i[8])
                text = str(i[5])+"-"+str(i[6])+" "+ str(i[7])
                veri_ice.setText(text) 
                self.ui.listItems.addItem(veri_ice) #insertItem
                #self.ui.listItems.insertItem(currentIndex, text)
    
    def DataBaseAlinanKayitlar(self, loadList):
        sql = 'Select Tc, IzinBaslaT, IzinBitisTarh, IzinTuru FROM izinler where Tc=?'
        
        dataTip = loadList[0][0]
        liste = loadList[0]
        param = loadList[1]
        self.ui.comboAy.setCurrentIndex(param[0])
        self.ui.comboYil.setCurrentIndex(param[1])
        self.ui.comboTatilGunu_1.setCurrentIndex(param[2])
        self.ui.comboTatilGunu_2.setCurrentIndex(param[3])

        if isinstance(dataTip, str):
            dateIseBaslama = liste[5]
            dateIStenAyrilis = liste[6]
            GeciciKayitlar = [self.kayitliPersoneller.ui.listItemsKayitliPersIzinler.item(x).text() for x in range(self.kayitliPersoneller.ui.listItemsKayitliPersIzinler.count())]
            dateIzinBaslangic = self.kayitliPersoneller.ui.dateKayitliPersIzinBaslangic.text()
            dateIzinBitis = self.kayitliPersoneller.ui.dateKayitliPersIzinBitis.text()
            ComboTatil1Current = self.ui.comboTatilGunu_1.currentIndex()
            ComboTatil2Current = self.ui.comboTatilGunu_2.currentIndex()
            ComboTatil1Count = self.ui.comboTatilGunu_1.count()
            ComboTatil2Count = self.ui.comboTatilGunu_2.count()
            SeciliYil = self.ui.comboYil.currentText()
            SeciliAyIndex = (self.ui.comboAy.currentIndex()+1)
            # self.DataBaseKayitPuantaj(dateIseBaslama, dateIStenAyrilis, GeciciKayitlar, dateIzinBaslangic, 
            # dateIzinBitis, ComboTatil1Current, ComboTatil2Current, ComboTatil1Count, ComboTatil2Count, SeciliYil, SeciliAyIndex)

            pj=Puantaj(dateIseBaslama, dateIStenAyrilis, GeciciKayitlar, dateIzinBaslangic, 
            dateIzinBitis, ComboTatil1Current, ComboTatil2Current, ComboTatil1Count, ComboTatil2Count, SeciliYil, SeciliAyIndex)
            liste = liste+pj.PuantajOlustur()

            ad = liste[1]
            soyad = liste[2]
            donem = self.ui.comboYil.currentText()+"-"+self.ui.comboAy.currentText()
            baslik = '{} DÖNEM PUANTAJI'.format(donem)
            metin = '{} {}    için Kayıt Oluşturulsun mu?'.format(ad,soyad)
            evet = 'Evet'
            hayir = 'Hayır'
            result = self.MesajBoxSoru(baslik, metin, evet, hayir)
            if result == evet:
                rowCount = self.ui.tableProducts.rowCount()
                self.ui.tableProducts.insertRow(rowCount)
                for x,y in enumerate(liste):
                    if isinstance(y, int):
                        y=str(y)
                    if y!="":
                        self.ui.tableProducts.setItem(rowCount,x,QTableWidgetItem(y))

        if isinstance(dataTip, tuple):
            for kişi in liste:
                kişi = list(kişi)
                sorguTc = self.DBsorguArg(sql, kişi[3])
                izinler = sorguTc

                GeciciKayitlar= []
                for iz in izinler:
                    iz=list(iz)
                    if iz[0]==kişi[3]:
                        kayitlar = '{}-{} {}'.format(iz[1], iz[2], iz[3])
                        GeciciKayitlar.append(kayitlar)
                                 
                dateIseBaslama = kişi[5]
                dateIStenAyrilis = kişi[6]
                
                dateIzinBaslangic = self.kayitliPersoneller.ui.dateKayitliPersIzinBaslangic.text()
                dateIzinBitis = self.kayitliPersoneller.ui.dateKayitliPersIzinBitis.text()
                ComboTatil1Current = self.ui.comboTatilGunu_1.currentIndex()
                ComboTatil2Current = self.ui.comboTatilGunu_2.currentIndex()
                ComboTatil1Count = self.ui.comboTatilGunu_1.count()
                ComboTatil2Count = self.ui.comboTatilGunu_2.count()
                SeciliYil = self.ui.comboYil.currentText()
                SeciliAyIndex = (self.ui.comboAy.currentIndex()+1)
                pj=Puantaj(dateIseBaslama, dateIStenAyrilis, GeciciKayitlar, dateIzinBaslangic, 
                dateIzinBitis, ComboTatil1Current, ComboTatil2Current, ComboTatil1Count, ComboTatil2Count, SeciliYil, SeciliAyIndex)

                ad = kişi[1]
                soyad = kişi[2]
                donem = self.ui.comboYil.currentText()+"-"+self.ui.comboAy.currentText()
                baslik = '{} DÖNEM PUANTAJI'.format(donem)
                metin = '{} {}\nKayıt Oluşturuluyor'.format(ad,soyad)
                evet = 'Evet'
                hayir = 'Hayır'
                result = self.MesajBoxSoru(baslik, metin, evet, hayir)
                if result == evet:
                    kişi = kişi+pj.PuantajOlustur()
                    rowCount = self.ui.tableProducts.rowCount()
                    self.ui.tableProducts.insertRow(rowCount)
                    for x,y in enumerate(kişi):
                        if isinstance(y, int):
                            y=str(y)
                        if y!="":
                            self.ui.tableProducts.setItem(rowCount,x,QTableWidgetItem(y))

    def DBConnect(self):
        home = str(Path.home())
        with closing(sqlite3.connect(home+"\\Personeller.db")) as con, con,  \
                closing(con.cursor()) as cur:
            try:
                AnaTablo = cur.execute("create table if not exists personel(PersKod text, Ad text, Soyad text, Tc int UNIQUE, Unvan text, IseBaslamT date, IstenAyrilisT date, SGKFirma text, SGKSube text, Sehir text, Lokasyon text, Departman text, id integer primary key autoincrement)")
                IzinTablo = cur.execute("create table if not exists izinler(PersKod text, Ad text, Soyad text, Tc int, Unvan text, IzinBaslaT date, IzinBitisTarh date, IzinTuru text, id integer primary key autoincrement, FOREIGN KEY (Tc) REFERENCES personel(Tc))")
                #ForeignKey = self.islem.execute("ALTER TABLE personel FOREIGN KEY (Tc) REFERENCES izinler(Tc)")
                con.commit()
                
            except Exception as hata:
                baslik = 'Sql Sorgu Hatası'
                metin = 'Hata Kodu: {}'.format(hata)
                ok = 'Tamam'
                icon = ":/resim/kaynakjpg/hitchhikeguidetogalaxy1_help.png"
                self.MesajBoxWarning(baslik, metin, ok, icon)     

    def DBsorgu(self, sql):
        home = str(Path.home())
        with closing(sqlite3.connect(home+"\\Personeller.db")) as con, con,  \
                closing(con.cursor()) as cur:
            try:
                cur.execute(sql)
                return cur.fetchall()
            
            except Exception as hata:
                baslik = 'Sql Sorgu Hatası'
                metin = 'Hata Kodu: {}'.format(hata)
                ok = 'Tamam'
                icon = ":/resim/kaynakjpg/hitchhikeguidetogalaxy1_help.png"
                self.MesajBoxWarning(baslik, metin, ok, icon)         
    
    def DBsorguArg(self, sql, *arg):
        home = str(Path.home())
        with closing(sqlite3.connect(home+"\\Personeller.db")) as con, con,  \
                closing(con.cursor()) as cur:
            try:
                cur.execute(sql, (*arg,))
                con.commit()
                return cur.fetchall()
            
            except Exception as hata:
                baslik = 'Sql Sorgu Hatası'
                metin = 'Hata Kodu: {}'.format(hata)
                ok = 'Tamam'
                icon = ":/resim/kaynakjpg/hitchhikeguidetogalaxy1_help.png"
                self.MesajBoxWarning(baslik, metin, ok, icon)         
    
########################################################## diğer tablolarla etkileşim #############################################################

    def OpenLoadPage(self):
        self.load.show()
        self.load.activateWindow()
        self.Temizle()
        self.load.setEnabled(True)
    
    def OpenParam(self):
        self.param.show()
        self.param.activateWindow()
    
    def OpenDisplayPage(self):
        rowCount = self.ui.tableProducts.rowCount()
        if rowCount > 0:
            self.display.show()
            self.display.activateWindow()
        
        else:
            self.acilis = AcilisEkrani()

    def OpenPreview(self): #dataframe yapısı numpy array olarak değiştirilmeli!!!!!!
        rowCount = self.ui.tableProducts.rowCount()
        if rowCount > 0:
            while (self.preview.ui.tableProductsPreview.rowCount() > 0):
                    self.preview.ui.tableProductsPreview.removeRow(0)

            basliklar = []
            for i in range(self.ui.tableProducts.model().columnCount()):
                basliklar.append(self.ui.tableProducts.horizontalHeaderItem(i).text())
            
            self.preview.ui.tableProductsPreview.setColumnCount(len(basliklar))
            self.preview.ui.tableProductsPreview.setHorizontalHeaderLabels(basliklar)
            
            ColumnWidth = [100,200,200,125,150,120,120,150,150,150,150,150,135,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
            for index, width in enumerate(ColumnWidth):
                self.preview.ui.tableProductsPreview.setColumnWidth(index,width)
            
            data = DataFrame(columns=basliklar)
            for r in range(self.ui.tableProducts.rowCount()):
                for c in range(self.ui.tableProducts.columnCount()):
                    obj = self.ui.tableProducts.item(r,c)
                    if obj is not None and obj.text() != '':
                        data.at[r, basliklar[c]] = self.ui.tableProducts.item(r, c).text()

            data = data.fillna(' ')
            for indx in range(len(data.index)):
                rowCount = self.preview.ui.tableProductsPreview.rowCount()
                self.preview.ui.tableProductsPreview.insertRow(rowCount)
                for c in range(len(data.columns)):
                    for r, row in data.iterrows():
                        try:
                            self.preview.ui.tableProductsPreview.setItem(r, c, QTableWidgetItem(str(data.iloc[r, c]).strip()))
                        except:
                            return
  
            self.preview.showMaximized()
            self.preview.activateWindow()
  
        else:
            self.acilis = AcilisEkrani()

    def OpenKullaniciDegistir(self):
        LoadList =['Merhaba Ben Geldim']
        self.signal.emit(LoadList)
        self.ui.centralwidget.setEnabled(False)
        self.ui.actionCSV_Aktar.setEnabled(False)
        self.ui.actionToplu_Y_kleme.setEnabled(False)
        self.ui.actionYenile.setEnabled(False)
        self.ui.actionExcel.setEnabled(False)
        self.ui.actionPDF_Aktar.setEnabled(False)
        self.ui.actionCSV_Aktar.setEnabled(False)
        self.ui.actionDisplay.setEnabled(False)
        self.ui.actionSil.setEnabled(False)
        self.ui.actionKayitli_Personeller.setEnabled(False)
        self.ui.action_On_Izleme.setEnabled(False)
        
    def OpenKayitliPersonel(self):
        self.kayitliPersoneller.showMaximized()
        self.kayitliPersoneller.activateWindow()

########################################################### messagebox işlemler #######################################################################

    def MesajBoxSoru(self, baslik, metin, evet, hayir):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        #msg.setStyleSheet("QLabel {min-width: 250px; min-height: 250px;}")
        mesajMetin  = '<pre style="font-size:12pt; color: #064e9a;">{}<figure>'.format(metin)
        msg.setWindowTitle(baslik)
        
        icon = ":/resim/kaynakjpg/Arthur-Dent-icon.png"
        pixmap = QPixmap(icon)
        msg.setIconPixmap(pixmap)
        #q_icon = QIcon(pixmap)
        #self.setWindowIcon(q_icon)
        
        msg.setBaseSize
        msg.setText(mesajMetin)
        msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        buttonY = msg.button(QMessageBox.Yes)
        buttonY.setText(evet)
        buttonN = msg.button(QMessageBox.No)
        buttonN.setText(hayir)
        msg.exec_()
        if msg.clickedButton() == buttonY:
            return evet
        
        if msg.clickedButton() == buttonN:
            return hayir
    
    def MesajBoxWarning(self, baslik, metin, ok, icon):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        mesajMetin  = '<pre style="font-size:12pt; color: #01040a;">{}<figure>'.format(metin)
        msg.setWindowTitle(baslik)

        pixmap = QPixmap(icon)
        msg.setIconPixmap(pixmap)
       
        msg.setBaseSize
        msg.setText(mesajMetin)
        msg.setStandardButtons(QMessageBox.Ok)
        buttonOk = msg.button(QMessageBox.Ok)
        buttonOk.setText(ok)
        msg.exec_()
    
#######################################################################################################################################################
