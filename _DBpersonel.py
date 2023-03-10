# encoding:utf-8
# database kayıtlı verilerin gösterilmesi, değiştirilmesi, yeniden oluşturulması. 
# Database verilerine göre puantaj oluşturma. 

from PyQt5.QtWidgets import QMainWindow, QMessageBox, QListWidgetItem, QMenu, QTableWidgetItem
from PyQt5.QtCore import pyqtSignal, Qt, QDate, QRegExp, QTimer, QEvent
from PyQt5.QtGui import QRegExpValidator, QPixmap
from _calendar import Takvim
from _PersonelForm import Ui_PersonelWindow
from _preview import Preview
from contextlib import closing
from pandas import offsets, date_range, to_datetime, unique, DataFrame, DateOffset
from datetime import datetime as dt
from dateutil import relativedelta
import numpy as np
import re
import sqlite3
from pathlib import Path
import os

class KayitliPersonel(QMainWindow):
    signal = pyqtSignal(list)

    def __init__(self):
        super(KayitliPersonel, self).__init__()

        self.ui = Ui_PersonelWindow()
        self.ui.setupUi(self)

        self.preview = Preview()

        self.DBConnect() #database bağlantı
        self.PersonelListele() #database isim listesi

        self.StatusTime = 4000

        #Combobox işlemler / current ve datalar
        self.GenelTatil = Takvim()
        self.Aylar =Takvim.Aylar()
        self.Gunler = Takvim.Gunler()
        self.yillar = Takvim.Yillar()
        self.ui.comboKayitliPersAy.addItems(self.Aylar)
        self.ui.comboYilKayitliPers.addItems(self.yillar)
        self.ui.comboYilKayitliPers.setCurrentIndex(23)
        self.ui.comboTatilGunu_1KayitliPers.addItems(self.Gunler)
        self.ui.comboKayitliPersKayitli_2.addItems(self.Gunler)
        self.ui.comboTatilGunu_1KayitliPers.setCurrentIndex(0)
        self.ui.comboKayitliPersKayitli_2.setCurrentIndex(1)

        #Tc karakter standartlar
        valTC=QRegExpValidator(QRegExp(r'[0-9]+'))
        self.ui.txtKayitliPersTC.setValidator(valTC)
        
        #tarih karakter standartlar
        self.val=QRegExpValidator(QRegExp("(^(((0[1-9]|1[0-9]|2[0-8])[\/](0[1-9]|1[012]))|((29|30|31)[\/](0[13578]|1[02]))|((29|30)[\/](0[4,6,9]|11)))[\/](19|[2-9][0-9])\d\d$)|(^29[\/]02[\/](19|[2-9][0-9])(00|04|08|12|16|20|24|28|32|36|40|44|48|52|56|60|64|68|72|76|80|84|88|92|96)$)"))
        self.ui.dateKayitliPersIStenAyrilis.setValidator(self.val)
        self.vals = "(^(((0[1-9]|1[0-9]|2[0-8])[\/](0[1-9]|1[012]))|((29|30|31)[\/](0[13578]|1[02]))|((29|30)[\/](0[4,6,9]|11)))[\/](19|[2-9][0-9])\d\d$)|(^29[\/]02[\/](19|[2-9][0-9])(00|04|08|12|16|20|24|28|32|36|40|44|48|52|56|60|64|68|72|76|80|84|88|92|96)$)"

############################################################## Signals & Slots #####################################################################
        
        self.ui.listItemsKayitliPers.installEventFilter(self)
        self.ui.txtKayitliPersTC.installEventFilter(self)
        self.ui.listItemsKayitliPersIzinler.installEventFilter(self)

        self.preview.ui.btn_ExcelAktir.clicked.connect(self.ExcelAktar)
        self.ui.btnKayitliPersIzinListele.clicked.connect(self.IzinListesi)
        self.ui.btnKayitliPersPersonelListele.clicked.connect(self.PersonelListesi)
        self.ui.btnKayitliPersButunPersonelPuantajOlustur_2.clicked.connect(self.ButunPersoenlPuantaj)
        self.ui.btnKayitliPersSeciliPersonelPuantajOlustur.clicked.connect(self.SeciliPersonelPuantaj)
        self.ui.btnKayitliPersPersonelSil.clicked.connect(self.PersonelSil)
        self.ui.btnKayitliPersIzinSil.clicked.connect(self.IzinSil)
        self.ui.btnKayitliPersYeniKayiyOlustur.clicked.connect(self.DataBasePersonelEkle)
        self.ui.btnKayitliPersTemizle.clicked.connect(self.BilgileriSil)
        self.ui.txtKayitliPersTC.editingFinished.connect(self.TxtTcSignals)
        self.ui.btnKayitliPersGuncelle_Kayit.clicked.connect(self.PersonelBilgileriGuncelleVeKayit)
        self.ui.btnKayitliPersAdd.clicked.connect(self.IzinKayitKontrol)
        self.ui.listItemsKayitliPers.itemPressed.connect(self.PersonelBilgileriTextItem)
        self.ui.listItemsKayitliPers.itemPressed.connect(self.KalanIzin)
        self.ui.listItemsKayitliPers.itemPressed.connect(self.IzinBilgileriListItem)
        self.ui.listItemsKayitliPers.itemPressed.connect(self.KalanIzin)
        self.ui.dateKayitliPersIStenAyrilis.editingFinished.connect(self.IstenAyrilisSignals)
        self.ui.comboTatilGunu_1KayitliPers.currentIndexChanged['QString'].connect(self.KalanIzin)
        self.ui.comboKayitliPersKayitli_2.currentIndexChanged['QString'].connect(self.KalanIzin)

