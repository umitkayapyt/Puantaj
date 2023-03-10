# encoding:utf-8
# izin, tatil, resmi tatil, giriş-çıkış durumlarına göre puantaj oluşturma, denetleme merkezi

from pandas import Timestamp, offsets, date_range, to_datetime, DateOffset
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import  QPixmap
from _calendar import Takvim
#from _Param import Param
import re
import locale
locale.setlocale(locale.LC_TIME, "tr")

class Puantaj:
    objCalisma = 'X'
    objCalismaDisi = '-'
    objHaftaTatili = 'T'
    objResmiTatil = 'RS'
    objIseGirmedi = 'İŞE GİRMEDİ'
    objCikmis = 'ÇIKMIŞ'

    def __init__(self, dateIseBaslama, dateIStenAyrilis, GeciciKayitlar, dateIzinBaslangic, dateIzinBitis,
    ComboTatil1Current, ComboTatil2Current, ComboTatil1Count, ComboTatil2Count, SeciliYil, SeciliAyIndex):

        self.dateIseBaslama = dateIseBaslama
        self.dateIStenAyrilis = dateIStenAyrilis
        self.GeciciKayitlar = GeciciKayitlar
        self.dateIzinBaslangic = dateIzinBaslangic
        self.dateIzinBitis = dateIzinBitis
        self.ComboTatil1Current = ComboTatil1Current
        self.ComboTatil2Current = ComboTatil2Current
        self.ComboTatil1Count = ComboTatil1Count
        self.ComboTatil2Count = ComboTatil2Count
        self.SeciliYil = SeciliYil
        self.SeciliAyIndex = SeciliAyIndex

        self.GenelTatil = Takvim()

 
    def IseGirisData(self):
        DateIseBaslamaTarihi = to_datetime(self.dateIseBaslama,format="%d.%m.%Y")
        # tsSeciliDonemBitis = DateIseBaslamaTarihi+offsets.MonthEnd()
        tsSeciliDonemBaslangic = DateIseBaslamaTarihi+offsets.MonthEnd(n=0)-offsets.MonthBegin(n=1)

        if DateIseBaslamaTarihi not in self.SeciliDonemResmiTatillerIsGunleri()[2]:
            return
        elif DateIseBaslamaTarihi == tsSeciliDonemBaslangic:  
            return
        # elif DateIseBaslamaTarihi == tsSeciliDonemBitis: 
        #     return 
        else:
            return tsSeciliDonemBaslangic, DateIseBaslamaTarihi

    def GirisCikis(self):
        IseBaslamaTarihi = to_datetime(self.dateIseBaslama, format="%d.%m.%Y") - DateOffset(1)
        if self.dateIStenAyrilis == "" or self.dateIStenAyrilis == " ":
            IstenAyrilisTarihi = "02.01.1753"
        else:
            IstenAyrilisTarihi = to_datetime(self.dateIStenAyrilis, format="%d.%m.%Y") + DateOffset(1)

        return IseBaslamaTarihi, IstenAyrilisTarihi
       
    def IstenCikisData(self):
        DateIstenAyrilisTarihi = to_datetime(self.dateIStenAyrilis, format="%d.%m.%Y")
        tsSeciliDonemBitis = DateIstenAyrilisTarihi+offsets.MonthEnd()
        # tsSeciliDonemBaslangic = DateIstenAyrilisTarihi+offsets.MonthEnd(n=0)-offsets.MonthBegin(n=1)

        if DateIstenAyrilisTarihi not in self.SeciliDonemResmiTatillerIsGunleri()[2]: 
            return
        # elif DateIstenAyrilisTarihi == tsSeciliDonemBaslangic:  
        #     return
        elif DateIstenAyrilisTarihi == tsSeciliDonemBitis: 
            return 
        else:
            return DateIstenAyrilisTarihi+ DateOffset(1), tsSeciliDonemBitis, DateIstenAyrilisTarihi

    def KayitliIzinSlicing(self):
        KayitliIzinTurleri = []
        KayitliIzinBaslamaTarihleri = []
        KayitliIzinBitisTarihleri = []
        KayitliIzinKapsamlari = []
        for i in self.GeciciKayitlar:
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

    def GirilenIzinDatalar(self):
        GirilendateBaslangic = to_datetime(self.dateIzinBaslangic,format="%d.%m.%Y")
        GirilendateBitis = to_datetime(self.dateIzinBitis,format="%d.%m.%Y")
        GirilenIzinKapsamiGunleri = date_range(start=GirilendateBaslangic.date(), end=GirilendateBitis.date(),freq="D")

        return GirilendateBaslangic, GirilendateBitis, GirilenIzinKapsamiGunleri

    def HaftaTatilleri(self): #burada seçili dönemin varsa normal hafta tatilleri bilgisi çıkarılacak yoksa bütün günleri hafta tatili gibi sayacak
        Index = []
        Days = ['W-SAT', 'W-SUN', 'W-MON', 'W-TUE', 'W-WED', 'W-THU', 'W-FRI',"D"]

        if self.ComboTatil2Current == 7:
            for i in range(int(self.ComboTatil1Count)):
                if i==int(self.ComboTatil1Current):
                    Index.append(Days[i])
                    Index.append(Days[i])

        elif self.ComboTatil1Current==7:
            for j in range(int(self.ComboTatil2Count)):
                if j==int(self.ComboTatil2Current):
                    Index.append(Days[j])
                    Index.append(Days[j])

        else:
            for k in range(int(self.ComboTatil1Count)):
                if k==int(self.ComboTatil1Current):
                    Index.append(Days[k])
            
            for l in range(int(self.ComboTatil2Count)):
                if l==int(self.ComboTatil2Current):
                    Index.append(Days[l])

        return Index

    def HaftaTatilleriNormal(self): #burada seçili dönemin varsa normal hafta tatilleri bilgisi çıkarılacak yoksa boş index verecek
        
        formatt = Timestamp(self.SeciliYil+"-"+str(self.SeciliAyIndex)+"-01")
        tsSeciliDonemBitis = formatt+offsets.MonthEnd()
        tsSeciliDonemBaslangic = to_datetime(formatt,format="%d.%m.%Y")
        Days = ['W-SAT', 'W-SUN', 'W-MON', 'W-TUE', 'W-WED', 'W-THU', 'W-FRI']
        HaftaTatilleri = []

        if self.ComboTatil1Current == 7 and self.ComboTatil2Current !=7:
            for i in range(int(self.ComboTatil2Count)):
                if i==int(self.ComboTatil2Current):
                    ilkKolonTatilGunleri=date_range(start=tsSeciliDonemBaslangic.date(), end=tsSeciliDonemBitis.date(), freq=Days[i])
                    return ilkKolonTatilGunleri

        elif self.ComboTatil2Current == 7 and self.ComboTatil1Current != 7:
            for j in range(int(self.ComboTatil1Count)):
                if j==int(self.ComboTatil1Current):
                    ikinciKolonTatilGunleri=date_range(start=tsSeciliDonemBaslangic.date(), end=tsSeciliDonemBitis.date(), freq=Days[j])
                    return ikinciKolonTatilGunleri

        elif self.ComboTatil1Current != 7 and self.ComboTatil2Current != 7:
             for x in range(int(self.ComboTatil1Count)):
                y=int(self.ComboTatil1Current)
                KolonIlk = date_range(start=tsSeciliDonemBaslangic.date(), end=tsSeciliDonemBitis.date(), freq=Days[y])
                z=int(self.ComboTatil2Current)
                KolonIki = date_range(start=tsSeciliDonemBaslangic.date(), end=tsSeciliDonemBitis.date(), freq=Days[z])
                KolonCift = KolonIlk.union(KolonIki)
                return KolonCift

        elif self.ComboTatil1Current == 7 and self.ComboTatil2Current == 7:
            return HaftaTatilleri
        
    def SeciliDonemResmiTatillerIsGunleri(self):
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

    def PuantajOlustur(self):
        
        puantaj = list([self.objCalisma]*len(self.SeciliDonemResmiTatillerIsGunleri()[2])) #tam ay X
        
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

        box = QMessageBox()
        box.setIcon(QMessageBox.Question)
        icon = ":/resim/kaynakjpg/Arthur-Dent-icon.png"
        pixmap = QPixmap(icon)
        box.setIconPixmap(pixmap)

        if self.GeciciKayitlar is not None:
            for start, end, tur in zip(self.KayitliIzinSlicing()[0],self.KayitliIzinSlicing()[1],self.KayitliIzinSlicing()[2]):
                start = to_datetime(start,format="%d.%m.%Y")
                end = to_datetime(end,format="%d.%m.%Y")
                SiraliGunler = date_range(start=start.date(),end=end.date(),freq="D") #izin kapsam günleri sıralı olarak
                farklar = [i for i in SiraliGunler if i not in self.SeciliDonemResmiTatillerIsGunleri()[2]] #diğer aya atlaması halinde farklar
                
                Ht = [i for i in SiraliGunler if i in self.SeciliDonemResmiTatillerIsGunleri()[0]] #ya hepsi HT ya da Normal işgünü
                HtNrm = [i for i in SiraliGunler if i in self.HaftaTatilleriNormal()]
                Rt = [i for i in SiraliGunler if i in self.SeciliDonemResmiTatillerIsGunleri()[3]] #resmi tatiller
                z = tur
                SaydirTur=[z for i in range((len(SiraliGunler)- len(farklar)))] #izin türü klonlama
                TextHt=[i.strftime('%d-%B-%Y-%A') for i in Ht]
                TextRt=[i.strftime('%d-%B-%Y-%A') for i in Rt]

                if (len(Ht)!=(len(SiraliGunler) - len(farklar)) or len(Ht)==(len(SiraliGunler) - len(farklar))) and HtNrm!=[]: #Sadece HT gözetiyor ama 1 günlük HT kaçırıyor
                    metin = 'İzin tarihleri HAFTA TATİL gününe denk gelmektedir.\n\nHafta Tatilleri:\n\n{}\n\nİzin Türü: {}\n\nPuantaja Nasıl İşlensin?\n\nNot: Çıkarsan Tatil Günlerini Atlayarak İşler'.format(str(TextHt),z).replace(",","\n")
                    mesajMetin  = '<pre style="font-size:12pt; color: #064e9a;">{}<figure>'.format(metin)
                    box.setText(mesajMetin)
                    box.setWindowTitle('HAFTA TATİL GÜNLERİ PUANTAJ')
                    box.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
                    buttonY = box.button(QMessageBox.Yes)
                    buttonY.setText('Üzerine İşle')
                    buttonN = box.button(QMessageBox.No)
                    buttonN.setText('Atla')
                    box.exec_()
                    
                    if box.clickedButton() == buttonY: #üzerine işleyerek
                        for d in SiraliGunler:
                            if d in self.SeciliDonemResmiTatillerIsGunleri()[2]: #tam ay
                                d=int(d.day)
                                for f in SaydirTur:
                                    puantaj[(d-1)]=f
                                
                        for s in SiraliGunler:
                            if s in self.SeciliDonemResmiTatillerIsGunleri()[3]: #resmi tatil
                                s=int(s.day)
                                puantaj[(s-1)]=self.objResmiTatil

                    if box.clickedButton() == buttonN: #hafta tatilleri atlayarak
                        for d in SiraliGunler:
                            if d in self.SeciliDonemResmiTatillerIsGunleri()[2]:
                                d=int(d.day)
                                for f in SaydirTur:
                                    puantaj[(d-1)]=f
                                    
                        for i in SiraliGunler:
                            if i in self.SeciliDonemResmiTatillerIsGunleri()[0]:
                                i=int(i.day)
                                puantaj[(i-1)]=self.objHaftaTatili

                        for s in SiraliGunler:
                            if s in self.SeciliDonemResmiTatillerIsGunleri()[3]:
                                s=int(s.day)
                                puantaj[(s-1)]=self.objResmiTatil

                if len(Ht)!=(len(SiraliGunler) - len(farklar)) and HtNrm==[]: # HT denk gelmeyen izin günleri
                    for d in SiraliGunler:
                        if d in self.SeciliDonemResmiTatillerIsGunleri()[2]:
                            d=int(d.day)
                            for f in SaydirTur:
                                puantaj[(d-1)]=f
                                
                if len(Ht)==(len(SiraliGunler) - len(farklar)) and HtNrm==[]: # HT olmaksızın bütün iş günleri
                    for d in SiraliGunler:
                        if d in self.SeciliDonemResmiTatillerIsGunleri()[2]:
                            d=int(d.day)
                            for f in SaydirTur:
                                puantaj[(d-1)]=f

                if Rt:
                    metin = 'İzin tarihleri RESMİ TATİL gününe denk gelmektedir.\n\nResmi Tatiller:\n\n{}\n\nİzin Türü: {}\n\nPuantaja Nasıl İşlensin?\n\nNot: Çıkarsan Tatil Günlerini Atlayarak İşler'.format(str(TextRt),z).replace(",","\n")
                    mesajMetin  = '<pre style="font-size:12pt; color: #064e9a;">{}<figure>'.format(metin)
                    box.setText(mesajMetin)
                    box.setWindowTitle('RESMİ TATİL GÜNLERİ PUANTAJ')
                    box.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
                    buttonY = box.button(QMessageBox.Yes)
                    buttonY.setText('Üzerine İşle')
                    buttonN = box.button(QMessageBox.No)
                    buttonN.setText('Atla')
                    box.exec_()
                    if box.clickedButton() == buttonY:
                        for s in SiraliGunler:
                            if s in self.SeciliDonemResmiTatillerIsGunleri()[3]:
                                s=int(s.day)
                                f = tur
                                puantaj[(s-1)]=f 
                       
                    if box.clickedButton() == buttonN:
                        for s in SiraliGunler:
                            if s in self.SeciliDonemResmiTatillerIsGunleri()[3]:
                                s=int(s.day)
                                puantaj[(s-1)]=self.objResmiTatil
                        

        if (self.GirisCikis()[0] in self.SeciliDonemResmiTatillerIsGunleri()[2]) and self.IseGirisData() is not None: # if işe giriş - 1 seçili dönemin içerisindeyse ----
            SaydirGirisAralik = self.IseGirisData()[1].day-self.IseGirisData()[0].day
            for g in range(SaydirGirisAralik):
                puantaj[g]=self.objCalismaDisi
        
        if (self.GirisCikis()[1] in self.SeciliDonemResmiTatillerIsGunleri()[2]) and self.IstenCikisData() is not None: # if işten ayrılış + 1 seçili dönemin içerisindeyse ----
            SaydirCikisAralik = date_range(start=self.IstenCikisData()[0],end=self.IstenCikisData()[1],freq="D")
            for ck in SaydirCikisAralik:
                ck=int(ck.day)
                puantaj[(ck-1)]=self.objCalismaDisi
        
        if (self.GirisCikis()[0] > self.SeciliDonemResmiTatillerIsGunleri()[4]) and (self.GirisCikis()[0]+ DateOffset(1)) not in self.SeciliDonemResmiTatillerIsGunleri()[6]: # if işe giriş-1 seçili dönemin başından büyükse ve (işe giriş-1 seçili dönemin içerisinde değilse )
            puantaj = list([self.objIseGirmedi]*len(self.SeciliDonemResmiTatillerIsGunleri()[2]))
        
        if not self.dateIStenAyrilis in {"02.01.1753","2.01.1753","02.1.1753","2.1.1753",""," ", str(self.SeciliDonemResmiTatillerIsGunleri()[6])} and (self.GirisCikis()[1] <= self.SeciliDonemResmiTatillerIsGunleri()[4]): # if işten ayrılış + 1 seçili dönemin başından küçükeşitse
            puantaj = list([self.objCikmis]*len(self.SeciliDonemResmiTatillerIsGunleri()[2]))

        return puantaj