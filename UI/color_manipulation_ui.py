# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\juanc\Desktop\Asistente de vision\UI\color_manipulation.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Color_Manipulation(object):
    def setupUi(self, Color_Manipulation):
        Color_Manipulation.setObjectName("Color_Manipulation")
        Color_Manipulation.resize(617, 346)
        Color_Manipulation.setModal(False)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Color_Manipulation)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Contenedor = QtWidgets.QWidget(Color_Manipulation)
        self.Contenedor.setObjectName("Contenedor")
        self.colorWheel_1 = QtWidgets.QWidget(self.Contenedor)
        self.colorWheel_1.setGeometry(QtCore.QRect(40, 60, 241, 241))
        self.colorWheel_1.setObjectName("colorWheel_1")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.colorWheel_1)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 241, 241))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.wheel_layout_1 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.wheel_layout_1.setContentsMargins(0, 0, 0, 0)
        self.wheel_layout_1.setObjectName("wheel_layout_1")
        self.colorWheel_2 = QtWidgets.QWidget(self.Contenedor)
        self.colorWheel_2.setGeometry(QtCore.QRect(330, 60, 241, 241))
        self.colorWheel_2.setObjectName("colorWheel_2")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.colorWheel_2)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(0, 0, 241, 241))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.wheel_layout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.wheel_layout_2.setContentsMargins(0, 0, 0, 0)
        self.wheel_layout_2.setObjectName("wheel_layout_2")
        self.operationBox = QtWidgets.QComboBox(self.Contenedor)
        self.operationBox.setGeometry(QtCore.QRect(40, 0, 241, 22))
        self.operationBox.setObjectName("operationBox")
        self.operationBox.addItem("")
        self.operationBox.addItem("")
        self.label = QtWidgets.QLabel(self.Contenedor)
        self.label.setGeometry(QtCore.QRect(120, 310, 81, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.Contenedor)
        self.label_2.setGeometry(QtCore.QRect(430, 310, 81, 16))
        self.label_2.setObjectName("label_2")
        self.minimum = QtWidgets.QRadioButton(self.Contenedor)
        self.minimum.setGeometry(QtCore.QRect(40, 30, 91, 17))
        self.minimum.setObjectName("minimum")
        self.maximum = QtWidgets.QRadioButton(self.Contenedor)
        self.maximum.setGeometry(QtCore.QRect(180, 30, 101, 17))
        self.maximum.setObjectName("maximum")
        self.horizontalLayout.addWidget(self.Contenedor)

        self.retranslateUi(Color_Manipulation)
        QtCore.QMetaObject.connectSlotsByName(Color_Manipulation)

    def retranslateUi(self, Color_Manipulation):
        _translate = QtCore.QCoreApplication.translate
        Color_Manipulation.setWindowTitle(_translate("Color_Manipulation", "Dialog"))
        self.operationBox.setItemText(0, _translate("Color_Manipulation", "Substract"))
        self.operationBox.setItemText(1, _translate("Color_Manipulation", "Change"))
        self.label.setText(_translate("Color_Manipulation", "SOURCE COLOR"))
        self.label_2.setText(_translate("Color_Manipulation", "TO CHANGE"))
        self.minimum.setText(_translate("Color_Manipulation", "Minimum range"))
        self.maximum.setText(_translate("Color_Manipulation", "Maximum range"))
