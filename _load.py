# encoding:utf-8
# Dosyadan yüklenen verileri tek seferde puantaj oluşturur. Veriler istenilen formatta olmalıdır.

############### İstenilen Formatlar:
# Seçilen dosya xls veya xlsx formatında olmalıdır
# dosyadan opsiyonel olarak en az 3, en fazla 5 kolon istenir ve buna göre processing işlemleri yapılır. 
# 3 kolon: adSoyad - TC - İşe Giriş Tarihi
# 4 kolon: ad - Soyad - TC - İşe Giriş Tarihi
# 5 kolon: ad - Soyad - TC - İşe Giriş Tarihi - İşten Ayrılış Tarihi 

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal
from _loadForm import Ui_LoadWindow
from _calendar import Takvim
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from pandas import offsets, date_range, to_datetime, DataFrame, unique, read_excel, NaT, isnull, Timestamp, DateOffset
from numpy import nan
from datetime import date
import re
from pathlib import Path


class LoadWindow(QMainWindow):
    signal = pyqtSignal(list)

    # parametreler
    objCalisma = 'X'
    objCalismaDisi = '-'
    objHaftaTatili = 'T'
    objResmiTatil = 'RS'
    objIseGirmedi = 'İŞE GİRMEDİ'
    objCikmis = 'ÇIKMIŞ'
    
    def __init__(self):
        super(LoadWindow, self).__init__()

        self.ui = Ui_LoadWindow()
        self.ui.setupUi(self)
        
        self.StatusTime = 1000
        self.df_ = DataFrame()

        #Combobox işlemler / current ve datalar
        self.GenelTatil = Takvim()
        self.Aylar =Takvim.Aylar()
        self.Gunler = Takvim.Gunler()
        self.yillar = Takvim.Yillar()
        self.ui.comboAyLoad.addItems(self.Aylar)
        self.ui.comboYilLoad.addItems(self.yillar)
        self.ui.comboYilLoad.setCurrentIndex(23)
        self.ui.comboTatilGunu_1Load.addItems(self.Gunler)
        self.ui.comboTatilGunu_2Load.addItems(self.Gunler)
        self.ui.comboTatilGunu_1Load.setCurrentIndex(0)
        self.ui.comboTatilGunu_2Load.setCurrentIndex(1)

        # signals & Slots
        self.ui.btnOpenLoad.clicked.connect(self.DosyaSec)
        self.ui.btnSaveLoad.clicked.connect(self.Processing)

