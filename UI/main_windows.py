import sys
import os
import easyocr
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow,QApplication,QFileDialog,QShortcut,QDialog,QTableWidgetItem,QVBoxLayout
from PyQt5.QtCore import Qt
from LOGICAL.widgets_control import CanvasWidget
from UI.color_plane_extractor import PlaneExtractor
from UI.color_operators import ColorOperator
from UI.color_manipulation import colorManipulation
from UI.Select_patern import selectPattern
from PyQt5.QtGui import QKeySequence
from UI.generic_popup import Popup
import pyqtgraph as pg
import numpy as np
__author__ = "Juan Cruz Noya"
__country__ = "Argentina"
__license__ = "MIT"
__version__ = "1.1.2"
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
1.0.7 Se agrega el boton save scripts
1.0.9 Se agrega que el script se pueda utilizar en multiples fotos y continuar editando
1.0.10 Se agrega el OCR
1.1.0 Se cambia la interfaz grafica, agregando un stackedWidget
1.1.1 Se agrega el boton para cambiar de interaz y tambien la conversion de imagen a numerico
1.1.2 agrego funciones y pyqtgrapgh para la windows 2
"""

class Main(QMainWindow):

    def  __init__(self):
        super().__init__()
        self.ocr = easyocr.Reader(['es', 'en'])
        uic.loadUi("UI/main.ui",self)
        
        self.select_kernel = Popup(window_title="Select Kernel", text="Block Size", text2="C") #Creo un popup en caso de necesitarlo
        self.re_scale_popup = Popup(window_title="Select zoom", text="zoom") #Creo un popup en caso de necesitarlo
        self.extractor_color = PlaneExtractor(cv_imagen=None) #no le cargo imagen
        self.color_operator_popup = ColorOperator(cv_image=None) #No le cargo imagen
        self.color_manipulation_popup = colorManipulation(cv_image=None) #No le cargo imagen

        self.stackedWidget.setCurrentWidget(self.main_page)
        self.MAIN_FLAG = True
        ####Agrego visor de imagenes
        self.graph_widget = pg.PlotWidget() #Creo el objeto a controlar
        x = np.linspace(0, 10, 1000) #Creo una funcion generica facil de usar
        y = np.sin(x)
        self.graph_widget.plot(x, y, pen='r')  
        
        #Bar Menu actions
    
        
        self.canvas = CanvasWidget(self.img_conteiner,ocr=self.ocr) #This is the image control and is going to img_conteiner
        
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
        
        self.Save_Script.triggered.connect(self.canvas.save_scripts)
        
        self.Delete_pattern.clicked.connect(self.delete_patron)
        
        self.Select_source_folder.triggered.connect(self.select_folder)
        
        self.Select_destination_folder.triggered.connect(self.select_destination)
        
        self.Apply_multiple.triggered.connect(self.apply_multiple_imagen)
        
        self.Apply_script.triggered.connect(self.apply_script)
        
        self.OCR_butt.triggered.connect(self.apply_ocr)
        
        self.delete_ocr.clicked.connect(self.delete_selected_ocr)
        
        self.change_to_numeric.triggered.connect(self.change_numeric)
        
        self.To_numeric.triggered.connect(self.apply_im_to_num)

        self.cambiar_nombre_imagen_numerica.clicked.connect(self.change_numeric_name)

        #Atajos de teclado
        self.shortcut_undo = QShortcut(QKeySequence("Ctrl+z"), self).activated.connect(self.canvas.undo) #Atajo retroceso
        self.shortcut_flip = QShortcut(QKeySequence("Ctrl+w"), self).activated.connect(self.canvas.apply_flip) #Atajo flip
        self.shortcut_gray = QShortcut(QKeySequence("Ctrl+q"), self).activated.connect(self.canvas.apply_grayscale) #Atajo gray scale
        self.open = QShortcut(QKeySequence("Ctrl+o"), self).activated.connect(self.open_image) #Atajo seleccionar imagen
        self.pattern = QShortcut(QKeySequence("Ctrl+p"), self).activated.connect(self.open_patron) #Atajo seleccionar patron imagen
        self.chop = QShortcut(QKeySequence("Ctrl+x"), self).activated.connect(self.canvas.chop_loaded_pattern) #Atajo cortar patron
        self.shortcut_save_scripts =QShortcut(QKeySequence("Ctrl+s"), self).activated.connect(self.canvas.save_scripts) #Atajo Guardar scripts
        self.change_windows = QShortcut(QKeySequence("Right"), self).activated.connect(self.change_numeric) #Atajo Guardar scripts
        
        #Señales
        
        self.canvas.patrones_lista.connect(self.update_lista_patrones)
        self.canvas.ocr_lista.connect(self.update_lista_ocr)
        self.canvas.numeric_list.connect(self.update_lista_numerica)
        
        #Updates
        self.ocr_table.clicked.connect(self.ocr_text)
        self.numeric_image_table.clicked.connect(self.update_grafico_numerico)
        
        
        layout = QVBoxLayout(self.imagen_numeric)
        layout.addWidget(self.graph_widget)
        self.imagen_numeric.setLayout(layout)
    def open_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select image from Files", "", "Image Files (*.png *.jpg *.bmp *.jpeg)", options=options)
        if file_name: # this is full path                                
            self.canvas.load_image(file_name) # This charge the img in memory
            
    """def open_patron(self):
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self,"Select image from Files", "", "Image Files (*.png *.jpg *.bmp *.jpeg)", options=options)
        if path:
            self.canvas.select_pattern(path)"""
    def open_patron(self):
        dialog = selectPattern()
        if dialog.exec_() == QDialog.Accepted:
            nombre_patron,path = dialog.getValues()
            if path:
                self.canvas.select_pattern(path=path,name=nombre_patron)
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
                self.canvas.apply_color_operators(operation=operation,color=color)
                
            else:
                pass
    def color_manipulation_control(self):
        if self.canvas.qt_image is not None:
            temp_img = self.canvas.get_cv_image() #Tomo la imagen cargada
            self.color_manipulation_popup.load_image(cv_image=temp_img)
            dialog = self.color_manipulation_popup
            if dialog.exec_() == QDialog.Accepted:
                operacion,color1,color2,color_cambio = dialog.getValues() #donde color1 = rango de color 1, color2 = rango de color 2 y color_cambio = color por el cual se reemplaza
                self.canvas.apply_color_manipulation(operation=operacion,color1=color1,color2=color2,color_change=color_cambio)
                
    def update_lista_patrones(self,lista_patrones):

        self.Pattern_list.setRowCount(len(lista_patrones))
        for row, values in enumerate(lista_patrones):
            coord = f"({values[0].x()},{values[0].width()}),({values[0].y()},{values[0].height()})" #(x0,x1),(y0,y1)
            self.Pattern_list.setItem(row, 0, QTableWidgetItem(str(values[1])))
            self.Pattern_list.setItem(row, 1, QTableWidgetItem(coord))
            
    def delete_patron(self):
        try:
            fila_seleccionada = self.Pattern_list.currentRow()
            nombre_patron = self.Pattern_list.item(fila_seleccionada, 0).text()
        except:
            print("No selecciono ninguna fila a eliminar")
        PATRON_LISTA,PATRON_PATH = self.canvas.get_patern_list()
        _patron_ = [] #aux
        _patron_path = [] #aux
        try:
            for i,p in enumerate(PATRON_LISTA):
                if p[1]!=nombre_patron:
                    _patron_.append(p)
                    _patron_path.append(PATRON_PATH[i]) #La mejor forma que vi de resolver esto
                else:
                    print(f"Se ha eliminado el patron {p}")
        except:
            pass
                
        self.canvas.set_patrones_list(patrones=_patron_,patrones_path=_patron_path)
        self.update_lista_patrones(lista_patrones=_patron_)
        
    def select_folder(self):
        """
        Selecciona la **carpeta con las imagenes target**
        """
        options = QFileDialog.Options()
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", "", options=options)
        self.canvas.SOURCE_FOLDER = folder #selecciona la carpeta para aplicar scripts multiples


    def select_destination(self):
        """
        Selecciona la carpeta donde se **guardarn las imagenes editadas** ademas de sus datos... \n
        """
        options = QFileDialog.Options()
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", "", options=options)
        self.canvas.DESTINATION_FOLDER = folder #folder destino
        
    def apply_multiple_imagen(self):
        """
        Funcion que aplica el patron a multiples imagenes, se debe tener seleccionado la **ruta de imagen** y el la **carpeta de aplicacion**\n
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select from Files", "", "File (*pkl)", options=options)
        self.canvas.scrip_path=file_name
        self.canvas.apply_filter_many_times(debug=True)
        
    def apply_script(self):
        """
        Aplica el script a una imagen especifica. Se debe poder seguir actualizando la misma
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select from Files", "", "File (*pkl)", options=options)
        self.canvas.scrip_path=file_name
        self.canvas.apply_script_and_continue_editing(debug=True)

    def apply_ocr(self):
        """
        Activa el flag ocr
        """
        self.canvas.apply_ocr()

    def update_lista_ocr(self,ocr_lista):

        self.ocr_table.setRowCount(len(ocr_lista))
        for row, values in enumerate(ocr_lista):
            coord = f"({values[1].x()},{values[1].width()}),({values[1].y()},{values[1].height()})" #(x0,x1),(y0,y1)
            self.ocr_table.setItem(row, 0, QTableWidgetItem(str(values[0])))
            self.ocr_table.setItem(row, 1, QTableWidgetItem(coord))
            self.ocr_table.setItem(row, 2, QTableWidgetItem(str(values[2])))
            
    def delete_selected_ocr(self):
        try:
            fila_seleccionada = self.ocr_table.currentRow()
            nombre_ocr = self.ocr_table.item(fila_seleccionada, 0).text()
        except:
            print("No selecciono ninguna fila a eliminar")
        OCR_LISTA = self.canvas.get_ocr_list()
        _ocr_ = [] #aux
        try:
            for i,p in enumerate(OCR_LISTA):
                if p[0]!=nombre_ocr:
                    _ocr_.append(p)

                else:
                    print(f"Se ha eliminado el OCR {p}")
        except:
            pass
        
        self.canvas.set_ocr_list(OCR_list = _ocr_ )
        self.update_lista_ocr(ocr_lista = _ocr_)
    def ocr_text(self):
        currentRow = self.ocr_table.currentRow()
        if currentRow == -1:
            pass
        rowValue = [
            self.ocr_table.item(currentRow, col).text()
            for col in range(self.ocr_table.columnCount())
        ] #Me devuelve una lista con los valores seleccionado en ese indice
        #print(rowValue)
        self.OCR_TEXT.setText(rowValue[2])
        
    def change_numeric(self):
        if self.MAIN_FLAG: #Si estoy en la main, cambio
            self.stackedWidget.setCurrentWidget(self.numeric_page)
            self.MAIN_FLAG=False #Activo que no estoy en el main
        else: #Si no estoy en la main, regreso
            self.stackedWidget.setCurrentWidget(self.main_page)
            self.MAIN_FLAG = True
    def apply_im_to_num(self):
        """
        Activa la flag para numerico
        """
        self.canvas.apply_image_to_numeric()
        
    ##Actualizar lista numerica
    def update_lista_numerica(self,lista_num):
        self.numeric_image_table.setRowCount(len(lista_num)) #Seteo la cantidad de filas "rows"
        for row, values in enumerate(lista_num):
            self.numeric_image_table.setItem(row, 0, QTableWidgetItem(str(values[0]))) #0 nombre; 1=x[~]; 2=y[~]
            
    def update_grafico_numerico(self):
        currentRow = self.numeric_image_table.currentRow()
        if currentRow == -1:
            pass
        rowValue = [
            self.numeric_image_table.item(currentRow, col).text()
            for col in range(self.numeric_image_table.columnCount())
        ] #Me devuelve una lista con los valores seleccionado en ese indice
        lista_numerica_ = self.canvas.get_numeric_list()
        for numerica in lista_numerica_:
            if numerica[0]==rowValue[0]:
                x = numerica[1]
                y = numerica[2]
                self.graph_widget.clear()
                self.graph_widget.plot(x, y, pen='r')  
    def change_numeric_name(self):
        lista_numerica_ = self.canvas.get_numeric_list()
        nombre_actualizado = [self.numeric_image_table.item(0, col).text()
        for col in range(self.numeric_image_table.columnCount())]
        for i in range(len(lista_numerica_)):
            lista_numerica_[i][0] =nombre_actualizado[i]
        self.canvas.set_numeric_list(lista_numerica=lista_numerica_) #Seteo la nueva lista numerica
if __name__ =="__main__":
    app = QApplication(sys.argv)
    mw = Main()
    mw.show()
    sys.exit(app.exec_())