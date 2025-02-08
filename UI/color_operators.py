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


class ColorOperator(QDialog):
    def __init__(self,cv_image=None):
        super().__init__()
        uic.loadUi("UI/color_operators.ui",self)
        self._IMAGE = cv_image #es necestaio tener una imagen para mostrarlo

        # Crear el widget de la rueda de colores con el mismo tamaño que el placeholder
        self.color_wheel = ColorWheel(self.colorWheel) #pongo el circulo el widget
        self.color_wheel.setFixedSize(self.colorWheel.size())


        self.color = QColor(255,255,255) #Inicializo una variable con este color blanco
        self.wheel_layout.addWidget(self.color_wheel)

        #Debo agregar alguna forma de conectar la señal
        self.color_wheel.colorSelected.connect(self.updateColor)
        
        #La lista de operaciones
        
        self.operators_list.clicked.connect(self.show_image) #Al presionar ira a la funcion show_image
        self._SELECTOR = None
        #Activo los ok y cancel
        self.buttonBox.accepted.connect(self.accept) #activo los botones OK Y CANCEL. Envia directamente la señal getValues
        self.buttonBox.rejected.connect(self.reject)
    def show_image(self):
        if self._IMAGE is not None:
            
            R = self.color.red() #Obtengo las componente en rojo
            B = self.color.blue() #Obtengo las componente en azul
            G = self.color.green() #obtengo las componente en verde
            
            

            
            selector = self.operators_list.currentItem().text() #Quiero el valor actual seleccionado
            self._SELECTOR = selector
            if selector =="Add":
                NP_COLOR = np.array([B,G,R],dtype=np.uint8)
                im_temp = cv2.add(self._IMAGE,NP_COLOR)
            elif selector =="Subtract":
                NP_COLOR = np.array([B,G,R],dtype=np.uint8)
                im_temp = cv2.subtract(self._IMAGE,NP_COLOR)
            elif selector =="Multiply":
                NP_COLOR = np.array([B/255,G/255,R/255],dtype=np.float32)
                im_temp = cv2.multiply(self._IMAGE.astype(np.float32) ,NP_COLOR)
            elif selector =="Divide":
                try:
                    NP_COLOR = np.array([255/B,255/G,255/R],dtype=np.float32)
                    im_temp = cv2.divide(self._IMAGE,NP_COLOR)
                except:
                    im_temp = self._IMAGE
            elif selector =="Absolute Difference":
                NP_COLOR = np.array([B,G,R],dtype=np.uint8)
                im_temp = cv2.absdiff(self._IMAGE,NP_COLOR)
            elif selector =="Modulo":
                #NP_COLOR = np.array([1/B,1/G,1/R],dtype=np.uint8)
                im_temp = self._IMAGE % np.array([B,G,R],dtype=np.uint8)
                
            elif selector =="And":
                NP_COLOR = np.array([B,G,R],dtype=np.uint8)
                im_temp = cv2.bitwise_and(self._IMAGE,NP_COLOR)
            elif selector =="Not And":
                NP_COLOR = np.array([B,G,R],dtype=np.uint8)
                im_temp = cv2.bitwise_not(cv2.bitwise_and(self._IMAGE,NP_COLOR))#Le aplico el not para hacer el inverso del and
            elif selector =="Or":
                NP_COLOR = np.array([B,G,R],dtype=np.uint8)
                im_temp = cv2.bitwise_or(self._IMAGE,NP_COLOR)
            elif selector =="Not Or":
                NP_COLOR = np.array([B,G,R],dtype=np.uint8)
                im_temp = cv2.bitwise_not(cv2.bitwise_or(self._IMAGE,NP_COLOR))
            elif selector == "Exclusive Or":
                NP_COLOR = np.array([B,G,R],dtype=np.uint8)
                im_temp = cv2.bitwise_xor(self._IMAGE,NP_COLOR)
            elif selector =="Not Exclusive Or":
                NP_COLOR = np.array([B,G,R],dtype=np.uint8)
                im_temp = cv2.bitwise_not(cv2.bitwise_xor(self._IMAGE,NP_COLOR))              
            else:
                im_temp = self._IMAGE
            cv2.imshow("Imagen",im_temp)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            
    def load_image(self,cv_image):
        """
        Para cambiar la imagen que se encuentra dentro
        """
        self._IMAGE = cv_image
    
    def updateColor(self,color):
        """
        Funcion que va a conectar la señal del wheelColor con cambio de color
        """
        self.color =color #Actualizo el valor
        self.colorSample.setStyleSheet(f"background-color: {self.color.name()}")
        if self._SELECTOR is not None:
            self.show_image() #En caso que ya exista cargada alguna operacion y se cambia el color
            
    def getValues(self):
        if self._SELECTOR is not None:
            return self._SELECTOR,(self.color.blue(),self.color.green(),self.color.red()) #Devuelvo una tupla con los colores
        else:
            pass
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ima = cv2.imread(r"C:\Users\juanc\Desktop\Asistente de vision\multipar.jpeg")
    dialog = ColorOperator(cv_image=ima)
    dialog.exec_()