# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '_UsersForm.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_UsersWindow(object):
    def setupUi(self, UsersWindow):
        UsersWindow.setObjectName("UsersWindow")
        UsersWindow.resize(800, 600)
        UsersWindow.setMaximumSize(QtCore.QSize(800, 600))
        UsersWindow.setStyleSheet("#centralwidget{\n"
"    border-image: url(:/resim/kaynakjpg/dpanic5s.jpg);\n"
"}\n"
"\n"
"\n"
"")
        self.centralwidget = QtWidgets.QWidget(UsersWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.btnLogin = QtWidgets.QPushButton(self.centralwidget)
        self.btnLogin.setGeometry(QtCore.QRect(184, 370, 211, 61))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnLogin.sizePolicy().hasHeightForWidth())
        self.btnLogin.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Snap ITC")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(9)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.btnLogin.setFont(font)
        self.btnLogin.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.btnLogin.setAcceptDrops(False)
        self.btnLogin.setToolTip("")
        self.btnLogin.setStyleSheet("font: 75 12pt  \"Snap ITC\";\n"
"color: rgb(255, 255, 255);\n"
"background-color: rgb(28, 44, 97);")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/resim/kaynakjpg/Hitchhiker-Symbol-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnLogin.setIcon(icon)
        self.btnLogin.setIconSize(QtCore.QSize(60, 60))
        self.btnLogin.setObjectName("btnLogin")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(70, 280, 322, 69))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_12 = QtWidgets.QLabel(self.layoutWidget)
        self.label_12.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";\n"
"color: rgb(255, 255, 255);")
        self.label_12.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_12.setObjectName("label_12")
        self.gridLayout.addWidget(self.label_12, 0, 0, 1, 1)
        self.txtKullaniciAdi = QtWidgets.QLineEdit(self.layoutWidget)
        self.txtKullaniciAdi.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";")
        self.txtKullaniciAdi.setText("")
        self.txtKullaniciAdi.setAlignment(QtCore.Qt.AlignCenter)
        self.txtKullaniciAdi.setDragEnabled(True)
        self.txtKullaniciAdi.setClearButtonEnabled(True)
        self.txtKullaniciAdi.setObjectName("txtKullaniciAdi")
        self.gridLayout.addWidget(self.txtKullaniciAdi, 0, 1, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.layoutWidget)
        self.label_13.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";\n"
"color: rgb(255, 255, 255);")
        self.label_13.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 1, 0, 1, 1)
        self.txtSifre = QtWidgets.QLineEdit(self.layoutWidget)
        self.txtSifre.setEnabled(False)
        self.txtSifre.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";")
        self.txtSifre.setText("")
        self.txtSifre.setFrame(True)
        self.txtSifre.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.txtSifre.setAlignment(QtCore.Qt.AlignCenter)
        self.txtSifre.setDragEnabled(True)
        self.txtSifre.setClearButtonEnabled(True)
        self.txtSifre.setObjectName("txtSifre")
        self.gridLayout.addWidget(self.txtSifre, 1, 1, 1, 1)
        UsersWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(UsersWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        UsersWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(UsersWindow)
        self.statusbar.setObjectName("statusbar")
        UsersWindow.setStatusBar(self.statusbar)

        self.retranslateUi(UsersWindow)
        QtCore.QMetaObject.connectSlotsByName(UsersWindow)

    def retranslateUi(self, UsersWindow):
        _translate = QtCore.QCoreApplication.translate
        UsersWindow.setWindowTitle(_translate("UsersWindow", "Kullanıcı"))
        self.btnLogin.setText(_translate("UsersWindow", " GİRİŞ"))
        self.btnLogin.setShortcut(_translate("UsersWindow", "Backspace"))
        self.label_12.setText(_translate("UsersWindow", "Kullanıcı Adı"))
        self.label_13.setText(_translate("UsersWindow", "Şifre"))
import kaynak_rc


# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     UsersWindow = QtWidgets.QMainWindow()
#     ui = Ui_UsersWindow()
#     ui.setupUi(UsersWindow)
#     UsersWindow.show()
#     sys.exit(app.exec_())
