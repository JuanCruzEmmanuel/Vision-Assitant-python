import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import cv2
import numpy as np
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog,QApplication,QListWidget
from PyQt5.QtGui import QColor
from UI.UTILS import RangeSliderWidget
from PyQt5.QtCore import Qt


class colorManipulation(QDialog):
    def __init__(self,cv_image=None):
        super().__init__()
        uic.loadUi("UI/color_manipulation.ui",self)
        self._IMAGE = cv_image #es necestaio tener una imagen para mostrarlo
        #HUE1,HUE2,HUE3,HUE4 SON LAYOUT
        #SAT1,SAT2,SAT3,SAT4 SON LAYOUT
        #VAL1,VAL2,VAL3,VAL4 SON LAYOUT
        #Slicer 1
        self.hue_slicer_1 = RangeSliderWidget(min_value=0,max_value=180) #pongo el circulo el widget
        self.HUE1.addWidget(self.hue_slicer_1)
        self.HUE1.update()
        self.hue_slicer_1.rangedValue.connect(self.update_hue1)
        self.hue1_color = (0,0)
        self.saturation_slicer_1 = RangeSliderWidget()
        self.SAT1.addWidget(self.saturation_slicer_1)
        self.SAT1.update()
        self.saturation_slicer_1.rangedValue.connect(self.update_sat1)
        self.sat1_color = (0,0)
        self.value_slicer_1 = RangeSliderWidget()
        self.VAL1.addWidget(self.value_slicer_1)
        self.VAL1.update()
        self.value_slicer_1.rangedValue.connect(self.update_val1)
        self.val1_color = (0,0)
        #Slicer 2
        self.hue_slicer_2 = RangeSliderWidget(min_value=0,max_value=180) #pongo el circulo el widget
        self.HUE2.addWidget(self.hue_slicer_2)
        self.HUE2.update()
        self.hue2_color = (0,0)
        self.hue_slicer_2.rangedValue.connect(self.update_hue2)
        self.saturation_slicer_2 = RangeSliderWidget()
        self.SAT2.addWidget(self.saturation_slicer_2)
        self.SAT2.update()
        self.sat2_color = (0,0)
        self.saturation_slicer_2.rangedValue.connect(self.update_sat2)
        self.value_slicer_2 = RangeSliderWidget()
        self.VAL2.addWidget(self.value_slicer_2)
        self.VAL2.update()
        self.val2_color = (0,0)
        self.value_slicer_2.rangedValue.connect(self.update_val2)
        #Slicer 3 YA RELACIONADO AL COLOR SECUNDARIO
        self.hue_slicer_3 = RangeSliderWidget() #pongo el circulo el widget
        self.HUE3.addWidget(self.hue_slicer_3)
        self.HUE3.update()
        self.R_color = (0,0)
        self.hue_slicer_3.rangedValue.connect(self.update_hue3)
        self.saturation_slicer_3 = RangeSliderWidget()
        self.SAT3.addWidget(self.saturation_slicer_3)
        self.SAT3.update()
        self.G_color = (0,0)
        self.saturation_slicer_3.rangedValue.connect(self.update_sat3)
        self.value_slicer_3 = RangeSliderWidget()
        self.VAL3.addWidget(self.value_slicer_3)
        self.VAL3.update()
        self.B_color = (0,0)
        self.value_slicer_3.rangedValue.connect(self.update_val3)
        #Slicer 4
        self.hue_slicer_4 = RangeSliderWidget(min_value=0,max_value=180) #pongo el circulo el widget
        self.HUE4.addWidget(self.hue_slicer_4)
        self.HUE4.update()
        self.hue4_color = (0,0)
        self.hue_slicer_4.rangedValue.connect(self.update_hue4)
        self.saturation_slicer_4 = RangeSliderWidget()
        self.SAT4.addWidget(self.saturation_slicer_4)
        self.SAT4.update()
        self.sat4_color = (0,0)
        self.saturation_slicer_4.rangedValue.connect(self.update_sat4)
        self.value_slicer_4 = RangeSliderWidget()
        self.VAL4.addWidget(self.value_slicer_4)
        self.VAL4.update()
        self.val4_color = (0,0)
        self.value_slicer_4.rangedValue.connect(self.update_val4)

        self._OPERATION = "Substract" #Lo inicializo en un valor para evitar errores
        self.operationBox.currentTextChanged.connect(self.switchCase) #Desde aca voy a usar las operaciones
        self.HUE1.addWidget(self.hue_slicer_1)
        self.HUE1.update()
    def switchCase(self):
        """
        No se me ocurrio otro nombre xd
        """
        self._OPERATION = self.operationBox.currentText()
        
        if self._OPERATION == "Substract":
            self.substract()
        elif self._OPERATION == "Change":
            self.change()
    
    def load_image(self,cv_image):
        """
        Carga la imagen de manera externa\n
        :cv_image: Imagen en formato cv
        """
        self._IMAGE = cv_image #Cargo como atributo
    
    def substract(self):
        im_temp = self._IMAGE.copy()
        HSV_IMAGE = cv2.cvtColor(self._IMAGE,cv2.COLOR_BGR2HSV) #Cambio el plano de trabajo

        #para trabajar las imagenes voy a tener que usar los colores maximos y minimos
        #(hue,sat,value)
        low_color_1 = np.array([self.hue1_color[0],self.sat1_color[0],self.val1_color[0]])
        high_color_1 = np.array([self.hue1_color[1],self.sat1_color[1],self.val1_color[1]])
        mask = cv2.inRange(HSV_IMAGE, low_color_1, high_color_1)
       
        if self.hue2_color[1]-self.hue2_color[0]<100: #Totalmente arbitrario
            low_color_2 = np.array([self.hue2_color[0],self.sat2_color[0],self.val2_color[0]])
            high_color_2 = np.array([self.hue2_color[1],self.sat2_color[1],self.val2_color[1]])
            mask2 = cv2.inRange(HSV_IMAGE, low_color_2, high_color_2)
            
            mask = cv2.bitwise_or(mask,mask2) #En caso que exista, los uno
        
        cv2.imshow("Mask", mask)
        im_temp[mask > 0] = [0, 0, 0]
        
        cv2.imshow("Substract",im_temp)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    def change(self):
        im_temp = self._IMAGE.copy()
        HSV_IMAGE = cv2.cvtColor(self._IMAGE,cv2.COLOR_BGR2HSV) #Cambio el plano de trabajo

        #para trabajar las imagenes voy a tener que usar los colores maximos y minimos
        #(hue,sat,value)
        low_color_1 = np.array([self.hue1_color[0],self.sat1_color[0],self.val1_color[0]])
        high_color_1 = np.array([self.hue1_color[1],self.sat1_color[1],self.val1_color[1]])
        mask = cv2.inRange(HSV_IMAGE, low_color_1, high_color_1)
       
        if self.hue2_color[1]-self.hue2_color[0]<100: #Totalmente arbitrario
            low_color_2 = np.array([self.hue2_color[0],self.sat2_color[0],self.val2_color[0]])
            high_color_2 = np.array([self.hue2_color[1],self.sat2_color[1],self.val2_color[1]])
            mask2 = cv2.inRange(HSV_IMAGE, low_color_2, high_color_2)
            
            mask = cv2.bitwise_or(mask,mask2) #En caso que exista, los uno
        
        cv2.imshow("Mask", mask)
        im_temp[mask > 0] = [self.B_color[1], self.G_color[1], self.R_color[1]]
        
        cv2.imshow("Change",im_temp)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    #Tengo que buscar una forma mas elegante de resolver esto, ya que hace lo mismo    
    def update_hue1(self,value):
        
        self.hue1_color = value
        
        self.switchCase()
    def update_hue2(self,value):
        
        self.hue2_color = value
        self.switchCase()
    def update_hue3(self,value):
        
        self.R_color = value
        self.switchCase()
    def update_hue4(self,value):
        
        self.hue4_color = value
        self.switchCase()
    def update_sat1(self,value):
        
        self.sat1_color = value
        self.switchCase()
    def update_sat2(self,value):
        
        self.sat2_color = value
        self.switchCase()
    def update_sat3(self,value):
        
        self.G_color = value
        self.switchCase()
    def update_sat4(self,value):
        
        self.sat4_color = value
        self.switchCase()
    def update_val1(self,value):
        
        self.val1_color = value
        self.switchCase()
    def update_val2(self,value):
        
        self.val2_color = value
        self.switchCase()
    def update_val3(self,value):
        
        self.B_color= value
        self.switchCase()
    def update_val4(self,value):
        
        self.val4_color = value
        self.switchCase()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ima = cv2.imread(r"C:\Users\juanc\Desktop\Asistente de vision\manzana.jpg")
    dialog = colorManipulation(cv_image=ima)
    dialog.exec_()