############################################################# Dosya İşlemler #######################################################################

    def DosyaSec(self):
        dosya_yol, _  = QFileDialog.getOpenFileName(self, "Dosya Aç", "", "Excel (*.xls *.xlsx)")
        path = Path(dosya_yol)
        isim=path.name

        if dosya_yol:    
            df= read_excel(fr"{dosya_yol}",header=None)
            df = df.apply(lambda x: x.replace(r'^\s*$', NaT, regex=True) if x.dtype == "object" else x)
            df = df.apply(lambda x: x.replace(nan, NaT, regex=True) if x.dtype == "float64" else x)
            df = df.apply(lambda x: x.replace(nan, NaT, regex=True) if x.dtype == "float32" else x)
            df = df.apply(lambda x: x.replace(nan, NaT, regex=True) if x.dtype == "integer" else x)

            df.dropna(how='all',axis=1, inplace=True)
            df.dropna(how='all',axis=0, inplace=True)
            df=df.rename(index={j: i for i, j in enumerate(df.index)})

            try:
                self.ui.txtDosyaYolLoad.insert(isim)
                txt = "Hazır"
                self.BilgilerEkrani(isim, txt)
                self.df_ = df
            except:
                self.MesajBox()
                self.ui.txtDosyaYolLoad.clear()
        
    def Processing(self):
        if not self.df_.empty:

            veri = self.df_
            tc=[]
            adSoyad=[]
            ad=[]
            soyAd=[]
            GirisCikisT=[]
            girisT=[]
            cikisT=[]
            baslikkontrol = [p for p in veri.values[0] if isinstance(p, float) or isinstance(p, int)]
    
            if baslikkontrol!=[]:
                for i in veri.index:
                    for j in veri.values[i]:
                        if isinstance(j, float) or isinstance(j, int):
                            tc.append(j)
                        if isinstance(j, str):
                            adSoyad.append(j)
                        if isinstance(j, date):
                            GirisCikisT.append(j)
                
                if len(adSoyad)==len(tc):
                    for z in adSoyad:
                        if re.match(".+\s",z):
                            nesne1 = re.match(".+\s",z)
                            nesne1 = nesne1.group()
                            nesne1 = nesne1[:-1]
                            nesne2 = re.search("\s.+",z)
                            nesne2 = nesne2.group()
                            nesne2 = nesne2[1:]
                            if nesne1:
                                ad.append(nesne1)
                                soyAd.append(nesne2)
                        else:
                            ad.append(z)
                            soyAd.append(z)
                else:
                    for x in range(len(adSoyad)):
                        if x %2==0:
                            ad.append(adSoyad[x])
                        else:
                            soyAd.append(adSoyad[x])

                if len(GirisCikisT)==len(tc):
                    girisT=GirisCikisT
                    for q in range(len(girisT)):
                        cikisT.append(NaT)

                else:
                    for y in range(len(GirisCikisT)):
                        if y %2==0:
                            girisT.append(GirisCikisT[y])
                        else:
                            cikisT.append(GirisCikisT[y])
                                
                df1 = {'ad':ad, 'soyAd':soyAd, 'tc':tc, 'girisT':girisT, 'cikisT':cikisT}
                try:
                    sonVeri = DataFrame(df1)
                    return self.KayitleriYukle(sonVeri)
                except:
                    self.MesajBox()
                    self.ui.txtDosyaYolLoad.clear()
            
            else:
                veri=veri.drop([0,0])
                veri=veri.rename(index={j: i for i, j in enumerate(veri.index)})
                veri = veri.apply(lambda x: x.replace(r'^\s*$', NaT, regex=True) if x.dtype == "object" else x)
                veri = veri.apply(lambda x: x.replace(nan, NaT, regex=True) if x.dtype == "float64" else x)
                veri = veri.apply(lambda x: x.replace(nan, NaT, regex=True) if x.dtype == "float32" else x)
                veri = veri.apply(lambda x: x.replace(nan, NaT, regex=True) if x.dtype == "integer" else x)

                for i in veri.index:
                    for j in veri.values[i]:
                        if isinstance(j, float) or isinstance(j, int):
                            tc.append(j)
                        if isinstance(j, str):
                            adSoyad.append(j)
                        if isinstance(j, date):
                            GirisCikisT.append(j)
                            
                if len(adSoyad)==len(tc):
                    for z in adSoyad:
                        if re.match(".+\s",z):
                            nesne1 = re.match(".+\s",z)
                            nesne1 = nesne1.group()
                            nesne1 = nesne1[:-1]
                            nesne2 = re.search("\s.+",z)
                            nesne2 = nesne2.group()
                            nesne2 = nesne2[1:]
                            if nesne1:
                                ad.append(nesne1)
                                soyAd.append(nesne2)
                        else:
                            ad.append(z)
                            soyAd.append(z)
                else:
                    for x in range(len(adSoyad)):
                        if x %2==0:
                            ad.append(adSoyad[x])
                        else:
                            soyAd.append(adSoyad[x])

                if len(GirisCikisT)==len(tc):
                    girisT=GirisCikisT
                    for q in range(len(girisT)):
                        cikisT.append(NaT)

                else:
                    for y in range(len(GirisCikisT)):
                        if y %2==0:
                            girisT.append(GirisCikisT[y])
                        else:
                            cikisT.append(GirisCikisT[y])
            
                df1 = {'ad':ad, 'soyAd':soyAd, 'tc':tc, 'girisT':girisT, 'cikisT':cikisT}
                try:
                    sonVeri1 = DataFrame(df1)
                    return self.KayitleriYukle(sonVeri1)
                except:
                    self.MesajBox()
                    self.ui.txtDosyaYolLoad.clear()

    def KayitleriYukle(self, df):
        try:
        
            dataCikis = df['cikisT'].apply(lambda x: x.strftime('%d.%m.%Y') if not isnull(x) else '')
            
            tc=df['tc'].values
            ad=df['ad'].values
            soyAd=df['soyAd'].values
            girisT=df['girisT']
            cikisT=df['cikisT']

            personelKod = 'Plus_Satin_Al'
            unvan = 'Plus_Satin_Al'
            SGKFirma = self.ui.txtSGK_FirmaLoad.text()
            SGKSube = self.ui.txtSGK_SbLoad.text()
            sehir = self.ui.txtSehirLoad.text()
            lokasyon = self.ui.txtLokasYonLoad.text()
            departman = self.ui.txtDepartmanLoad.text()
            extcomun = self.ui.comboYilLoad.currentText()+"-"+self.ui.comboAyLoad.currentText()
            
            LoadList = []

            for q, w, x, y, z, p in zip(tc, ad, soyAd, girisT, cikisT, dataCikis):
                
                txtTc = str(int(q))
                txtAd = w
                txtSoyad = x
                dateGirisT = y.strftime('%d.%m.%Y')
                dateCikisT = p

                liste = [personelKod,txtAd,txtSoyad,txtTc,unvan,dateGirisT,dateCikisT,SGKFirma,SGKSube,sehir, lokasyon, departman, extcomun]
                
                liste = liste+self.PuantajOlusturLoad(y,z)
                LoadList += [liste]

            self.signal.emit(LoadList)
            txt1 = 'Dosyadaki veriler'
            txt2 = 'tabloya eklendi'
            self.BilgilerEkrani(txt1, txt2)
            self.ui.txtDosyaYolLoad.clear()
            self.df_=DataFrame()
        except:
            return

