import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import cv2
import numpy as np
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog,QApplication,QListWidget

"""
Abre la ventana para extraer el color de la imagen

"""

class PlaneExtractor(QDialog):
    def __init__(self,cv_imagen=None):
        super().__init__()
        uic.loadUi("UI\color_plane.ui",self)
        self.image = cv_imagen
        self.extraction_list.clicked.connect(self.show_image)
        self._BLACK_WHITE = False

        self.blackAndWhite.clicked.connect(self.checkBox) #Conecta la presion del boton a la funcion de cambio

        self.buttonBox.accepted.connect(self.accept) #activo los botones OK Y CANCEL. Envia directamente la señal getValues
        self.buttonBox.rejected.connect(self.reject)
        self._EXTRACTION_PLANE = None  
    def on_mouse_click(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:  # Cuando se hace clic con el botón izquierdo
            cv2.destroyAllWindows()  # Cerrar todas las ventanas

    def checkBox(self):
        """
        Cambia el estado de la variable black and white al presionar el check box
        """
        self._BLACK_WHITE =self.blackAndWhite.isChecked()

    def set_imagen(self,cv_image):
        """
        Carga la imagen a la UI
        """
        self.image = cv_image

    def show_image(self):
        #print(self.black_white)
        im_temp = self.image.copy()
        b, g, r = cv2.split(self.image) #separo los planos de trabajo
        selector = self.extraction_list.currentItem().text()
        self._EXTRACTION_PLANE = selector
        if selector == "RGB - Red Plane":
            #print(1)
            #im_temp = cv2.merge([np.zeros_like(b), np.zeros_like(g), r]) #Elimino el plano Rojo
            im_temp = r
        elif selector == "RGB - Green Plane":
            #print(2)
            #im_temp = cv2.merge([np.zeros_like(b), g, np.zeros_like(r)]) #Elimino el plano verde
            im_temp = g
        elif selector == "RGB - Blue Plane":
            #print(3)
            #im_temp = cv2.merge([b, np.zeros_like(g), np.zeros_like(r)]) #Elimino el plano azul
            im_temp = b
        #if self._BLACK_WHITE:
            #im_temp = cv2.cvtColor(im_temp, cv2.COLOR_BGR2GRAY)
        print(im_temp.shape)
        cv2.imshow("Imagen",im_temp)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    def getValues(self):
        
        return self._EXTRACTION_PLANE, self._BLACK_WHITE
if __name__ =="__main__":
    #help(QListWidget)
    imagen_cv = cv2.imread(r"C:\Users\Desarrollo-LucasB\Desktop\Asistente de vision 2\patron_2.jpeg")
    app = QApplication(sys.argv)
    mw = PlaneExtractor(cv_imagen=imagen_cv)
    mw.show()
    sys.exit(app.exec_())