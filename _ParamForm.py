# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '_ParamForm.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ParamWindow(object):
    def setupUi(self, ParamWindow):
        ParamWindow.setObjectName("ParamWindow")
        ParamWindow.resize(870, 550)
        ParamWindow.setMaximumSize(QtCore.QSize(870, 550))
        ParamWindow.setStyleSheet("#centralwidget{\n"
"border-image: url(:/resim/kaynakjpg/dpanic88.jpg);\n"
"}\n"
"\n"
"\n"
"")
        self.centralwidget = QtWidgets.QWidget(ParamWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(110, 30, 301, 301))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_12 = QtWidgets.QLabel(self.layoutWidget)
        self.label_12.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";\n"
"color: rgb(255, 255, 255);")
        self.label_12.setObjectName("label_12")
        self.gridLayout_4.addWidget(self.label_12, 0, 0, 1, 1)
        self.txtCalismaGunu = QtWidgets.QLineEdit(self.layoutWidget)
        self.txtCalismaGunu.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";")
        self.txtCalismaGunu.setText("")
        self.txtCalismaGunu.setDragEnabled(True)
        self.txtCalismaGunu.setClearButtonEnabled(True)
        self.txtCalismaGunu.setObjectName("txtCalismaGunu")
        self.gridLayout_4.addWidget(self.txtCalismaGunu, 0, 1, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.layoutWidget)
        self.label_13.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";\n"
"color: rgb(255, 255, 255);")
        self.label_13.setObjectName("label_13")
        self.gridLayout_4.addWidget(self.label_13, 1, 0, 1, 1)
        self.txtCalismaDisi = QtWidgets.QLineEdit(self.layoutWidget)
        self.txtCalismaDisi.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";")
        self.txtCalismaDisi.setText("")
        self.txtCalismaDisi.setDragEnabled(True)
        self.txtCalismaDisi.setClearButtonEnabled(True)
        self.txtCalismaDisi.setObjectName("txtCalismaDisi")
        self.gridLayout_4.addWidget(self.txtCalismaDisi, 1, 1, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.layoutWidget)
        self.label_14.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";\n"
"color: rgb(255, 255, 255);")
        self.label_14.setObjectName("label_14")
        self.gridLayout_4.addWidget(self.label_14, 2, 0, 1, 1)
        self.txtHaftaTatili = QtWidgets.QLineEdit(self.layoutWidget)
        self.txtHaftaTatili.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";")
        self.txtHaftaTatili.setText("")
        self.txtHaftaTatili.setDragEnabled(True)
        self.txtHaftaTatili.setClearButtonEnabled(True)
        self.txtHaftaTatili.setObjectName("txtHaftaTatili")
        self.gridLayout_4.addWidget(self.txtHaftaTatili, 2, 1, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.layoutWidget)
        self.label_15.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";\n"
"color: rgb(255, 255, 255);")
        self.label_15.setObjectName("label_15")
        self.gridLayout_4.addWidget(self.label_15, 3, 0, 1, 1)
        self.txtResmiTatil = QtWidgets.QLineEdit(self.layoutWidget)
        self.txtResmiTatil.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";")
        self.txtResmiTatil.setText("")
        self.txtResmiTatil.setDragEnabled(True)
        self.txtResmiTatil.setClearButtonEnabled(True)
        self.txtResmiTatil.setObjectName("txtResmiTatil")
        self.gridLayout_4.addWidget(self.txtResmiTatil, 3, 1, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.layoutWidget)
        self.label_18.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";\n"
"color: rgb(255, 255, 255);")
        self.label_18.setObjectName("label_18")
        self.gridLayout_4.addWidget(self.label_18, 4, 0, 1, 1)
        self.txtIseGirmedi = QtWidgets.QLineEdit(self.layoutWidget)
        self.txtIseGirmedi.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";")
        self.txtIseGirmedi.setText("")
        self.txtIseGirmedi.setDragEnabled(True)
        self.txtIseGirmedi.setClearButtonEnabled(True)
        self.txtIseGirmedi.setObjectName("txtIseGirmedi")
        self.gridLayout_4.addWidget(self.txtIseGirmedi, 4, 1, 1, 1)
        self.label_20 = QtWidgets.QLabel(self.layoutWidget)
        self.label_20.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";\n"
"color: rgb(255, 255, 255);")
        self.label_20.setObjectName("label_20")
        self.gridLayout_4.addWidget(self.label_20, 5, 0, 1, 1)
        self.txtCikmis = QtWidgets.QLineEdit(self.layoutWidget)
        self.txtCikmis.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";")
        self.txtCikmis.setText("")
        self.txtCikmis.setDragEnabled(True)
        self.txtCikmis.setClearButtonEnabled(True)
        self.txtCikmis.setObjectName("txtCikmis")
        self.gridLayout_4.addWidget(self.txtCikmis, 5, 1, 1, 1)
        self.btnDegistir = QtWidgets.QPushButton(self.centralwidget)
        self.btnDegistir.setGeometry(QtCore.QRect(110, 350, 301, 101))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDegistir.sizePolicy().hasHeightForWidth())
        self.btnDegistir.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Snap ITC")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(9)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.btnDegistir.setFont(font)
        self.btnDegistir.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.btnDegistir.setAcceptDrops(False)
        self.btnDegistir.setStyleSheet("font: 75 10pt  \"Snap ITC\";\n"
"color: rgb(255, 255, 255);\n"
"background-color: rgb(28, 44, 97);")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/resim/kaynakjpg/hitchhikeguidetogalaxy5_refresh.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnDegistir.setIcon(icon)
        self.btnDegistir.setIconSize(QtCore.QSize(100, 100))
        self.btnDegistir.setObjectName("btnDegistir")
        ParamWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ParamWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 870, 26))
        self.menubar.setObjectName("menubar")
        ParamWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ParamWindow)
        self.statusbar.setObjectName("statusbar")
        ParamWindow.setStatusBar(self.statusbar)

        self.retranslateUi(ParamWindow)
        QtCore.QMetaObject.connectSlotsByName(ParamWindow)

    def retranslateUi(self, ParamWindow):
        _translate = QtCore.QCoreApplication.translate
        ParamWindow.setWindowTitle(_translate("ParamWindow", "Parametreler"))
        self.label_12.setText(_translate("ParamWindow", "Çalışma Günü"))
        self.label_13.setText(_translate("ParamWindow", "Çalışılma Dışı"))
        self.label_14.setText(_translate("ParamWindow", "Hafta Tatili"))
        self.label_15.setText(_translate("ParamWindow", "Resmi Tatil"))
        self.label_18.setText(_translate("ParamWindow", "İşe Girmedi"))
        self.label_20.setText(_translate("ParamWindow", "İşten Ayrılmış"))
        self.btnDegistir.setToolTip(_translate("ParamWindow", "CTRL+D"))
        self.btnDegistir.setText(_translate("ParamWindow", "PARAMETRELERİ\n"
"   GÜNCELLE"))
        self.btnDegistir.setShortcut(_translate("ParamWindow", "Ctrl+D"))
import kaynak_rc


# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     ParamWindow = QtWidgets.QMainWindow()
#     ui = Ui_ParamWindow()
#     ui.setupUi(ParamWindow)
#     ParamWindow.show()
#     sys.exit(app.exec_())