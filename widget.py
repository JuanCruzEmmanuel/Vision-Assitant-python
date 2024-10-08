from PyQt5.QtWidgets import QWidget, QInputDialog,QDialog,QVBoxLayout, QSpinBox, QLabel, QDialogButtonBox,QDoubleSpinBox
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect, QPoint
from Processing import ImageProcessor
import pickle

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.processor = ImageProcessor()
        self.qt_image = None
        self.start_point = None
        self.end_point = None
        self.rectangles = []  # Lista de tuplas (QRect, etiqueta, color)
        self.patrones = []
        self.scale_factor = 1.0  # Factor de escala inicial
        self.translation = QPoint(0, 0)  # Para el desplazamiento
        self.last_mouse_pos = None  # Para seguimiento del movimiento del ratón
        self.patron = False
        self.ejes_ = False
        self.save_actions = []
        self.GS = False
    def load_image(self, file_name):
        self.processor.load_image(file_name)
        self.qt_image = self.processor.get_qt_image()
        self.rectangles = []  # Resetear recuadros al cargar una nueva imagen
        self.scale_factor = 1.0  # Resetear escala al cargar una nueva imagen
        self.translation = QPoint(0, 0)
        self.save_actions.append(("load_image",file_name))
        self.update()

    def paintEvent(self, event):

        #Para cargar la imagen y que se muestre en pantalla
        if self.qt_image:
            painter = QPainter(self)
            painter.translate(self.translation)  # Aplicar desplazamiento
            painter.scale(self.scale_factor, self.scale_factor)  # Aplicar escala
            painter.drawImage(0, 0, self.qt_image)
            for rect, label, color in self.rectangles:
                painter.setPen(QPen(color, 2, Qt.SolidLine))
                painter.drawRect(rect)
                painter.drawText(rect.topLeft(), label)


            for rect, label in self.patrones:
                painter.setPen(QPen(Qt.green, 2, Qt.SolidLine))
                painter.drawRect(rect)
                painter.drawText(rect.topLeft(), label)
                if self.ejes_ == True:
                    painter_line = QPainter(self)
                    painter_line.translate(self.translation)  # Aplicar desplazamiento
                    painter_line.scale(self.scale_factor, self.scale_factor)  # Aplicar escala
                    painter_line.setPen(QPen(Qt.red, 2, Qt.DashDotLine))
                    y,h,x,w = self.processor.ejes()
                    painter_line.drawLine(x-10,(y+h)//2,x+w+10,(y+h)//2)
                    painter_line.drawLine((2*x+w)//2, y-10, (2*x+w)//2, y+h +10)
            if self.start_point and self.end_point:
                painter.setPen(QPen(Qt.blue, 2, Qt.DashLine))  # Color provisional del recuadro
                painter.drawRect(QRect(self.start_point, self.end_point))


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos() / self.scale_factor - self.translation / self.scale_factor
            self.end_point = self.start_point
        elif event.button() == Qt.RightButton:
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.start_point:
            self.end_point = event.pos() / self.scale_factor - self.translation / self.scale_factor
            self.update()
        elif self.last_mouse_pos:
            # Movimiento del mouse con el botón derecho presionado para desplazar la imagen
            delta = event.pos() - self.last_mouse_pos
            self.translation += delta
            self.last_mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.start_point:
            self.end_point = event.pos() / self.scale_factor - self.translation / self.scale_factor
            rect = QRect(self.start_point, self.end_point)
            if self.patron == True:
                nombre_patron, ok = QInputDialog.getText(self, "Patron", "Nombre:")
                if ok and nombre_patron:
                    self.processor.select_patron(int(rect.y()),
                                                 int(rect.height()),int(rect.x()),
                                                 int(rect.width()),nombre_patron)
                    self.patrones.append((rect,nombre_patron))

                    self.patron = False

            # Obtener la etiqueta del usuario
            #label, ok = QInputDialog.getText(self, "Etiqueta", "Ingrese la etiqueta:")
            #if ok and label:
                #color = self.get_color_for_label(label)
                #self.rectangles.append((rect, label, color))

            self.start_point = None
            self.end_point = None
            self.update()
        elif event.button() == Qt.RightButton:
            self.last_mouse_pos = None

    def wheelEvent(self, event):
        # Ajuste del factor de escala según la rueda del mouse
        delta = event.angleDelta().y()
        if delta > 0:
            self.scale_factor *= 1.1
        else:
            self.scale_factor /= 1.1
        self.update()

    def get_color_for_label(self, label):
        # Asignar un color específico basado en la etiqueta
        hash_code = hash(label) % 255
        return QColor(hash_code, 255 - hash_code, (hash_code * 2) % 255)

    def delete_last_rectangle(self):
        if self.rectangles:
            self.rectangles.pop()
            self.update()

    def apply_grayscale(self):
        self.processor.apply_grayscale()
        self.qt_image = self.processor.get_qt_image()
        self.save_actions.append(("apply_grayscale",0))
        self.GS = True
        self.update()

    def apply_zoom(self, zoom):
        self.processor.resize(zoom)
        self.qt_image = self.processor.get_qt_image()
        self.save_actions.append(("apply_zoom",zoom))
        self.update()

    def apply_blur(self, kernel_size=5):
        if self.processor.cv_image is not None:
            # Verifica que el tamaño del kernel sea impar y mayor que 0
            if kernel_size % 2 == 0:
                kernel_size += 1
            self.processor.apply_blur(kernel_size)
            self.save_actions.append(("apply_blur", kernel_size))
            self.qt_image = self.processor.get_qt_image()
            self.update()

    def undo(self):
        self.processor.undo()
        self.qt_image = self.processor.get_qt_image()
        self.save_actions.pop()
        self.update()

    def rotacion(self, angulo=0):
        if self.processor.cv_image is not None:
            self.processor.rotacion(angulo)
            self.qt_image = self.processor.get_qt_image()
            self.update()

    def select_patron(self):
        if self.processor.cv_image is not None:
            self.patron = True
            self.update()

    def carga_patron(self,path):
        if self.processor.cv_image is not None:
            y,h,x,w = self.processor.PATRON(path)
            rect = QRect(x,y,w,h)
            print(rect)
            self.patrones.append((rect,"Patron"))
            self.save_actions.append(("load_patern", path))
            self.update()

    def recorte_imagen_directo(self,path):
        if self.processor.cv_image is not None:
            self.processor.recorte_directo(path)
            self.qt_image = self.processor.get_qt_image()
            print("aa")
            self.update()


    def ejes(self):
        if self.processor.cv_image is not None:
            if self.ejes_ == False:
                self.ejes_ =True
                self.update()
            else:
                self.ejes_ =False
                self.update()

    def apply_threshold_filter(self,kernel,c):
        if self.processor.cv_image is not None:
            if self.GS:
                self.processor.adaptiveThreshold(kernel,c)
                self.qt_image = self.processor.get_qt_image()
                self.save_actions.append(("apply_threshold_filter", kernel,c))
                self.update()

    def apply_flip(self):
        if self.processor.cv_image is not None:
            self.processor.flip()
            self.qt_image = self.processor.get_qt_image()
            self.save_actions.append(("apply_flip",0))
            self.update()

    def apply_brightnessAndContrast(self,alpha,beta):
        if self.processor.cv_image is not None:
            self.processor.brightnessAndContrast(alpha,beta)
            self.qt_image = self.processor.get_qt_image()
            self.save_actions.append(("apply_brightnessAndContrast",alpha,beta))
            self.update()

    def save(self):
        print(self.save_actions)
        with open("data.pkl", "wb") as f:
            pickle.dump(self.save_actions, f)

    def dilate(self,k,iter):

        self.processor.DILATE(kernel=k,iter=iter)
        self.qt_image = self.processor.get_qt_image()
        self.save_actions.append(("dilate", k, iter))
        self.update()

    def erode(self,k,iter):
        self.processor.ERODE(kernel=k,iter=iter)
        self.qt_image = self.processor.get_qt_image()
        self.save_actions.append(("erode", k, iter))
        self.update()


    @property
    def update_status(self):
        return self.GS
    @update_status.setter
    def update_status(self,value):
        if self.GS !=value:
            self.GS =value
            self.GS_changed.emit(self.GS)
class Popup(QDialog):
    def __init__(self,window_title,text1,text2="",step=1,step2=0, min1=0, min2=0, max1=100, max2=100):
        super().__init__()

        self.setWindowTitle(window_title)

        # Layout principal
        layout = QVBoxLayout()

        # Selección del primer kernel
        if isinstance(step,float) == True:
            self.value1_input = QDoubleSpinBox(self)
        else:
            self.value1_input = QSpinBox(self)
        self.value1_input.setRange(min1, max1)
        self.value1_input.setSingleStep(step)
        layout.addWidget(QLabel(text1))
        layout.addWidget(self.value1_input)


        if text2=="":
            pass
        else:
            if isinstance(step2,float) == True:
                self.value2_input = QDoubleSpinBox(self)
            else:
                self.value2_input = QSpinBox(self)
            self.value2_input.setRange(min2, max2)
            if step2 == 0: #Si no se especifica, entonces se selecciona el mismo
                step2 = step
            self.value2_input.setSingleStep(step2)
            layout.addWidget(QLabel(text2))
            layout.addWidget(self.value2_input)

        # Botones OK y Cancelar
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

        # Aplicar layout
        self.setLayout(layout)

    def getValues(self):
        if self.value2_input is not None:
            return self.value1_input.value(), self.value2_input.value()
        else:
            return self.value1_input.value()

