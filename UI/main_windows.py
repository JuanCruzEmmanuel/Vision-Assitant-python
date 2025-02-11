import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow,QApplication,QFileDialog,QShortcut,QDialog
from LOGICAL.widgets_control import CanvasWidget
from UI.color_plane_extractor import PlaneExtractor
from UI.color_operators import ColorOperator
from UI.color_manipulation import colorManipulation
from PyQt5.QtGui import QKeySequence
from UI.generic_popup import Popup

__author__ = "Juan Cruz Noya"
__country__ = "Argentina"
__license__ = "MIT"
__version__ = "1.0.6"
__maintainer__ = "Juan Cruz Noya"
__email__ = "juancruznoya@unc.edu.ar"
__status__ = "Production"


"""
VERSIONES
1.0.0 Se inicia el proyecto. En un primer momento solo se trataba de un asistente simple con intefaz en codigo
1.0.1 Proyecto Crece y se agregan funciones mas complejas. A su vez se crea un pipeline que se podra ejecutar siempre de manera automaticazada

1.0.2 "Se reinicia" el proyecto buscando un enfoque mas estructurado del mismo. Ahora la UI es mediante qt designer. Se agregan atajos de teclado
1.0.3 se agregan funcionabilidades como cortar el patron para mas facilidades de trabajo. Se agrega la posibilidad de observar el histograma de la imagen
1.0.4 Se agrega el plano de extraccion de colores.
1.0.5 Se agrega La operacion de colores
1.0.6 Se agrega manipulacion de colores en hsv
"""

class Main(QMainWindow):

    def  __init__(self):
        super().__init__()
        
        uic.loadUi("UI/main.ui",self)
        
        self.select_kernel = Popup(window_title="Select Kernel", text="Block Size", text2="C") #Creo un popup en caso de necesitarlo
        self.re_scale_popup = Popup(window_title="Select zoom", text="zoom") #Creo un popup en caso de necesitarlo
        self.extractor_color = PlaneExtractor(cv_imagen=None) #no le cargo imagen
        self.color_operator_popup = ColorOperator(cv_image=None) #No le cargo imagen
        self.color_manipilation_popup = colorManipulation(cv_image=None) #No le cargo imagen
        #Bar Menu actions
        
        self.canvas = CanvasWidget(self.img_conteiner) #This is the image control and is going to img_conteiner
        
        self.img_display.addWidget(self.canvas) #Lo uso para que sea el widgets encargado de visor de imagen
        
        self.Convert_To_Grayscale.triggered.connect(self.canvas.apply_grayscale) #Al presionar el boton de gray scale convierte esta en blanco y negro
        
        self.Flip.triggered.connect(self.canvas.apply_flip) #Rota la imagen 180º
        
        
        self.Open_Image.triggered.connect(self.open_image) #Carga la imagen
        
        self.Undo.triggered.connect(self.canvas.undo) #Elimina la ultima accion
        
        self.Select_Pattern.triggered.connect(self.open_patron) #Selecciona una imagen patron
        self.Adaptative_Theshold.triggered.connect(self.kernel_selector)
        self.Chop_Pattern.triggered.connect(self.canvas.chop_loaded_pattern)
        self.Histogram.triggered.connect(self.canvas.view_hisogram)
        self.Geometry.triggered.connect(self.size_selector)
        self.Color_plane_extraction.triggered.connect(self.plane_selector)
        self.Clamp.triggered.connect(self.canvas.apply_clamp)
        
        self.Color_Operators.triggered.connect(self.color_operator_window)
        
        self.Color_Manipulation.triggered.connect(self.color_manipulation_control)
        #Atajos de teclado
        
        self.shortcut_undo = QShortcut(QKeySequence("Ctrl+z"), self).activated.connect(self.canvas.undo) #Atajo retroceso
        self.shortcut_flip = QShortcut(QKeySequence("Ctrl+w"), self).activated.connect(self.canvas.apply_flip) #Atajo flip
        self.shortcut_gray = QShortcut(QKeySequence("Ctrl+q"), self).activated.connect(self.canvas.apply_grayscale) #Atajo gray scale
        self.open = QShortcut(QKeySequence("Ctrl+o"), self).activated.connect(self.open_image) #Atajo seleccionar imagen
        self.pattern = QShortcut(QKeySequence("Ctrl+p"), self).activated.connect(self.open_patron) #Atajo seleccionar patron imagen
        self.chop = QShortcut(QKeySequence("Ctrl+x"), self).activated.connect(self.canvas.chop_loaded_pattern) #Atajo cortar patron
        
    def open_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select image from Files", "", "Image Files (*.png *.jpg *.bmp *.jpeg)", options=options)
        if file_name: # this is full path                                
            self.canvas.load_image(file_name) # This charge the img in memory
            
    def open_patron(self):
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self,"Select image from Files", "", "Image Files (*.png *.jpg *.bmp *.jpeg)", options=options)
        if path:
            self.canvas.select_pattern(path)
            
    def kernel_selector(self):
        if self.canvas.GS:
            dialog = self.select_kernel
            if dialog.exec_() == QDialog.Accepted:
                kernel, c = dialog.getValues()
                #print(f"Selected Kernels: {kernel1}, {kernel2}")
                self.canvas.apply_threshold_filter(kernel, c)
            else:
                return None, None
            
    def size_selector(self):
        if self.canvas.qt_image is not None: #En caso que haya una imagen cargada
            dialog = self.re_scale_popup
            if dialog.exec_() == QDialog.Accepted: #Al presionar aceptar
                zoom= dialog.getValues()
                self.canvas.apply_zoom(zoom=zoom)
            else:
                return None
            
    def plane_selector(self):
        if self.canvas.qt_image is not None: #En caso que haya una imagen cargada
            temp_img = self.canvas.get_cv_image()
            self.extractor_color.set_imagen(cv_image=temp_img)
            dialog=self.extractor_color
            if dialog.exec_() == QDialog.Accepted: #Al presionar aceptar
                extraction, blackwhite = dialog.getValues()
                self.canvas.apply_plane_extraction(plane=extraction,bw=blackwhite)
            else:
                pass
    def color_operator_window(self):
        if self.canvas.qt_image is not None:
            temp_img = self.canvas.get_cv_image() #Tomo la imagen cargada
            self.color_operator_popup.load_image(cv_image=temp_img)
            dialog = self.color_operator_popup
            if dialog.exec_() == QDialog.Accepted:
                operation,color = dialog.getValues()
                #Se debe agregar la funncion en el canva
                
            else:
                pass
    def color_manipilation_control(self):
        if self.canvas.qt_image is not None:
            temp_img = self.canvas.get_cv_image() #Tomo la imagen cargada
            self.color_manipilation_popup.load_image(cv_image=temp_img)
            dialog = self.color_operator_popup
            if dialog.exec_() == QDialog.Accepted:
                print("HACER ALGO")
        
if __name__ =="__main__":
    app = QApplication(sys.argv)
    mw = Main()
    mw.show()
    sys.exit(app.exec_())