########################################################### puantaj işlemleri ######################################################################

    def PuantajOlusturLoad(self, ise_baslama, isten_ayrilis):
        
        puantaj = list([self.objCalisma]*len(self.SeciliDonemResmiTatillerIsGunleri()[2])) #tam ay X
        try:
            for i in self.SeciliDonemResmiTatillerIsGunleri()[0]:
                if len(self.SeciliDonemResmiTatillerIsGunleri()[0])==len(self.SeciliDonemResmiTatillerIsGunleri()[2]):
                    i=int(i.day)
                    puantaj[(i-1)]=self.objCalisma
                else:
                    i=int(i.day)
                    puantaj[(i-1)]=self.objHaftaTatili

            for s in self.SeciliDonemResmiTatillerIsGunleri()[1]:
                if s in self.SeciliDonemResmiTatillerIsGunleri()[2]:
                    s=int(s.day)
                    puantaj[(s-1)]=self.objResmiTatil


            if (self.GirisCikis(ise_baslama, isten_ayrilis)[0] in self.SeciliDonemResmiTatillerIsGunleri()[2]) and self.IseGirisData(ise_baslama) is not None:
                SaydirGirisAralik = self.IseGirisData(ise_baslama)[1].day-self.IseGirisData(ise_baslama)[0].day
                for g in range(SaydirGirisAralik):
                    puantaj[g]=self.objCalismaDisi
            
            if (self.GirisCikis(ise_baslama, isten_ayrilis)[1] in self.SeciliDonemResmiTatillerIsGunleri()[2]) and self.IstenCikisData(isten_ayrilis) is not None:
                SaydirCikisAralik = date_range(start=self.IstenCikisData(isten_ayrilis)[0],end=self.IstenCikisData(isten_ayrilis)[1],freq="D")
                for ck in SaydirCikisAralik:
                    ck=int(ck.day)
                    puantaj[(ck-1)]=self.objCalismaDisi
            
            if (self.GirisCikis(ise_baslama, isten_ayrilis)[0] > self.SeciliDonemResmiTatillerIsGunleri()[4]) and (self.GirisCikis(ise_baslama, isten_ayrilis)[0]+ DateOffset(1)) not in self.SeciliDonemResmiTatillerIsGunleri()[6]: #işe başlama > seçili dönemin başlangıcından
                puantaj = list([self.objIseGirmedi]*len(self.SeciliDonemResmiTatillerIsGunleri()[2]))
            
            if self.GirisCikis(ise_baslama, isten_ayrilis)[1] <= self.SeciliDonemResmiTatillerIsGunleri()[4] and self.GirisCikis(ise_baslama, isten_ayrilis)[0] not in self.SeciliDonemResmiTatillerIsGunleri()[6]: #işten ayrılış < seçili dönemin başlangıcından
                puantaj = list([self.objCikmis]*len(self.SeciliDonemResmiTatillerIsGunleri()[2]))
        
        except:
            baslik = 'FORMAT HATASI'
            metin = 'Girilen Format Geçerli Değil..!'
            ok = 'Tamam'
            icon = ":/resim/kaynakjpg/hitchhikeguidetogalaxy1_config.png"
            self.MesajBoxWarning(baslik, metin, ok, icon)
        
        return puantaj
    
    def SeciliDonemResmiTatillerIsGunleri(self):

        self.SeciliYil = self.ui.comboYilLoad.currentText()
        self.SeciliAyIndex = (self.ui.comboAyLoad.currentIndex()+1)
        
        formatt = Timestamp(self.SeciliYil+"-"+str(self.SeciliAyIndex)+"-01")
        tsSeciliDonemBitis = formatt+offsets.MonthEnd()
        tsSeciliDonemBaslangic = to_datetime(formatt,format="%d.%m.%Y")

        TamAyX = list(date_range(start=tsSeciliDonemBaslangic.date(), end=tsSeciliDonemBitis.date(),freq="D"))
        TamAyY = date_range(start=tsSeciliDonemBaslangic.date(), end=tsSeciliDonemBitis.date(),freq="D")

        GenelTatilGunleri = set(self.GenelTatil.holidays(start=tsSeciliDonemBaslangic, end=tsSeciliDonemBitis))
        GenelTatilGunleriTS = self.GenelTatil.holidays(start=tsSeciliDonemBaslangic, end=tsSeciliDonemBitis)
        
        HaftaTatilleri1=date_range(start=tsSeciliDonemBaslangic.date(), end=tsSeciliDonemBitis.date(), freq=self.HaftaTatilleri()[0]) 
        HaftaTatilleri2=date_range(start=tsSeciliDonemBaslangic.date(), end=tsSeciliDonemBitis.date(), freq=self.HaftaTatilleri()[1])
        HaftaTatilleri = HaftaTatilleri1.union(HaftaTatilleri2)
        
        return HaftaTatilleri, GenelTatilGunleri, TamAyX, GenelTatilGunleriTS, tsSeciliDonemBaslangic, tsSeciliDonemBitis, TamAyY
    
    def IseGirisData(self, ise_baslama):
        try:
            DateIseBaslamaTarihi = to_datetime(ise_baslama,format="%d.%m.%Y")
            # tsSeciliDonemBitis = DateIseBaslamaTarihi+offsets.MonthEnd()
            tsSeciliDonemBaslangic = DateIseBaslamaTarihi+offsets.MonthEnd(n=0)-offsets.MonthBegin(n=1)
        except:
            return

        if DateIseBaslamaTarihi not in self.SeciliDonemResmiTatillerIsGunleri()[2]:
            return
        elif DateIseBaslamaTarihi == tsSeciliDonemBaslangic:  
            return
        # elif DateIseBaslamaTarihi == tsSeciliDonemBitis: 
        #     return 
        else:
            return tsSeciliDonemBaslangic, DateIseBaslamaTarihi

    def GirisCikis(self, ise_baslama, isten_ayrilis):
        try:
            IseBaslamaTarihi = to_datetime(ise_baslama, format="%d.%m.%Y") - DateOffset(1)
            IstenAyrilisTarihi = to_datetime(isten_ayrilis, format="%d.%m.%Y") + DateOffset(1)
        except:
            IseBaslamaTarihi = to_datetime('01.01.2023', format="%d.%m.%Y") - DateOffset(1)
            IstenAyrilisTarihi = to_datetime('01.01.2023', format="%d.%m.%Y") + DateOffset(1)
            return IseBaslamaTarihi, IstenAyrilisTarihi

        return IseBaslamaTarihi, IstenAyrilisTarihi
       
    def IstenCikisData(self, isten_ayrilis):
        try:
            DateIstenAyrilisTarihi = to_datetime(isten_ayrilis, format="%d.%m.%Y")
            tsSeciliDonemBitis = DateIstenAyrilisTarihi+offsets.MonthEnd()
            # tsSeciliDonemBaslangic = DateIstenAyrilisTarihi+offsets.MonthEnd(n=0)-offsets.MonthBegin(n=1)
        except:
            return
        
        if DateIstenAyrilisTarihi not in self.SeciliDonemResmiTatillerIsGunleri()[2]: 
            return
        # elif DateIstenAyrilisTarihi == tsSeciliDonemBaslangic:  
        #     return
        elif DateIstenAyrilisTarihi == tsSeciliDonemBitis: 
            return 
        else:
            return DateIstenAyrilisTarihi+ DateOffset(1), tsSeciliDonemBitis, DateIstenAyrilisTarihi

    def HaftaTatilleri(self): #burada seçili dönemin varsa normal hafta tatilleri bilgisi çıkarılacak yoksa bütün günleri hafta tatili gibi sayacak
        Index = []
        Days = ['W-SAT', 'W-SUN', 'W-MON', 'W-TUE', 'W-WED', 'W-THU', 'W-FRI',"D"]

        if self.ui.comboTatilGunu_2Load.currentIndex()==7:
            for i in range(int(self.ui.comboTatilGunu_1Load.count())):
                if i==int(self.ui.comboTatilGunu_1Load.currentIndex()):
                    Index.append(Days[i])
                    Index.append(Days[i])

        elif self.ui.comboTatilGunu_1Load.currentIndex()==7:
            for j in range(int(self.ui.comboTatilGunu_2Load.count())):
                if j==int(self.ui.comboTatilGunu_2Load.currentIndex()):
                    Index.append(Days[j])
                    Index.append(Days[j])

        else:
            for k in range(int(self.ui.comboTatilGunu_1Load.count())):
                if k==int(self.ui.comboTatilGunu_1Load.currentIndex()):
                    Index.append(Days[k])
            
            for l in range(int(self.ui.comboTatilGunu_2Load.count())):
                if l==int(self.ui.comboTatilGunu_2Load.currentIndex()):
                    Index.append(Days[l])

        return Index

