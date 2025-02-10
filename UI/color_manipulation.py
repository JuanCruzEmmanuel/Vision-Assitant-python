import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import cv2
import numpy as np
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog,QApplication,QListWidget
from PyQt5.QtGui import QColor
from UI.UTILS import ColorWheel
from PyQt5.QtCore import Qt


class colorManipulation(QDialog):
    def __init__(self,cv_image=None):
        super().__init__()
        uic.loadUi("UI/color_manipulation.ui",self)
        self._IMAGE = cv_image #es necestaio tener una imagen para mostrarlo
        self.color_wheel_1 = ColorWheel(self.colorWheel_1) #pongo el circulo el widget
        self.color_wheel_1.setFixedSize(self.colorWheel_1.size()) #Convierto el circulo segun el tamaño del widget
        self.color_wheel_2 = ColorWheel(self.colorWheel_2) #pongo el circulo el widget
        self.color_wheel_2.setFixedSize(self.colorWheel_2.size()) #El tamaño del circulo en funcion al tamaño del widget
        self._OPERATION = "Substract" #Lo inicializo en un valor para evitar errores
        self.operationBox.currentTextChanged.connect(self.switchCase) #Desde aca voy a usar las operaciones
        self.color_minimum = QColor(255,255,255) #Lo inicializo en blanco
        self.color_maximum = QColor(255,255,255) #Lo inicializo en blanco
        self.minimum_flag  = True
        self.maximum_flag  = False
        self.minimum.toggled.connect(self.minimum_select)
        #Debo agregar alguna forma de conectar la señal
        self.color_wheel_1.colorSelected.connect(self.updateColor)
    def switchCase(self):
        """
        No se me ocurrio otro nombre xd
        """
        self._OPERATION = self.operationBox.currentText()
        
        if self._OPERATION == "Substract":
            self.substract()
        elif self._OPERATION == "Change":
            self.change()
            
    def minimum_select(self,selected):
        """
        Como solo voy a tener 2 radio buttons puedo usarlo para controlar
        el color
        """
        if selected:
            self.minimum_flag = True
            self.maximum_flag = False
        else:
            self.minimum_flag = False
            self.maximum_flag = True
            
    def updateColor(self,color):
        
        if self.minimum_flag:
            print("holaa")
            self.color_minimum =color #Actualizo el limite inferior
        else:
            print("Holi")
            self.color_maximum =color #Actualizo el limite superir
         
        #print(color.getHsv())
        #print(color.toHsv().hue()) 
        self.switchCase() #Ingreso al switch case
            
        
    def substract(self):
        print(self.color_minimum.toHsv().hue()//2)
        print(self.color_maximum.toHsv().hue()//2)
        im_temp = cv2.cvtColor(self._IMAGE,cv2.COLOR_BGR2HSV)
        lower_color_1 = np.array([self.color_minimum.getHsv()[0]//2,self.color_minimum.getHsv()[1],20]) #Esto puedo mejorar pero me quiiero ir a dormir
     #Esto puedo mejorar pero me quiiero ir a dormir
        upper_color_2 = np.array([self.color_maximum.getHsv()[0]//2,self.color_maximum.getHsv()[1],255])
        mask1 = cv2.inRange(im_temp, lower_color_1, upper_color_2)
        cv2.imshow("mask",mask1)

        
        im_temp[mask1 > 0] =[0,0,0] #Como lo estoy eliminando, quiero que sea negro
        im_temp = cv2.cvtColor(im_temp, cv2.COLOR_HSV2BGR)
        cv2.imshow("Substract",im_temp)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ima = cv2.imread(r"C:\Users\juanc\Desktop\Asistente de vision\multipar.jpeg")
    dialog = colorManipulation(cv_image=ima)
    dialog.exec_()