############################################################### database islemleri ##################################################################
        
    def PersonelListele(self): # 'personel' veri tabanındaki personellerin ad soyadları listeleniyor. data=Tc numaraları
        #currentIndex = self.ui.listItemsKayitliPersIzinler.currentRow()
        sql = 'Select Ad, Soyad, Tc FROM personel'
        sorgu = self.DBsorgu(sql)
        for i in sorgu:
            veri_ice = QListWidgetItem()
            veri_ice.setData(Qt.UserRole, i[2])
            veri_ice.setText(str(i[0])+' '+str(i[1])) 
            self.ui.listItemsKayitliPers.addItem(veri_ice) #insertItem
            self.ui.listItemsKayitliPers.sortItems(Qt.SortOrder.AscendingOrder)
            self.ui.listItemsKayitliPers.setCurrentRow(0)

    def PersonelBilgileriTextItem(self): #seçili personelin data bilgisi(TC) ile 'personel' veri tabanındaki Tclerin eşleşenlerin bütün itemleri
        if self.ui.listItemsKayitliPers.currentItem():
            dt = self.ui.listItemsKayitliPers.currentItem().data(Qt.UserRole)
        else:
            dt=None

        sql = 'Select * FROM personel'
        sorgu = self.DBsorgu(sql)
        for i in sorgu:
            if (dt == i[3]): # and (str(i[1])+' '+str(i[2]) == veri)
                self.ui.txtKayitliPersPersKod.setText(i[0])
                self.ui.txtKayitliPersAd.setText(i[1])
                self.ui.txtKayitliPersSoyad.setText(i[2])
                self.ui.txtKayitliPersTC.setText(str(i[3]))
                self.ui.txtKayitliPersUnvan.setText(str(i[4]))
                self.ui.dateKayitliPersIStenAyrilis.setText(str(i[6]))
                textBaslama = str(i[5]).split('.')
                self.ui.dateKayitliPersIseBaslama.setDate(QDate(int(textBaslama[2]), int(textBaslama[1]), int(textBaslama[0])))
                self.ui.txtKayitliPersSGK_Firma.setText(str(i[7]))
                self.ui.txtKayitliPersSGK_Sb.setText(str(i[8]))
                self.ui.txtKayitliPersSehir.setText(str(i[9]))
                self.ui.txtKayitliPersLokasYon.setText(str(i[10]))
                self.ui.txtKayitliPersDepartman.setText(str(i[11]))

    def DataBasePersonelEkle(self):
        personelKod = self.ui.txtKayitliPersPersKod.text()
        if not re.match('^\s', self.ui.txtKayitliPersAd.text()) and (self.ui.txtKayitliPersAd.text() !=""):
            ad = self.ui.txtKayitliPersAd.text()
            if ad.startswith('i'):
                ad = 'İ' + ad [1:]
            ad = ad.capitalize()
        else:
            baslik = 'İsim Eksik!'
            metin = 'Personel İsmi Giriniz..'
            ok = 'Ok.'
            icon = 'kaynakjpg/Jeltz-icon.png'
            self.MesajBoxWarning(baslik, metin, ok, icon)
            return
        
        if not re.match('^\s', self.ui.txtKayitliPersSoyad.text()) and (self.ui.txtKayitliPersSoyad.text() !=""):
            soyad = self.ui.txtKayitliPersSoyad.text().replace("i", "İ").upper()
        else:
            baslik = 'Soyad Eksik!'
            metin = 'Personel Soyad Giriniz..'
            ok = 'Ok.'
            icon = 'kaynakjpg/Jeltz-icon.png'
            self.MesajBoxWarning(baslik, metin, ok, icon)
            return
        
        if not re.match('^\s', self.ui.txtKayitliPersTC.text()) and (self.ui.txtKayitliPersTC.text() !="") and (len(self.ui.txtKayitliPersTC.text())==11):
            sqlTC = 'Select Tc FROM personel'
            sorguTc = self.DBsorgu(sqlTC)
            if sorguTc:
                for i in sorguTc:
                    if i[0] == int(self.ui.txtKayitliPersTC.text()):
                        baslik = 'Çift Kayıt'
                        metin = 'Aynı kişi için çift kayıt yapıyorsunuz'
                        ok = 'Ok.'
                        icon = 'kaynakjpg/Jeltz-icon.png'
                        self.MesajBoxWarning(baslik, metin, ok, icon)
                        self.BilgileriSil()
                        return
                        
                    else:
                        tc = int(self.ui.txtKayitliPersTC.text())
                # else:
                #     tc = int(self.ui.txtTC.text())
        else:
            baslik = 'TC No Eksik!'
            metin = '11 Haneli TC Numarası Giriniz..'
            ok = 'Ok.'
            icon = 'kaynakjpg/Jeltz-icon.png'
            self.MesajBoxWarning(baslik, metin, ok, icon)
            return

        tc = int(self.ui.txtKayitliPersTC.text())
        unvan = self.ui.txtKayitliPersUnvan.text()
        iseBaslamaTarihi = self.ui.dateKayitliPersIseBaslama.text()

        if 1 <= len(self.ui.dateKayitliPersIStenAyrilis.text()) < 10:
            baslik = 'Tarih Formatı Geçersiz'
            metin = 'İşten Ayrılış Tarihi Geçersiz'
            ok = 'Ok.'
            icon = 'kaynakjpg/Jeltz-icon.png'
            self.MesajBoxWarning(baslik, metin, ok, icon)
            return

        if self.ui.dateKayitliPersIStenAyrilis.text()=="02.01.1753" or self.ui.dateKayitliPersIStenAyrilis.text()=="2.01.1753" or self.ui.dateKayitliPersIStenAyrilis.text()=="02.1.1753" or self.ui.dateKayitliPersIStenAyrilis.text()=="2.1.1753":
            İstenAyrilisTarihi=""
        else:
            İstenAyrilisTarihi = self.ui.dateKayitliPersIStenAyrilis.text().strip()

        SGKFirma = self.ui.txtKayitliPersSGK_Firma.text()
        SGKSube = self.ui.txtKayitliPersSGK_Sb.text()
        sehir = self.ui.txtKayitliPersSehir.text()
        lokasyon = self.ui.txtKayitliPersLokasYon.text()
        departman = self.ui.txtKayitliPersDepartman.text()
      
        baslik = 'PERSONEL EKLE'
        metin = "{} {} İsimli Kişi Eklensin mi?".format(ad, soyad)
        evet = 'Evet'
        hayir = 'Hayır'
        result = self.MesajBoxSoru(baslik, metin, evet, hayir)
        if result == evet:
            sql = "insert into personel (PersKod, Ad, Soyad, Tc, Unvan, IseBaslamT, IstenAyrilisT, SGKFirma, SGKSube, Sehir, Lokasyon, Departman) values (?,?,?,?,?,?,?,?,?,?,?,?)"
            self.DBsorguArg(sql, personelKod, ad, soyad, tc, unvan, iseBaslamaTarihi, İstenAyrilisTarihi, SGKFirma, SGKSube, sehir, lokasyon, departman)
            self.ui.statusbar.showMessage('{} {} İsimli Personel Veritabanına Kayıt Edildi'.format(ad,soyad),self.StatusTime)
            self.ui.listItemsKayitliPers.clear()
            self.PersonelListele()
            self.PersonelBilgileriTextItem()

    def PersonelBilgileriGuncelleVeKayit(self): #Database verileri Günceller
        personelKod = self.ui.txtKayitliPersPersKod.text()

        if not re.match('^\s', self.ui.txtKayitliPersAd.text()) and (self.ui.txtKayitliPersAd.text() !=""):
            txtAd = self.ui.txtKayitliPersAd.text()
            if txtAd.startswith('i'):
                txtAd = 'İ' + txtAd [1:]
            txtAd = txtAd.capitalize()
        else:
            return
        
        if not re.match('^\s', self.ui.txtKayitliPersSoyad.text()) and (self.ui.txtKayitliPersSoyad.text() !=""):
            txtSoyad = self.ui.txtKayitliPersSoyad.text().replace("i", "İ").upper()
        else:
            return

        if self.ui.txtKayitliPersTC.text():
            txtTc = int(self.ui.txtKayitliPersTC.text())
        else:
            txtTc = self.ui.txtKayitliPersTC.text()

        unvan = self.ui.txtKayitliPersUnvan.text()
        dateGirisT = self.ui.dateKayitliPersIseBaslama.text()
        dateCikisT = self.ui.dateKayitliPersIStenAyrilis.text()

        if 1 <= len(dateCikisT) < 10:
            baslik = 'Tarih Formatı Geçersiz'
            metin = 'İşten Ayrılış Tarihi Geçersiz'
            ok = 'Ok.'
            icon = 'kaynakjpg/Jeltz-icon.png'
            self.MesajBoxWarning(baslik, metin, ok, icon)
            return
        
        SGKFirma = self.ui.txtKayitliPersSGK_Firma.text()
        SGKSube = self.ui.txtKayitliPersSGK_Sb.text()
        sehir = self.ui.txtKayitliPersSehir.text()
        lokasyon = self.ui.txtKayitliPersLokasYon.text()
        departman = self.ui.txtKayitliPersDepartman.text()

        liste = [personelKod, txtAd, txtSoyad, txtTc, unvan, dateGirisT, dateCikisT, SGKFirma, SGKSube, sehir, lokasyon, departman]

        sqlTc = 'Select Tc FROM personel'
        TcDataBase = self.DBsorgu(sqlTc)
        KayitliTcler = []
        for tc in TcDataBase:
            KayitliTcler.append(tc[0])

        sqlBilgiler = 'Select PersKod, Ad, Soyad, Tc, Unvan, IseBaslamT, IstenAyrilisT, SGKFirma, SGKSube, Sehir, Lokasyon, Departman, id FROM personel'
        sorguBilgiler = self.DBsorgu(sqlBilgiler)

        if self.ui.listItemsKayitliPers.currentItem() is not None:
            dt = self.ui.listItemsKayitliPers.currentItem().data(Qt.UserRole)
        else:
            return

        for i in sorguBilgiler:
            sql = i[:-1]
            fark = [l for l, s in zip(liste, sql) if l != s]
            
            if (not re.match('^\s', self.ui.txtKayitliPersTC.text())) and (self.ui.txtKayitliPersTC.text() !="") and (len(str(liste[3]))==11) and (dt == i[3] and fark !=[]):
                id = i[12]

                baslik = 'PERSONEL BİLGİLERİ GÜNCELLE'
                metin = "{} {}\n\nİsimli Personel Bilgileri Güncellensin mi? ".format(i[1], i[2])
                evet = 'Evet'
                hayir = 'Hayır'
                result = self.MesajBoxSoru(baslik, metin, evet, hayir)
                if result == evet:
                    if liste[0] != i[0]:
                        sqlUpdatePersonelKod = 'UPDATE personel SET PersKod=? WHERE id=?'
                        self.DBsorguArg(sqlUpdatePersonelKod, liste[0], id)

                        sqlUpdateizinlerKod  = 'UPDATE izinler SET PersKod=? WHERE Tc=?'
                        self.DBsorguArg(sqlUpdateizinlerKod, liste[0], i[3])
                        
                    if liste[1] != i[1]:
                        sqlUpdatepersonelAd = 'UPDATE personel SET Ad=? WHERE id=?'
                        self.DBsorguArg(sqlUpdatepersonelAd, liste[1], id)

                        sqlUpdateizinlerAd  = 'UPDATE izinler SET Ad=? WHERE Tc=?'
                        self.DBsorguArg(sqlUpdateizinlerAd, liste[1], i[3])

                    if liste[2] != i[2]:
                        sqlUpdatepersonelSoyAd = 'UPDATE personel SET Soyad=? WHERE id=?'
                        self.DBsorguArg(sqlUpdatepersonelSoyAd, liste[2], id)

                        sqlUpdateizinlerSoyAd  = 'UPDATE izinler SET Soyad=? WHERE Tc=?'
                        self.DBsorguArg(sqlUpdateizinlerSoyAd, liste[2], i[3])
                    
                    if int(liste[3]) != i[3]:
                        if int(liste[3]) not in KayitliTcler:
                            sqlUpdatepersonelTc = 'UPDATE personel SET Tc=? WHERE id=?'
                            self.DBsorguArg(sqlUpdatepersonelTc, liste[3], id)

                            sqlUpdateizinlerTc  = 'UPDATE izinler SET Tc=? WHERE Tc=?'
                            self.DBsorguArg(sqlUpdateizinlerTc, liste[3], i[3])
                        else:
                            baslik = 'Çift TC'
                            metin = 'Aynı TC için başka kayıt var'
                            ok = 'Ok.'
                            icon = 'kaynakjpg/Jeltz-icon.png'
                            self.MesajBoxWarning(baslik, metin, ok, icon)
                            return
                            
                    if liste[4] != i[4]:
                        sqlUpdatepersonelUnvan = 'UPDATE personel SET Unvan=? WHERE id=?'
                        self.DBsorguArg(sqlUpdatepersonelUnvan,liste[4], id)

                        sqlUpdateizinlerUnvan  = 'UPDATE izinler SET Unvan=? WHERE Tc=?'
                        self.DBsorguArg(sqlUpdateizinlerUnvan, liste[4], i[3])

                    if liste[5] != i[5]:
                        sqlUpdatepersonelIseBaslama = 'UPDATE personel SET IseBaslamT=? WHERE id=?'
                        self.DBsorguArg(sqlUpdatepersonelIseBaslama, liste[5], id)
                    
                    if liste[6] != i[6]:
                        sqlUpdatepersonelIstenAyrilis = 'UPDATE personel SET IstenAyrilisT=? WHERE id=?'
                        self.DBsorguArg(sqlUpdatepersonelIstenAyrilis, liste[6], id)

                    if liste[7] != i[7]:
                        sqlUpdatepersonelSGKFirma = 'UPDATE personel SET SGKFirma=? WHERE id=?'
                        self.DBsorguArg(sqlUpdatepersonelSGKFirma, liste[7], id)

                    if liste[8] != i[8]:
                        sqlUpdatepersonelSGKSube = 'UPDATE personel SET SGKSube=? WHERE id=?'
                        self.DBsorguArg(sqlUpdatepersonelSGKSube, liste[8], id)
                        
                    if liste[9] != i[9]:
                        sqlUpdatepersonelSehir = 'UPDATE personel SET Sehir=? WHERE id=?'
                        self.DBsorguArg(sqlUpdatepersonelSehir, liste[9], id)
                        
                    if liste[10] != i[10]:
                        sqlUpdatepersonelLokasyon = 'UPDATE personel SET Lokasyon=? WHERE id=?'
                        self.DBsorguArg(sqlUpdatepersonelLokasyon, liste[10], id)
                        
                    if liste[11] != i[11]:
                        sqlUpdatepersonelDepartman = 'UPDATE personel SET Departman=? WHERE id=?'
                        self.DBsorguArg(sqlUpdatepersonelDepartman, liste[11], id)

                    self.ui.listItemsKayitliPers.clear()
                    self.PersonelListele()
                    self.PersonelBilgileriTextItem()
                    baslik = 'SQL Kayıt Güncelleme'
                    metin = '{} {}\nisimli personelin kayıtları güncellendi.'.format(i[1], i[2])
                    ok = 'Tamam'
                    icon = ":/resim/kaynakjpg/hitchhikeguidetogalaxy1_config.png"
                    self.MesajBoxWarning(baslik, metin, ok, icon)

    def DataBasePersonelSil(self, arg):
        dt = arg
        sqlTC = 'Select Tc FROM personel'
        obj = self.DBsorgu(sqlTC)
        tc = dt
        if not re.match('^\s', self.ui.txtKayitliPersTC.text()) and (self.ui.txtKayitliPersTC.text() !="") and (len(self.ui.txtKayitliPersTC.text())==11):
            for i in obj:
                if (i[0] == int(float(self.ui.txtKayitliPersTC.text()))) and (dt == i[0]): #BURASI BAZEN HATA VERİYOR AQ
                    sqlPersonel = "Delete from personel where Tc = ?"
                    #self.islem.execute(sil, (tc,))
                    self.DBsorguArg(sqlPersonel, tc)
                    baslik = 'SQL Kayıt Silme'
                    metin = 'Personel silindi'
                    ok = 'Tamam'
                    icon = ":/resim/kaynakjpg/hitchhikeguidetogalaxy1_config.png"
                    self.MesajBoxWarning(baslik, metin, ok, icon)
                    self.ui.listItemsKayitliPers.clear()
                    self.BilgileriSil()
                    self.PersonelListele()
                    self.PersonelBilgileriTextItem()
                    IzinKontrol = self.SorguIzinTcKontrol(i[0])
                    if IzinKontrol != []:
                        baslik = 'PERSONEL İZİN SİLME'
                        metin = "Personelin İzinleri de Silinsin mi?  "
                        evet = 'Evet'
                        hayir = 'Hayır'
                        result = self.MesajBoxSoru(baslik, metin, evet, hayir)
                        if result == evet:
                            sqlIzin = "Delete from izinler where Tc = ?"
                            self.DBsorguArg(sqlIzin, tc)
                            baslik = 'SQL Kayıt Silme'
                            metin = 'Personelin izinleri silindi'
                            ok = 'Tamam'
                            icon = ":/resim/kaynakjpg/hitchhikeguidetogalaxy1_config.png"
                            self.MesajBoxWarning(baslik, metin, ok, icon)
                            self.ui.listItemsKayitliPersIzinler.clear()

                        else:
                            self.ui.listItemsKayitliPersIzinler.clear()

    def IzinBilgileriListItem(self): #seçili personelin data bilgisi(TC) ile 'izinler' veri tabanındaki Tclerin eşleşenlerin izin itemleri
        #veri = self.ui.listItemsKayitliPers.currentItem().text()
        if self.ui.listItemsKayitliPers.currentItem() is not None:
            dt = self.ui.listItemsKayitliPers.currentItem().data(Qt.UserRole)
        else:
            return
        
        sql = 'Select * FROM izinler'
        sorgu = self.DBsorgu(sql)
        self.ui.listItemsKayitliPersIzinler.clear()
        for i in sorgu:
            if dt == i[3]:
                currentIndex = self.ui.listItemsKayitliPersIzinler.currentRow()
                text = str(i[5])+"-"+str(i[6])+" "+ str(i[7])
                self.ui.listItemsKayitliPersIzinler.insertItem(currentIndex, text)

    def DataBaseIzinEkle(self, personelKod, ad, soyad, tc, unvan, IzinBaslaT, IzinBitisTarh, Izinturu):
        sqlTc = 'Select Tc FROM personel'
        obj = self.DBsorgu(sqlTc)
        trh = IzinBaslaT+"-"+IzinBitisTarh+" "+Izinturu
        if not re.match('^\s', self.ui.txtKayitliPersTC.text()) and (self.ui.txtKayitliPersTC.text() !="") and (len(self.ui.txtKayitliPersTC.text())==11):
            for i in obj:
                if i[0] == int(self.ui.txtKayitliPersTC.text()):
                    sql = "insert into izinler (PersKod, Ad, Soyad, Tc, Unvan, IzinBaslaT, IzinBitisTarh, IzinTuru, id ) values (?,?,?,?,?,?,?,?,?)"
                    self.DBsorguArg(sql, personelKod, ad, soyad, tc, unvan, IzinBaslaT, IzinBitisTarh, Izinturu, None)
                    baslik = 'SQL Kayıt Güncelleme'
                    metin = '{} {}\nisimli personele aşağıdaki izinler eklendi\n\n{}'.format(ad, soyad, trh)
                    ok = 'Tamam'
                    icon = ":/resim/kaynakjpg/hitchhikeguidetogalaxy1_config.png"
                    self.MesajBoxWarning(baslik, metin, ok, icon)
                    self.PersonelBilgileriTextItem()

    def DataBaseIzinSil(self, arg):
        seciliIzin = arg
        dt = self.ui.listItemsKayitliPers.currentItem().data(Qt.UserRole)

        tc = dt
        nesne1 = re.match(".+-",seciliIzin)
        nesne1 = nesne1.group()
        IzinBaslaT = nesne1[:-1]
        nesne2 = re.search("-.+\s",seciliIzin)
        nesne2 = nesne2.group()
        IzinBitisTarh = nesne2[1:-1]
        nesne3 = re.search("\s.+",seciliIzin)
        nesne3 = nesne3.group()
        Izinturu = nesne3[1:]
        
        sqlTc = 'Select Tc FROM personel'
        obj = self.DBsorgu(sqlTc)
        if not re.match('^\s', self.ui.txtKayitliPersTC.text()) and (self.ui.txtKayitliPersTC.text() !="") and (len(self.ui.txtKayitliPersTC.text())==11):
            for i in obj:
                if (i[0] == int(self.ui.txtKayitliPersTC.text())) and (dt == i[0]):
                    sql = "Delete from izinler where Tc = ? and IzinBaslaT=? and IzinBitisTarh=? and IzinTuru=?"
                    self.DBsorguArg(sql, tc, IzinBaslaT, IzinBitisTarh, Izinturu)
                    baslik = 'SQL Kayıt Silme'
                    metin = 'izinler silindi'
                    ok = 'Tamam'
                    icon = ":/resim/kaynakjpg/hitchhikeguidetogalaxy1_config.png"
                    self.MesajBoxWarning(baslik, metin, ok, icon)
                    self.PersonelBilgileriTextItem()
  
    def SorguIzinTcKontrol(self, arg):
        sorguTc = 'Select Tc FROM izinler'
        IzinliPersonelTc = []
        obj = self.DBsorgu(sorguTc)
        for i in obj:
            if int(i[0]) == arg:
                IzinliPersonelTc.append(i)
        return IzinliPersonelTc

    def DBConnect(self):
        home = str(Path.home())
        with closing(sqlite3.connect(home+"\\Personeller.db")) as con, con,  \
                closing(con.cursor()) as cur:
            try:
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