########################################################### events and status #######################################################################

    def BilgilerEkrani(self, secili1, secili2):
            self.ui.statusbar.showMessage('{} {}          {}'.format(secili1, secili2, 100*'/'), self.StatusTime)
            self.ui.statusbar.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";\n"
"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super(LoadWindow, self).keyPressEvent(event)

########################################################### _table gelen veriler ###################################################################

    def TabloyuYenile(self, df):
        # df = df.apply(lambda x: x.replace(nan, NaT, regex=True) if x.dtype == "float64" else x) #bunlar ne işe yarıyo aq
        # df = df.apply(lambda x: x.replace(nan, NaT, regex=True) if x.dtype == "float32" else x)
        # df = df.apply(lambda x: x.replace(nan, NaT, regex=True) if x.dtype == "integer" else x)
        
        dataCikis = df['İşten Ayrılış T.'].apply(lambda x: x if not isnull(x) else '')
        tc=df['T.C.'].values
        ad=df['Ad'].values
        soyAd=df['Soyad'].values
        girisT=df['İşe Başlama T.'].values
        cikisT=df['İşten Ayrılış T.'].values

        personelKod = df['Pers. Kod'].fillna(' ').values
        unvan = df['Unvan'].fillna(' ').values

        SGKFirma = df['SGK Firma'].fillna(' ').values
        SGKSube = df['SGK Şube'].fillna(' ').values
        sehir = df['Şehir'].fillna(' ').values
        lokasyon = df['Lokasyon'].fillna(' ').values
        departman = df['Departman'].fillna(' ').values

        extcomun = self.ui.comboYilLoad.currentText()+"-"+self.ui.comboAyLoad.currentText()
        
        LoadList = []

        for a, b, q, w, x, y, z, p, c, d, e, f, g in zip(personelKod, unvan, tc, ad, soyAd, girisT, cikisT, dataCikis, SGKFirma, SGKSube, sehir, lokasyon, departman):
            
            txtTc = str(q)
            txtAd = w
            txtSoyad = x
            dateGirisT = y
            dateCikisT = p

            personelKoD = str(a).strip()
            Unvan = str(b).strip()
            SGKFirmA = str(c).strip()
            SGKSubE = str(d).strip()
            sehiR = str(e).strip()
            lokasyoN = str(f).strip()
            departmaN = str(g).strip()

            liste = [personelKoD, txtAd, txtSoyad, txtTc, Unvan, dateGirisT, dateCikisT, SGKFirmA, SGKSubE, sehiR, lokasyoN, departmaN, extcomun]
            
            liste = liste+self.PuantajOlusturLoad(y,z)
            LoadList += [liste]
        self.signal.emit(LoadList)

########################################################### messagebox işlemler #######################################################################

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
    
    def MesajBox(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle('HATALI DOSYA...!')
        msg.setBaseSize
        metin = 'Dosyada Hatalı Veriler Var..\n\nVerilerinizi Aşağıdaki Detaylara Göre Girmelisiniz!'
        mesajMetin  = '<pre style="font-size:12pt; color: #01040a;">{}<figure>'.format(metin)
        metin2 = "Sadece aşağıdaki bilgileri giriniz: \nAd - Soyad - TC\nİşe Giriş Tarihi(Gün/Ay/Yıl Formatında)\nVarsa İşten Ayrılış Tarihi(Gün/Ay/Yıl Formatında)"
        icon = ':/resim/kaynakjpg/Jeltz-icon.png'
        pixmap = QPixmap(icon)
        msg.setIconPixmap(pixmap)
        msg.setText(mesajMetin)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDetailedText(metin2)
        msg.exec_()

#######################################################################################################################################################