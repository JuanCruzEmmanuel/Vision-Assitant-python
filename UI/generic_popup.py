import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog,QApplication

class Popup(QDialog):
    def __init__(self,window_title="Sin Titulo",text="",text2="",step=1,step2=0, min1=0, min2=0, max1=100, max2=100):
        super().__init__()
        self.a = False
        uic.loadUi("UI/generic_selector.ui",self)
        self.setWindowTitle(window_title)
        self.text.setText(text)
        self.slider_1.valueChanged.connect(self.change_text) # A diferencia de los botones, no tiene triggered, tiene valuechanged
        self.text2.setText(text2)
        self.slider_2.valueChanged.connect(self.change_text)
        if text2=="": #En el caso que no se quiera tener un valor secundario
            self.slider_2.hide()
            self.value_2.setText("-1")
            self.value_2.hide()
            self.slider_2.setEnabled(False)
            self.value_2.setEnabled(False)
        self.buttonBox.accepted.connect(self.accept) #activo los botones OK Y CANCEL. Envia directamente la señal getValues
        self.buttonBox.rejected.connect(self.reject)       
    def change_text(self):
        self.value_1.setText(str(self.slider_1.value()))
        self.value_2.setText(str(self.slider_2.value()))
        #print(self.slider_2.isEnabled())
        #print(self.value_2.text())
        
    def getValues(self):
        if self.slider_2.isEnabled(): #Pregunto si esta activado el slider
            return int(self.value_1.text()), int(self.value_2.text())
        else:
            return int(self.value_1.text())
        
        
if __name__ =="__main__":
    app = QApplication(sys.argv)
    mw = Popup(text="EJEMPLO")
    mw.show()
    sys.exit(app.exec_())