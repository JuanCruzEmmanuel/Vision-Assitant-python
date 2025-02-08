from PyQt5.QtWidgets import QWidget, QInputDialog,QDialog,QVBoxLayout, QSpinBox, QLabel, QDialogButtonBox,QDoubleSpinBox
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect, QPoint
from LOGICAL.prosessing import ImageProcessor
import pickle

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.processor = ImageProcessor()
        self.qt_image = None #Mantengo una imagen en formato Qt_imagen
        self.start_point = None
        self.end_point = None
        self.rectangles = []  # Lista de tuplas (QRect, etiqueta, color)
        self.patrones = []
        self.scale_factor = 1.0  # Factor de escala inicial
        self.translation = QPoint(0, 0)  # Para el desplazamiento
        self.last_mouse_pos = None  # Para seguimiento del movimiento del ratón
        self.patron = False
        self._CLANP_FLAG = False #Controla la señal de CLAMP
        self._CLAMP_HISTORY = [] #Guardo los clamps que se realicen
        self.ejes_ = False
        self.save_actions = []
        self.GS = False
        
        
    def load_image(self, file_name):
        self.processor.load_image(file_name) #Cargo la imagen para trabajarla como opencv
        self.qt_image = self.processor.get_qt_image()
        self.rectangles = []  # Resetear recuadros al cargar una nueva imagen
        self.scale_factor = 1.0  # Resetear escala al cargar una nueva imagen
        self.translation = QPoint(0, 0)
        self.save_actions.append(("load_image",file_name)) #importante para tener el pipeline
        self.update() #Actualizo los eventos
        
        
    def paintEvent(self, event):#Muy importate mantener el nombre de este metodo, ya que no se ejecuta como un evento de dibujado Qt image
        #Siempre y cuando se realice un evento de tipo Qt 
        #Para cargar la imagen y que se muestre en pantalla
        
        #print(self.patrones)
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
                
    def mousePressEvent(self, event):#Muy importate mantener el nombre de este metodo, ya que no se ejecuta como un evento de dibujado Qt image
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos() / self.scale_factor - self.translation / self.scale_factor
            self.end_point = self.start_point
        elif event.button() == Qt.RightButton:
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):#Muy importate mantener el nombre de este metodo, ya que no se ejecuta como un evento de dibujado Qt image
        if self.start_point:
            self.end_point = event.pos() / self.scale_factor - self.translation / self.scale_factor
            self.update()
        elif self.last_mouse_pos:
            # Movimiento del mouse con el botón derecho presionado para desplazar la imagen
            delta = event.pos() - self.last_mouse_pos
            self.translation += delta
            self.last_mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):#Muy importate mantener el nombre de este metodo, ya que no se ejecuta como un evento de dibujado Qt image
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
            if self._CLANP_FLAG:
                print("generic_name")
                #print(rect)
                self.processor.clamp(rect=rect)

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

    def wheelEvent(self, event):#Muy importate mantener el nombre de este metodo, ya que no se ejecuta como un evento de dibujado Qt image
        # Ajuste del factor de escala según la rueda del mouse
        delta = event.angleDelta().y()
        if delta > 0:
            self.scale_factor *= 1.1
        else:
            self.scale_factor /= 1.1
        self.update()
        

    def apply_grayscale(self):
        """
        Funcion encargada de convertir la imagen en blanco y negro.
        """
        self.processor.apply_grayscale() #envia la señal para convertir la imagen ocv en blanco y negro
        self.qt_image = self.processor.get_qt_image() #Convierte la imagen ocv en formato Qt
        self.save_actions.append(("apply_grayscale",0))
        self.GS = True #atributo que se activa cuando se convierte la imagen en blanco y negro, y acciona sobre el proseso de la imagen
        self.update()
        
    def apply_flip(self):
        
        """
        Se encarga de rotar 180º la imagen
        """
        if self.processor.cv_image is not None: #Si no hay imagen entonces no hace nada
            self.processor.flip() #Rota la imagen OCV
            self.qt_image = self.processor.get_qt_image() #Carga la imagen en momoria
            self.save_actions.append(("apply_flip",0))
            self.update()
        
    def undo(self):
        
        """
        Se debe agregar una funcion para eliminar la ultima accion
        """
        if len(self.save_actions)>1: #debo agregar una linea para evitar que exista un error
            self.processor.undo()
            self.qt_image = self.processor.get_qt_image()
            self.save_actions.pop()
            self.update()
            
    def select_pattern(self,path):
        
        """
        Se encarga de recuadrar una imagen patron
        """
        if self.processor.cv_image is not None:
            y,h,x,w = self.processor.PATRON(path)
            rect = QRect(x,y,w,h)
            #print(rect)
            self.patrones.append((rect,"Patron"))
            self.save_actions.append(("load_patern", path))
            self.update()
            
    def apply_threshold_filter(self,kernel,c):
        
        """
        Aplica filtro de umbralizado. Se debe seleccionar el kernel y la matriz C
        """
        
        if self.processor.cv_image is not None:
            if self.GS:
                self.processor.adaptiveThreshold(kernel,c)
                self.qt_image = self.processor.get_qt_image()
                self.save_actions.append(("apply_threshold_filter", kernel,c))
                self.update()
                
    def save(self):
        #print(self.save_actions)
        with open("data.pkl", "wb") as f:
            pickle.dump(self.save_actions, f)
            

    def chop_loaded_pattern(self):
        if self.processor.cv_image is not None:
            if self.processor.patron is not None:
                self.processor.chop_patern()
                self.qt_image = self.processor.get_qt_image()
                self.save_actions.append(("chop_loaded_pattern",self.processor.patrones[0][1])) #Esto lo mejor es de alguna forma seleccionarlo por el nombre
                self.patrones = [] #Este detallo va a llevar tiempo mejorarlo, pero no es conveniente eliminarlo...
                self.update()
                
    def view_hisogram(self):
        if self.processor.cv_image is not None: # No se ejecuta en caso que no haya imagen cargada
            self.processor.histogram()

    def apply_zoom(self,zoom):
        """
        Aplica un cambio de escala a la imagen cargada una cantidad de veces deseada

        :param zoom: inidice de multiplicador
        """

        if zoom >6:
            zoom = 6
        elif zoom<0:
            zoom = 1

        self.processor.zoom_image(zoom)
        self.qt_image = self.processor.get_qt_image()
        self.save_actions.append(("apply_zoom",zoom))

        self.update()

    def get_cv_image(self):
        """
        Devuelve la imagen en CV para trabajar en alguna otra pantalla en caso de necesitarse (Util para acceder desde el main menu)

        :return: imagen en formato cv
        """

        return self.processor.cv_image


    def apply_plane_extraction(self,plane,bw):
        """
        Funcion que trabaja con la extraccion de planos especificos
        :plane: Plano de trabajo
        :bw: booleano que trabaja para convertir o no en blanco y negro
        
        """
        
        self.processor.plane_extraction(plane=plane,bw=bw)
        self.qt_image = self.processor.get_qt_image() #subo la imagen en qt
        self.GS = True #Hay que tener cuidado con esto, cuando se hace UNDO no va eliminar esta bandera, asi que deberia hacer una funcion que la elimine
        self.save_actions.append(("apply_plane_extraction",plane,bw))
        
        self.update()
        
    def apply_clamp(self):
        """
        Activa la flag del clamp
        """
        self._CLANP_FLAG = True