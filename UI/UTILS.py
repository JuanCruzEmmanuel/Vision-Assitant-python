import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget, QLabel,QHBoxLayout
from PyQt5.QtGui import QPainter, QImage, QColor, QMouseEvent, QPixmap
from PyQt5.QtCore import Qt, QPoint,pyqtSignal
from superqt import QRangeSlider

class ColorWheel(QWidget):
    colorSelected = pyqtSignal(QColor)
    def __init__(self,parent=None):
        super().__init__(parent) #obtengo todos los atributos del padre
        #self.setFixedSize(300, 350)
        self.setAttribute(Qt.WA_StyledBackground, True)  # Hace que el fondo sea transparente

        #self.color_label = QLabel(self)
        #self.color_label.setGeometry(50, 310, 200, 30)
        #self.color_label.setAlignment(Qt.AlignCenter)
        #self.color_label.setStyleSheet("font-size: 14px; border: 1px solid black; background-color: white;")

        self.color_wheel = self.generate_color_wheel()

        self.color = None

    def generate_color_wheel(self):
        """Genera una imagen con un círculo de colores y fondo transparente."""
        size = 241
        image = QImage(size, size, QImage.Format_ARGB32)
        image.fill(Qt.transparent)  # Fondo transparente

        center = QPoint(size // 2, size // 2)
        radius = size // 2

        for y in range(size):
            for x in range(size):
                dx, dy = x - center.x(), y - center.y()
                distance = (dx**2 + dy**2)**0.5
                if distance <= radius:
                    angle = math.degrees(-math.atan2(dy, dx))  # Convertir a grados
                    angle = (angle + 360) % 360
                    color = QColor.fromHsvF(angle / 360, distance / radius, 1.0)
                    image.setPixelColor(x, y, color)
        
        return image

    def paintEvent(self, event):
        """Dibuja el círculo de colores con fondo transparente."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPixmap(0, 0, QPixmap.fromImage(self.color_wheel))

    def mousePressEvent(self, event: QMouseEvent):
        """Obtiene el color al hacer clic en el círculo."""
        x, y = event.x(), event.y()
        if 0 <= x < self.color_wheel.width() and 0 <= y < self.color_wheel.height():
            color = self.color_wheel.pixelColor(x, y)
            self.colorSelected.emit(color) #Envia la señal
            html_color = color.name()
            self.color = html_color
            #print(html_color)
            #self.color_label.setText(html_color)
            #self.color_label.setStyleSheet(f"background-color: {html_color}; font-size: 14px; border: 1px solid black;")

class RangeSliderWidget(QWidget):
    """
    :Para que funcione se debe instalar la libreria superqt: \n
    Widget para controlar un slicer con rango inicial y final\n
    :min_value: valor inicial (extremo izquierdo). Por defecto =0\n
    :max_value: Valor final (extremo derecho). Por defecto = 255
    """

    rangedValue = pyqtSignal(tuple)
    def __init__(self,min_value:int=0,max_value:int=255):
        """
        Widget para controlar un slicer con rango inicial y final\n
        :min_value: valor inicial (extremo izquierdo). Por defecto =0\n
        :max_value: Valor final (extremo derecho). Por defecto = 255
        """
        super().__init__()
        self.label_min = QLabel(str(min_value))
        self.label_max = QLabel(str(max_value))
        self.slider = QRangeSlider() #Llamo al objeto de superqt
        self.slider.setOrientation(1)  # Horizontal       
        self.slider.setRange(min_value, max_value) #creo en funcion al tamaño que me intrese
        self.slider.setValue((min_value, max_value))
        self.slider.sliderReleased.connect(self.update_values) #En cambio que exista un cambio de valor
        #self.slider.setFixedWidth(140)
        # 🔹 Agregar layout interno
        layout = QHBoxLayout()
        layout.addWidget(self.label_min)
        layout.addWidget(self.slider)
        layout.addWidget(self.label_max)
        self.setLayout(layout)  # 🔹 Importante: establecer layout en el widget

    def update_values(self):
        """
        Señal que emite el valor al main
        """
        values = self.slider.value()
        self.label_min.setText(str(values[0]))  # Actualiza valor izquierdo
        self.label_max.setText(str(values[1]))  # Actualiza valor derecho
        #print(f"Nuevo rango: {values}")  
        self.rangedValue.emit(values) #Señal que emite los valores de cambio
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ColorWheel()
    window.show()
    sys.exit(app.exec_())