##############################################################  Events & Siglas #############################################################################

    def eventFilter(self, kaynak, aksiyon):
        if aksiyon.type() == QEvent.ContextMenu and kaynak is self.ui.listItemsKayitliPersIzinler:
            menu = QMenu()
            menu.addAction("İzin Sil       ", self.IzinSil)
            menu.exec_(aksiyon.globalPos())
           
            return True
    
        if aksiyon.type() == QEvent.ContextMenu and kaynak is self.ui.listItemsKayitliPers:
            menu = QMenu()
            menu.addAction("Personel Sil       ", self.PersonelSil)
            menu.exec_(aksiyon.globalPos())
           
            return True

        if self.ui.txtKayitliPersTC == kaynak and aksiyon.type() == QEvent.KeyPress:
            if aksiyon.key() == Qt.Key_Tab:
                QTimer.singleShot(0, self.evenTabTc)
        
        if self.ui.listItemsKayitliPersIzinler == kaynak and aksiyon.type() == QEvent.KeyPress:
            if aksiyon.key() == Qt.Key_Delete:
                QTimer.singleShot(0, self.IzinSil)

        if self.ui.listItemsKayitliPers == kaynak and aksiyon.type() == QEvent.KeyPress:
            if aksiyon.key() == Qt.Key_Delete:
                QTimer.singleShot(0, self.PersonelSil)
      
        return super().eventFilter(kaynak, aksiyon)
    
    def evenTabTc(self):
        self.BilgiGetir()
        self.IzinBilgiGetir()
        self.KalanIzin()

    def BilgiGetir(self):
        veri = self.ui.txtKayitliPersTC.text()
        if len(veri) != 11:
            baslik1 = 'TC Kimlik No Hatalı...!'
            metin1 = 'TC Kimlik Numarası 11 Haneli Olmalıdır...!'
            ok = 'Tamam'
            icon = ":/resim/kaynakjpg/Jeltz-icon.png"
            self.MesajBoxWarning(baslik1, metin1, ok, icon)
            
        sql = 'Select * FROM personel'
        sorguAll = self.DBsorgu(sql)
        for i in sorguAll:
            if (str(i[3]) == veri):
                self.ui.txtKayitliPersPersKod.setText(i[0])
                self.ui.txtKayitliPersAd.setText(i[1])
                self.ui.txtKayitliPersSoyad.setText(i[2])
                self.ui.txtKayitliPersTC.setText(str(i[3]))
                self.ui.txtKayitliPersUnvan.setText(str(i[4]))
                textBaslama = str(i[5]).split('.')
                self.ui.dateKayitliPersIseBaslama.setDate(QDate(int(textBaslama[2]), int(textBaslama[1]), int(textBaslama[0])))
                self.ui.dateKayitliPersIStenAyrilis.setText(str(i[6]))
                self.ui.txtKayitliPersSGK_Firma.setText(str(i[7]))
                self.ui.txtKayitliPersSGK_Sb.setText(str(i[8]))
                self.ui.txtKayitliPersSehir.setText(str(i[9]))
                self.ui.txtKayitliPersLokasYon.setText(str(i[10]))
                self.ui.txtKayitliPersDepartman.setText(str(i[11]))

    def IzinBilgiGetir(self):
        veri = self.ui.txtKayitliPersTC.text()
        sql = 'Select * FROM izinler'
        sorguIzin = self.DBsorgu(sql)
        self.ui.listItemsKayitliPersIzinler.clear()
        for i in sorguIzin:
            if (str(i[3]) == veri):
                veri_ice = QListWidgetItem()
                veri_ice.setData(Qt.UserRole, i[8])
                text = str(i[5])+"-"+str(i[6])+" "+ str(i[7])
                veri_ice.setText(text) 
                self.ui.listItemsKayitliPersIzinler.addItem(veri_ice) #insertItem

    def TxtTcSignals(self):
        dataTc = self.ui.txtKayitliPersTC.text()
        if len(dataTc) != 11:
            baslik1 = 'TC Kimlik No Hatalı...!'
            metin1 = 'TC Kimlik Numarası 11 Haneli Olmalıdır...!'
            ok = 'Tamam'
            icon = ":/resim/kaynakjpg/Jeltz-icon.png"
            self.MesajBoxWarning(baslik1, metin1, ok, icon)
            self.PersonelBilgileriTextItem()

    def IstenAyrilisSignals(self):
        dateF = self.ui.dateKayitliPersIStenAyrilis.text().replace("/", ".")
        self.ui.dateKayitliPersIStenAyrilis.setText(dateF)
        if self.ui.dateKayitliPersIStenAyrilis.text() ==" ":
            self.ui.dateKayitliPersIStenAyrilis.setText('')

        DateIseBaslamaTarihi = to_datetime(self.ui.dateKayitliPersIseBaslama.text(),format="%d.%m.%Y")
        DateIstenAyrilisTarihi = to_datetime(self.ui.dateKayitliPersIStenAyrilis.text(),format="%d.%m.%Y")
        if DateIstenAyrilisTarihi < DateIseBaslamaTarihi:
            baslik1 = 'YANLIŞ KAYIT...!'
            metin1 = 'İşe Giriş Tarihinden Önce Kayıt giremezsiniz..!'
            ok = 'Tamam'
            icon = ":/resim/kaynakjpg/Jeltz-icon.png"
            self.MesajBoxWarning(baslik1, metin1, ok, icon)
            self.ui.dateKayitliPersIStenAyrilis.clear()
            return

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super(KayitliPersonel, self).keyPressEvent(event)

    def KalanIzin(self):
        self.ui.txtKayitliPersKalanIzin.clear()
        self.ui.txtKayitliPersKidem.clear()

        vmatch = np.vectorize(lambda x: bool(re.match('^Y',x)))
        veri = self.ui.txtKayitliPersTC.text()
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
        HaftaTatilleri = [Days[self.ui.comboTatilGunu_1KayitliPers.currentIndex()]] + [Days[self.ui.comboKayitliPersKayitli_2.currentIndex()]]
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
               
        IseBaslamaTarihi = dt.strptime(self.ui.dateKayitliPersIseBaslama.text(),"%d.%m.%Y") #işe başlama tarihi date
        MinKidemTarihi = IseBaslamaTarihi + DateOffset(years=1) #1 yıllık kıdem - işe başlama tarihinden sonra yıl dönümü

        if len(self.ui.dateKayitliPersIStenAyrilis.text()) == 10:
            IstenAyrilisTari = dt.strptime(self.ui.dateKayitliPersIStenAyrilis.text(),"%d.%m.%Y")
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
                self.ui.txtKayitliPersKalanIzin.setText('{} Gün Yıllık İzin'.format(str(KalanYillikIizin)))
                self.ui.txtKayitliPersKidem.setText('{} Yıl {} Ay {} Gün'.format(KidemYil, KidemAy, KidemGun))
            
            elif 14>= KidemYil >=6:
                ikinciAsama = KidemYil - 5
                HakedilenYillik +=  (KidemYil * 14) + (ikinciAsama * 6)
                KalanYillikIizin = HakedilenYillik - KullanilanToplamYillikIzinGunleri
                self.ui.txtKayitliPersKalanIzin.setText('{} Gün Yıllık İzin'.format(str(KalanYillikIizin)))
                self.ui.txtKayitliPersKidem.setText('{} Yıl {} Ay {} Gün'.format(KidemYil, KidemAy, KidemGun))
            
            elif KidemYil >=15:
                ikinciAsama = KidemYil - 5
                ucuncuAsama = KidemYil - 14
                HakedilenYillik +=  (KidemYil * 14) + (ikinciAsama * 6) + (ucuncuAsama * 6)
                KalanYillikIizin = HakedilenYillik - KullanilanToplamYillikIzinGunleri
                self.ui.txtKayitliPersKalanIzin.setText('{} Gün Yıllık İzin'.format(str(KalanYillikIizin)))
                self.ui.txtKayitliPersKidem.setText('{} Yıl {} Ay {} Gün'.format(KidemYil, KidemAy, KidemGun))
            
        else:
            KalanYillikIizin = HakedilenYillik - KullanilanToplamYillikIzinGunleri
            self.ui.txtKayitliPersKalanIzin.setText('{} Gün Yıllık İzin'.format(str(KalanYillikIizin)))
            self.ui.txtKayitliPersKidem.setText('{} Yıl {} Ay {} Gün'.format(KidemYil, KidemAy, KidemGun))

