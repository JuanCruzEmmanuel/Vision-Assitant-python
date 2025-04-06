import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog,QFileDialog,QApplication

class selectPattern(QDialog):

    def __init__(self):
        super().__init__()
        uic.loadUi("UI/select_patern.ui",self)
        
        self.path_button.clicked.connect(self.select_path)
        self.path = None
        
        
        self.buttonBox.accepted.connect(self.accept) #activo los botones OK Y CANCEL. Envia directamente la señal getValues
        self.buttonBox.rejected.connect(self.reject)
        
    def select_path(self):
        

        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self,"Select image from Files", "", "Image Files (*.png *.jpg *.bmp *.jpeg)", options=options)
        
        self.path = path
        
        self.path_rute.setText(self.path)
        
    def getValues(self):
        """
        Devuelve el nombre del patron, y la ruta
        """
        return self.Name.text(),self.path
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = selectPattern()
    dialog.exec_()