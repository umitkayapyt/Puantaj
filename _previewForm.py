# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '_preview.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PreviewWindow(object):
    def setupUi(self, PreviewWindow):
        PreviewWindow.setObjectName("PreviewWindow")
        PreviewWindow.resize(2319, 951)
        self.centralwidget = QtWidgets.QWidget(PreviewWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tableProductsPreview = QtWidgets.QTableWidget(self.centralwidget)
        self.tableProductsPreview.setGeometry(QtCore.QRect(20, 0, 1881, 841))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.tableProductsPreview.setFont(font)
        self.tableProductsPreview.setStyleSheet("background-color: rgb(85, 255, 255);")
        self.tableProductsPreview.setObjectName("tableProductsPreview")
        self.tableProductsPreview.setColumnCount(0)
        self.tableProductsPreview.setRowCount(0)
        self.btn_ExcelAktir = QtWidgets.QPushButton(self.centralwidget)
        self.btn_ExcelAktir.setGeometry(QtCore.QRect(1800, 850, 51, 51))
        self.btn_ExcelAktir.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/resim/kaynakjpg/Microsoft-Office-Excel-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_ExcelAktir.setIcon(icon)
        self.btn_ExcelAktir.setIconSize(QtCore.QSize(50, 50))
        self.btn_ExcelAktir.setObjectName("btn_ExcelAktir")
        PreviewWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(PreviewWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 2319, 26))
        self.menubar.setObjectName("menubar")
        PreviewWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(PreviewWindow)
        self.statusbar.setObjectName("statusbar")
        PreviewWindow.setStatusBar(self.statusbar)

        self.retranslateUi(PreviewWindow)
        QtCore.QMetaObject.connectSlotsByName(PreviewWindow)

    def retranslateUi(self, PreviewWindow):
        _translate = QtCore.QCoreApplication.translate
        PreviewWindow.setWindowTitle(_translate("PreviewWindow", "Ön İzleme"))
import kaynak_rc


# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     PreviewWindow = QtWidgets.QMainWindow()
#     ui = Ui_PreviewWindow()
#     ui.setupUi(PreviewWindow)
#     PreviewWindow.show()
#     sys.exit(app.exec_())