##############################################################  Butonlar  #############################################################################
    
    def IzinEkle(self):
        currentIndex = self.ui.listItemsKayitliPersIzinler.currentRow()
        izinTuru = self.ui.txtKayitliPersIzinTuru.text()
        izinTuru = izinTuru.strip()
        izinTuru = izinTuru.replace("i", "İ").upper()
        text = self.ui.dateKayitliPersIzinBaslangic.text()+"-"+self.ui.dateKayitliPersIzinBitis.text()+" "+ str.upper(izinTuru)
        if izinTuru and text is not None:
            self.ui.listItemsKayitliPersIzinler.insertItem(currentIndex, text)

        personelKod = self.ui.txtKayitliPersPersKod.text()
        ad = self.ui.txtKayitliPersAd.text()
        if ad.startswith('i'):
            ad = 'İ' + ad [1:]
        ad = ad.capitalize()
        soyad = self.ui.txtKayitliPersSoyad.text().replace("i", "İ").upper()
        tc = self.ui.txtKayitliPersTC.text()
        unvan = self.ui.txtKayitliPersUnvan.text()
        IzinBaslaT = self.ui.dateKayitliPersIzinBaslangic.text()
        IzinBitisTarh = self.ui.dateKayitliPersIzinBitis.text()
        self.DataBaseIzinEkle(personelKod, ad, soyad, tc, unvan, IzinBaslaT, IzinBitisTarh, izinTuru) 

        self.KalanIzin()
        self.ui.listItemsKayitliPersIzinler.sortItems(Qt.SortOrder.AscendingOrder)
        self.ui.txtKayitliPersIzinTuru.clear()
        self.ui.statusbar.showMessage("{}-{} tarihleri arasına {} eklendi".format(self.ui.dateKayitliPersIzinBaslangic.text(),self.ui.dateKayitliPersIzinBitis.text(),str.upper(izinTuru)), self.StatusTime)
        self.ui.statusbar.setStyleSheet("color:rgb(0,0,255)")
    
    def IzinSil(self):
        index = self.ui.listItemsKayitliPersIzinler.currentRow()
        item = self.ui.listItemsKayitliPersIzinler.item(index)
        if not re.match('^\s', self.ui.txtKayitliPersTC.text()) and (self.ui.txtKayitliPersTC.text() !="") and (len(self.ui.txtKayitliPersTC.text())==11):

            if item is None:
                return

            baslik = 'İZİN SİLME'
            metin = item.text() + " Tarih Aralığı İzinler Silinsin mi?  "
            evet = 'Evet'
            hayir = 'Hayır'
            result = self.MesajBoxSoru(baslik, metin, evet, hayir)
            if result == evet:
                item = self.ui.listItemsKayitliPersIzinler.takeItem(index)
                seciliIzin = item.text()
                self.DataBaseIzinSil(seciliIzin)
                del item
                
                self.KalanIzin()
                self.ui.statusbar.showMessage("Seçili İzin Silindi", self.StatusTime)
                self.ui.statusbar.setStyleSheet("color:rgb(255,0,0)")
        else:
            baslik = 'PERSONEL SEÇİLİ DEĞİL'
            metin = 'Personel Seçin'
            ok = 'Tamam'
            icon = ":/resim/kaynakjpg/hitchhikeguidetogalaxy1_help.png"
            self.MesajBoxWarning(baslik, metin, ok, icon)
            return

    def PersonelSil(self):
        
        index = self.ui.listItemsKayitliPers.currentRow()
        item = self.ui.listItemsKayitliPers.item(index)
        if not re.match('^\s', self.ui.txtKayitliPersTC.text()) and (self.ui.txtKayitliPersTC.text() !="") and (len(self.ui.txtKayitliPersTC.text())==11):
            
            if item is None:
                return

            baslik = 'PERSONEL SİLME'
            metin = item.text() + " İsimli Personel Silinsin mi?  "
            evet = 'Evet'
            hayir = 'Hayır'
            result = self.MesajBoxSoru(baslik, metin, evet, hayir)
            if result == evet:
                item = self.ui.listItemsKayitliPers.takeItem(index)
                data = item.data(Qt.UserRole)
                self.DataBasePersonelSil(data)
                del item
                
                self.ui.statusbar.showMessage("Seçili Personel Silindi", self.StatusTime)
                self.ui.statusbar.setStyleSheet("color:rgb(255,0,0)")
            if result == hayir:
                return
        
        else:
            baslik = 'PERSONEL SEÇİLİ DEĞİL'
            metin = 'Personel Seçin'
            ok = 'Tamam'
            icon = ":/resim/kaynakjpg/hitchhikeguidetogalaxy1_help.png"
            self.MesajBoxWarning(baslik, metin, ok, icon)
            return

    def SeciliPersonelPuantaj(self):
        if self.ui.listItemsKayitliPers.currentItem() is not None:
            dt = self.ui.listItemsKayitliPers.currentItem().data(Qt.UserRole)
        else:
            return
        sql = 'Select * FROM personel where Tc = ?'
        db = self.DBsorguArg(sql, dt)
        ay = self.ui.comboKayitliPersAy.currentIndex()
        yil = self.ui.comboYilKayitliPers.currentIndex()
        tatil1 = self.ui.comboTatilGunu_1KayitliPers.currentIndex()
        tatil2 = self.ui.comboKayitliPersKayitli_2.currentIndex()
        donem = self.ui.comboYilKayitliPers.currentText()+"-"+self.ui.comboKayitliPersAy.currentText()

        db = list(db[0][:-1])
        db.append(donem)
        params = [ay, yil, tatil1, tatil2]
        LoadList = [db,params]

        self.signal.emit(LoadList)

    def ButunPersoenlPuantaj(self):
        if self.ui.listItemsKayitliPers.currentItem() is not None:
            dt = self.ui.listItemsKayitliPers.currentItem().data(Qt.UserRole)
        else:
            return
        
        persSayi = self.ui.listItemsKayitliPers.count()
        baslik = 'BÜTÜN PERSONEL PUANTAJ'
        metin = "{} Kişinin Puantajı Tek Tek Oluşturulacak\nDevam Edilsin mi?".format(str(persSayi))
        evet = 'Evet'
        hayir = 'Hayır'
        result = self.MesajBoxSoru(baslik, metin, evet, hayir)
        if result == evet:
            sql = 'Select * FROM personel'
            db = list(self.DBsorgu(sql))
            ay = self.ui.comboKayitliPersAy.currentIndex()
            yil = self.ui.comboYilKayitliPers.currentIndex()
            tatil1 = self.ui.comboTatilGunu_1KayitliPers.currentIndex()
            tatil2 = self.ui.comboKayitliPersKayitli_2.currentIndex()
            donem = self.ui.comboYilKayitliPers.currentText()+"-"+self.ui.comboKayitliPersAy.currentText()
            dbAll = []
            for i in db:
                tp = list(i)
                tp[12]=donem
                li = tuple(tp)
                dbAll.append(li)
            
            params = [ay, yil, tatil1, tatil2]
            LoadList = [dbAll,params]

            self.signal.emit(LoadList)

        else:
            return
   
    def BilgileriSil(self):

        self.ui.txtKayitliPersPersKod.clear()
        self.ui.txtKayitliPersAd.clear()
        self.ui.txtKayitliPersSoyad.clear()
        self.ui.txtKayitliPersTC.clear()
        self.ui.txtKayitliPersUnvan.clear()
        self.ui.dateKayitliPersIStenAyrilis.clear()
        self.ui.dateKayitliPersIseBaslama.setDate(QDate(1, 1, 2023))
        self.ui.txtKayitliPersSGK_Firma.clear()
        self.ui.txtKayitliPersSGK_Sb.clear()
        self.ui.txtKayitliPersSehir.clear()
        self.ui.txtKayitliPersLokasYon.clear()
        self.ui.txtKayitliPersDepartman.clear()

    def PersonelListesi(self):
        rowCount = [self.ui.listItemsKayitliPers.item(x).text() for x in range(self.ui.listItemsKayitliPers.count())]
        if len(rowCount) > 0:
            while (self.preview.ui.tableProductsPreview.rowCount() > 0):
                    self.preview.ui.tableProductsPreview.removeRow(0)

            basliklar = ['Pers. Kod','Ad','Soyad','T.C.', 'Unvan','İşe Başlama T.','İşten Ayrılış T.',
        'SGK Firma','SGK Şube','Şehir','Lokasyon','Departman','id']
            
            self.preview.ui.tableProductsPreview.setColumnCount(len(basliklar))
            self.preview.ui.tableProductsPreview.setHorizontalHeaderLabels(basliklar)
            
            ColumnWidth = [100,200,200,125,150,120,120,150,150,150,150,150,50]
            for index, width in enumerate(ColumnWidth):
                self.preview.ui.tableProductsPreview.setColumnWidth(index,width)
            
            sql = 'Select * FROM personel'
            data = self.DBsorgu(sql)
            for row_number, row_data in enumerate(data):
                self.preview.ui.tableProductsPreview.insertRow(row_number)

                for column_number, data in enumerate(row_data):
                    self.preview.ui.tableProductsPreview.setItem(row_number, column_number, QTableWidgetItem(str(data)))

            self.preview.showMaximized()
            self.preview.activateWindow()
  
        else:
            return

    def IzinListesi(self):
        sql = 'Select * FROM izinler'
        data = self.DBsorgu(sql)
        if data:
            while (self.preview.ui.tableProductsPreview.rowCount() > 0):
                    self.preview.ui.tableProductsPreview.removeRow(0)

            basliklar = ['Pers. Kod','Ad','Soyad','T.C.','Unvan','İzin Baş. T.','İzin Bitiş T.','İzin Türü','id']
            
            self.preview.ui.tableProductsPreview.setColumnCount(len(basliklar))
            self.preview.ui.tableProductsPreview.setHorizontalHeaderLabels(basliklar)
            
            ColumnWidth = [100,200,200,125,200,120,200,50]
            for index, width in enumerate(ColumnWidth):
                self.preview.ui.tableProductsPreview.setColumnWidth(index,width)
            
            
            for row_number, row_data in enumerate(data):
                self.preview.ui.tableProductsPreview.insertRow(row_number)

                for column_number, data in enumerate(row_data):
                    self.preview.ui.tableProductsPreview.setItem(row_number, column_number, QTableWidgetItem(str(data)))

            self.preview.showMaximized()
            self.preview.activateWindow()

        else:
            return

    def ExcelAktar(self):
        rowCount = self.preview.ui.tableProductsPreview.rowCount()
        if rowCount > 0:
            baslik = 'Excel Dosyası'
            metin = 'Tablodaki Veriler Excele aktarılsın mı?'
            evet = 'Evet'
            hayir = 'Hayır'
            result = self.MesajBoxSoru(baslik, metin, evet, hayir)
            if result == evet:
                df = self.TablodakiVeriler()
                path = os.path.join(os.path.expanduser("~"), "Desktop", "Data.xlsx")
                df.to_excel(path, index=False)
                baslik = 'EXCEL DOSYASI'
                metin = 'Data.xlsx Masaüstünde Oluşturuldu'
                ok = 'Ok.'
                icon = ":/resim/kaynakjpg/hitchhikeguidetogalaxy1_config.png"
                self.MesajBoxWarning(baslik, metin, ok, icon)
        
        else:
            return

