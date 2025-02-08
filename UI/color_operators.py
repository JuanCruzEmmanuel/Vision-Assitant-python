import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import cv2
import numpy as np
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog,QApplication,QListWidget
from UI.UTILS import ColorWheel


class ColorOperator(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("UI/color_operators.ui",self)


        # Crear el widget de la rueda de colores con el mismo tamaño que el placeholder
        self.color_wheel = ColorWheel(self.colorWheel) #pongo el circulo el widget
        self.color_wheel.setFixedSize(self.colorWheel.size())  

        # Agregar el nuevo widget al layout
        
        self.wheel_layout.addWidget(self.color_wheel)
        # Ocultar el placeholder en lugar de eliminarlo
        #self.colorWheel.hide()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ColorOperator()
    dialog.exec_()