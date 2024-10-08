from PyQt5.QtWidgets import QMainWindow, QScrollArea, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QAction, QFileDialog, QApplication, QInputDialog, QDialog
from widget import CanvasWidget, Popup
from PyQt5.QtCore import Qt

__author__ = "Juan Cruz Noya"
__country__ = "Argentina"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Juan Cruz Noya"
__email__ = "juancruznoya@unc.edu.ar"
__status__ = "Production"



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vision Assistant")
        self.setGeometry(100, 100, 1500, 800)
        self.select_kernel = Popup(window_title="Select Kernel", text1="Block Size", text2="C", step=2,min1 =1,min2 =-100)
        self.select_brighandcontrast = Popup(window_title="Select brightness and contrast",text1="Alpha: Contrast factor",
                                             text2="Beta: Brightness factor",step = 0.1,step2 = 0.5,min1 = 0,max1=4,min2 = -100,max2 = 100)
        self.dilate_erode_windows = Popup(window_title="kernel & Iter",text1="Kernel size",text2= "Iterations",
                                          step=2,step2=1,min1 = 1,min2 = 1, max1 = 7, max2=10)
        # Crear un QWidget principal para contener todos los elementos
        main_widget = QFrame(self)
        self.setCentralWidget(main_widget)

        # Crear un layout principal
        main_layout = QHBoxLayout(main_widget)

        # Crear un frame para el área central (donde se cargará la imagen)
        central_frame = QFrame(self)
        central_frame.setFrameShape(QFrame.Box)  # Delimita el frame con un borde
        central_frame.setLineWidth(2)  # Ancho de la línea del borde

        # Crear un CanvasWidget dentro del central_frame para mostrar la imagen
        self.canvas = CanvasWidget(central_frame)
        # Crear un layout vertical para el área central
        central_layout = QVBoxLayout(central_frame)
        central_layout.addWidget(self.canvas)




        right_frame = QFrame(self)
        right_frame.setFrameShape(QFrame.Box)
        right_frame.setLineWidth(2)


        right_layout = QVBoxLayout(right_frame)
        right_label = QLabel("Panel de Controles", right_frame)
        right_layout.addWidget(right_label)
        main_layout.addWidget(right_frame,stretch=1)
        # Añadir el frame central al layout principal
        main_layout.addWidget(central_frame,stretch=10)
        menubar = self.menuBar()
        menubar.clear()  # Borra el menú actual
        fileMenu = menubar.addMenu("File")
        imagen_patron = menubar.addMenu("Pattern Features")
        imagen_tratamiento = menubar.addMenu("Image Processing")

        #if self.canvas.GS:  # Verifica el estado de GS en el momento de la actualización
        #################################################
        gray_scale_menu = menubar.addMenu("Grayscale")
        adaptative = QAction("Adaptive Threshold", self)
        adaptative.triggered.connect(self.kernel_selector)
        gray_scale_menu.addAction(adaptative)
        """----------------------------------------------"""
        dilate = QAction("Dilate image",self)
        dilate.triggered.connect(self.dilateselector)
        gray_scale_menu.addAction(dilate)

        erode = QAction("Erode image",self)
        erode.triggered.connect(self.erodeselector)
        gray_scale_menu.addAction(erode)



        #################################################

        openFile = QAction("Open Image", self)
        openFile.triggered.connect(self.open_image)
        fileMenu.addAction(openFile)

        patron = QAction("Search Pattern", self)
        patron.triggered.connect(self.canvas.select_patron)
        imagen_patron.addAction(patron)

        patron2 = QAction("Load Pattern", self)
        patron2.triggered.connect(self.open_patron)
        imagen_patron.addAction(patron2)

        rec_patron = QAction("Chop a Pattern", self)
        rec_patron.triggered.connect(self.open_patron_for_chop)
        imagen_patron.addAction(rec_patron)

        ejes = QAction("Set Coordinate System", self)
        ejes.triggered.connect(self.canvas.ejes)
        imagen_patron.addAction(ejes)

        grayscale = QAction("Convert to Grayscale", self)
        grayscale.triggered.connect(self.canvas.apply_grayscale)
        imagen_tratamiento.addAction(grayscale)

        zoom = QAction("Zoom", self)
        zoom.triggered.connect(self.zoom_selector)
        imagen_tratamiento.addAction(zoom)

        undo = QAction("Undo", self)
        undo.triggered.connect(self.canvas.undo)
        fileMenu.addAction(undo)



        brigtContr = QAction("Brightness and Contrast",self)
        brigtContr.triggered.connect(self.brightnessAndContrast_selector)
        imagen_tratamiento.addAction(brigtContr)

        flip = QAction("Apply Flip", self)
        flip.triggered.connect(self.canvas.apply_flip)
        imagen_tratamiento.addAction(flip)

        save = QAction("Save", self)
        save.triggered.connect(self.canvas.save)
        fileMenu.addAction(save)



    def open_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select image from Files", "", "Image Files (*.png *.jpg *.bmp *.jpeg)", options=options)
        if file_name:
            self.canvas.load_image(file_name)

    def open_patron(self):
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self,"Select image from Files", "", "Image Files (*.png *.jpg *.bmp *.jpeg)", options=options)
        if path:
            self.canvas.carga_patron(path)

    def open_patron_for_chop(self):
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self,"Select image from Files", "", "Image Files (*.png *.jpg *.bmp *.jpeg)", options=options)
        if path:
            self.canvas.recorte_imagen_directo(path)

    def zoom_selector(self):
        # Mostrar un diálogo para seleccionar el tamaño del kernel
        zoom, ok = QInputDialog.getInt(self, "Select zoom", "Select zoom:",
                                              min=1, max=4, step=1)
        if ok:
            self.canvas.apply_zoom(zoom)

    def kernel_selector(self):
        if self.canvas.GS:
            dialog = self.select_kernel
            if dialog.exec_() == QDialog.Accepted:
                kernel, c = dialog.getValues()
                #print(f"Selected Kernels: {kernel1}, {kernel2}")
                self.canvas.apply_threshold_filter(kernel, c)
            else:
                return None, None

    def brightnessAndContrast_selector(self):
        dialog = self.select_brighandcontrast
        if dialog.exec_() == QDialog.Accepted:
            alpha,beta = dialog.getValues()
            self.canvas.apply_brightnessAndContrast(alpha,beta)
        else:
            return None, None

    def dilateselector(self):
        dialog = self.dilate_erode_windows
        if dialog.exec_() == QDialog.Accepted:
            kernel, iter = dialog.getValues()
            self.canvas.dilate(k=kernel, iter=iter)
        else:
            return None, None

    def erodeselector(self):
        dialog = self.dilate_erode_windows
        if dialog.exec_() == QDialog.Accepted:
            kernel, iter = dialog.getValues()
            self.canvas.erode(k=kernel, iter=iter)
        else:
            return None, None


app = QApplication([])
window = MainWindow()
window.show()
app.exec_()