##############################################################  Metot Etkileşimleri  ################################################################

    def IzinKayitKontrol(self):
        izinTuru = self.ui.txtKayitliPersIzinTuru.text()

        if 1 <= len(self.ui.dateKayitliPersIStenAyrilis.text()) < 10:
            baslik = 'Tarih Formatı Geçersiz'
            metin = 'İşten Ayrılış Tarihi Geçersiz'
            ok = 'Ok.'
            icon = 'kaynakjpg/Jeltz-icon.png'
            self.MesajBoxWarning(baslik, metin, ok, icon)
            return

        if self.ui.dateKayitliPersIStenAyrilis.text() == "" or self.ui.dateKayitliPersIStenAyrilis.text() == " ":
            bosFormat = "02.01.1753"
        else:
            bosFormat = self.ui.dateKayitliPersIStenAyrilis.text().strip()

        if not re.match('^\s', izinTuru) and izinTuru !="": 
            
            for x,y in zip(self.KayitliIzinSlicing()[0], self.KayitliIzinSlicing()[1]):
                start = to_datetime(x,format="%d.%m.%Y")
                end = to_datetime(y,format="%d.%m.%Y")
                KayitliIzinKapsamiGunleri = date_range(start=start.date(), end=end.date(),freq="D")
                
                for z in KayitliIzinKapsamiGunleri:
                    if z in self.GirilenIzinDatalar()[2]:
                        baslik1 = 'ÇİFT KAYIT...!'
                        metin1 = 'Girdiğiniz Tarih Aralığında Başka Kayıt Var...!'
                        ok = 'Tamam'
                        icon = ":/resim/kaynakjpg/Jeltz-icon.png"
                        self.MesajBoxWarning(baslik1, metin1, ok, icon)
                        return 
            
            if self.GirilenIzinDatalar()[1] < self.GirilenIzinDatalar()[0]:
                baslik1 = 'YANLIŞ KAYIT...!'
                metin1 = 'Bitiş Tarihi Başlangıç Tarihinden Küçük...!'
                ok = 'Tamam'
                icon = ":/resim/kaynakjpg/Jeltz-icon.png"
                self.MesajBoxWarning(baslik1, metin1, ok, icon)
                return
            
            DateIseBaslamaTarihi = to_datetime(self.ui.dateKayitliPersIseBaslama.text(),format="%d.%m.%Y")
            DateIstenAyrilisTarihi = to_datetime(bosFormat,format="%d.%m.%Y")
            baslama = (DateIseBaslamaTarihi - offsets.Day(1))
            bitis = (DateIstenAyrilisTarihi + offsets.Day(1))
            for gunler in  self.GirilenIzinDatalar()[2]:
                if gunler <= baslama:
                    baslik1 = 'YANLIŞ KAYIT...!'
                    metin1 = 'İşe Giriş Tarihinden Önce Kayıt giremezsiniz..!'
                    ok = 'Tamam'
                    icon = ":/resim/kaynakjpg/Jeltz-icon.png"
                    self.MesajBoxWarning(baslik1, metin1, ok, icon)
                    return

                if (not bosFormat in {"02.01.1753","2.01.1753","02.1.1753","2.1.1753",""," "}) and gunler >= bitis:
                    baslik1 = 'YANLIŞ KAYIT...!'
                    metin1 = 'İşten Ayrılış Tarihinden sonra Kayıt giremezsiniz..!'
                    ok = 'Tamam'
                    icon = ":/resim/kaynakjpg/Jeltz-icon.png"
                    self.MesajBoxWarning(baslik1, metin1, ok, icon)
                    return
                
            else:
                self.IzinEkle()
    
    def GirilenIzinDatalar(self):
        dateIzinBaslangic = self.ui.dateKayitliPersIzinBaslangic.text()
        dateIzinBitis = self.ui.dateKayitliPersIzinBitis.text()
        GirilendateBaslangic = to_datetime(dateIzinBaslangic,format="%d.%m.%Y")
        GirilendateBitis = to_datetime(dateIzinBitis,format="%d.%m.%Y")
        GirilenIzinKapsamiGunleri = date_range(start=GirilendateBaslangic.date(), end=GirilendateBitis.date(),freq="D")
        
        return GirilendateBaslangic, GirilendateBitis, GirilenIzinKapsamiGunleri
    
    def KayitliIzinSlicing(self):
        GeciciKayitlar = [self.ui.listItemsKayitliPersIzinler.item(x).text() for x in range(self.ui.listItemsKayitliPersIzinler.count())]
        KayitliIzinTurleri = []
        KayitliIzinBaslamaTarihleri = []
        KayitliIzinBitisTarihleri = []
        KayitliIzinKapsamlari = []
        for i in GeciciKayitlar:
            nesne1 = re.match(".+-",i)
            nesne1 = nesne1.group()
            nesne1 = nesne1[:-1]
            nesne2 = re.search("-.+\s",i)
            nesne2 = nesne2.group()
            nesne2 = nesne2[1:-1]
            nesne3 = re.search("\s.+",i)
            nesne3 = nesne3.group()
            nesne3 = nesne3[1:]
            nesne4 = re.match(".+\s",i)
            nesne4 = nesne4.group()
            nesne4 = nesne4[:-1]
            if nesne3:
                KayitliIzinBaslamaTarihleri.append(nesne1)
                KayitliIzinBitisTarihleri.append(nesne2)
                KayitliIzinTurleri.append(nesne3)
                KayitliIzinKapsamlari.append(nesne4)

        return KayitliIzinBaslamaTarihleri, KayitliIzinBitisTarihleri, KayitliIzinTurleri, KayitliIzinKapsamlari
    
    def TablodakiVeriler(self):
        basliklar = []
        
        for i in range(self.preview.ui.tableProductsPreview.model().columnCount()):
            basliklar.append(self.preview.ui.tableProductsPreview.horizontalHeaderItem(i).text())
        
        df = DataFrame(columns=basliklar)

        for j in range(self.preview.ui.tableProductsPreview.rowCount()):
            for clm in range(self.preview.ui.tableProductsPreview.columnCount()):
                obj = self.preview.ui.tableProductsPreview.item(j,clm)
                if obj is not None and obj.text() != '':
                    df.at[j, basliklar[clm]] = self.preview.ui.tableProductsPreview.item(j, clm).text()
        return df

############################################################### messagebox işlemler #################################################################

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
        
#######################################################################################################################################################