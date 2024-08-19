from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QApplication,QInputDialog,QDialog
from widget import CanvasWidget,Popup

__author__ = "Juan Cruz Noya"
__country__ = "Argentina"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Juan Cruz Noya"
__email__ = "juancruznoya@unc.ed.ar"
__status__ = "Production"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Asistente de Vision")
        self.setGeometry(100, 100, 1500, 800)

        self.canvas = CanvasWidget(self)
        self.select_kernel = Popup(window_title="Select Kernel", text1="Block Size", text2="C", step=2)
        self.setCentralWidget(self.canvas)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")
        imagen_patron = menubar.addMenu("Pattern Features")
        imagen_tratamiento = menubar.addMenu("image processing")

        openFile = QAction("Open Image", self)
        openFile.triggered.connect(self.open_image)
        fileMenu.addAction(openFile)

        patron = QAction("Search Patterm",self)
        patron.triggered.connect(self.canvas.select_patron)
        imagen_patron.addAction(patron)
        patron2 = QAction("Load Pattern",self)
        patron2.triggered.connect(self.open_patron)
        imagen_patron.addAction(patron2)
        ejes = QAction("Set Coordinate System",self)
        ejes.triggered.connect(self.canvas.ejes)
        imagen_patron.addAction(ejes)
        grayscale = QAction("Apply Gray Scale",self)
        grayscale.triggered.connect(self.canvas.apply_grayscale)
        imagen_tratamiento.addAction(grayscale)
        zoom = QAction("Apply Zoom",self)
        zoom.triggered.connect(self.zoom_selector)
        imagen_tratamiento.addAction(zoom)

        undo = QAction("Undo",self)
        undo.triggered.connect(self.canvas.undo)
        fileMenu.addAction(undo)

        adaptative = QAction("Adaptative Threshold",self)
        adaptative.triggered.connect(self.kernel_selector)
        imagen_tratamiento.addAction(adaptative)

        flip = QAction("Apply Flip",self)
        flip.triggered.connect(self.canvas.apply_flip)
        imagen_tratamiento.addAction(flip)

        save = QAction("Save",self)
        save.triggered.connect(self.canvas.save)
        fileMenu.addAction(save)
    def open_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Seleccione la imagen", "", "Image Files (*.png *.jpg *.bmp *.jpeg)", options=options)
        if file_name:
            self.canvas.load_image(file_name)

    def open_patron(self):
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self,"Seleccione la imagen", "", "Image Files (*.png *.jpg *.bmp *.jpeg)", options=options)
        if path:
            self.canvas.carga_patron(path)

    def zoom_selector(self):
        # Mostrar un diálogo para seleccionar el tamaño del kernel
        zoom, ok = QInputDialog.getInt(self, "Select zoom", "Select zoom:",
                                              min=1, max=4, step=1)
        if ok:
            self.canvas.apply_zoom(zoom)

    def kernel_selector(self):
        dialog = self.select_kernel
        if dialog.exec_() == QDialog.Accepted:
            kernel, c = dialog.getKernels()
            #print(f"Selected Kernels: {kernel1}, {kernel2}")
            self.canvas.apply_threshold_filter(kernel, c)
        else:
            return None, None  # O maneja el caso de cancelación como desees

"""app = QApplication([])
window = MainWindow()
window.show()
app.exec_()"""