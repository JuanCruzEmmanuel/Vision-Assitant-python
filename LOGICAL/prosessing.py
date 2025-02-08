import cv2,os
import numpy as np
from PyQt5.QtGui import QImage
import matplotlib.pyplot as plt

class ImageProcessor:
    def __init__(self):
        self.cv_image = None #Mantengo los cambios en una imagen "open cv"
        self.patron = None
        self.patrones = []
        self.history = []  # Historial de imágenes
        self.centro_rotacion = (0,0)
        self.angulo_rotacion = 0
        self.rot_hist = [] #Historial de rotacion
        self.binar = False

    def load_image(self, image_path):
        # Cargar la imagen usando OpenCV
        self.cv_image = cv2.imread(image_path)
        if self.cv_image is not None:
            self.centro_rotacion = tuple(np.array(self.cv_image.shape[1::-1]) / 2)
        self.history.append(self.cv_image.copy())  # Guardar estado inicial
        
    def get_qt_image(self):
        if self.cv_image is not None: #Solo funciona si se ha cargado previamente la imagen en formato opencv
            height, width = self.cv_image.shape[:2]
            #print(height,width)
            if len(self.cv_image.shape) == 2:  # Grayscale
                return QImage(self.cv_image.data, width, height,width,QImage.Format_Grayscale8) #Se devuelve en formato Qt escala de grises
            else:  # Color
                return QImage(self.cv_image.data, width, height, 3 * width, QImage.Format_BGR888) #Devuelve en formato Qt color

        return None
    
    def apply_grayscale(self):
        
        """
        Convierte la imagen OCV en blanco y negro
        """
        if self.cv_image is not None: #Si se presiona el boton pero no hay imagen, entonces no hace nada
            if len(self.cv_image.shape) != 2: #Si la imagen no es en blanco y negro (imagen en color  len(shape) = 3)
                self.cv_image = cv2.cvtColor(self.cv_image,cv2.COLOR_BGR2GRAY)
                #cv2.imshow("gs",self.cv_image)
                #cv2.waitKey(0)
                self.history.append(self.cv_image.copy())
            else: #en caso de ser una imagen de len(shape) = 2 entonces no hace nada (eso indica que ya es en blanco y negro)
                pass
            
    def flip(self):
        """
        Rota la imagen OCV
        """
        self.cv_image = cv2.rotate(self.cv_image,cv2.ROTATE_180)
        self.history.append(self.cv_image.copy())
        
    def undo(self):
        """
        Elimina la ultima accion realizada
        """
        if self.cv_image is not None:
            if len(self.history) > 1:
                self.history.pop()
                self.cv_image = self.history[-1]
                

    def PATRON(self,path):
        
        """
        Busca el patron en una imagen cargada
        """
        self.patron = cv2.imread(path,0)
        fig = self.cv_image.copy()
        metodo = cv2.TM_CCOEFF_NORMED
        coincidencias = cv2.matchTemplate(cv2.cvtColor(fig, cv2.COLOR_BGR2GRAY), self.patron, metodo)
        _, max_val, _, max_loc = cv2.minMaxLoc(coincidencias)
        if max_val != 0.0:
            # Obtén las dimensiones del patrón
            ancho_patron, alto_patron = self.patron.shape[::-1]
            punto_inicio = max_loc
            punto_fin = (punto_inicio[0] + ancho_patron, punto_inicio[1] + alto_patron)
        try:
            self.patrones.append((path,(punto_inicio[1],alto_patron, punto_inicio[0],ancho_patron)))
            return punto_inicio[1],alto_patron, punto_inicio[0],ancho_patron #y,h,x,w
        except:
            return 0,0,0,0
        

    def adaptiveThreshold(self,blocksize,c):
        
        """
        Aplica el filtro adaptativo a la imagen OCV
        """
        if self.cv_image is not None:
            try:
                if len(self.cv_image.shape) == 2:
                    #src = cv2.bitwise_not(self.cv_image)
                    self.cv_image = cv2.adaptiveThreshold(self.cv_image,255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                          cv2.THRESH_BINARY,blocksize,c)
                    self.cv_image = cv2.bitwise_not(self.cv_image)
                    self.history.append(self.cv_image.copy())

                else:
                    pass
            except Exception as e:
                print(f"Err01--{e}")
        else:
            pass
        
    def chop_patern(self):
        print(self.patrones[0][1])
        patrones_coordenadas= self.patrones[0][1]
        self.cv_image = self.cv_image[patrones_coordenadas[0]:patrones_coordenadas[0]+patrones_coordenadas[1],patrones_coordenadas[2]:patrones_coordenadas[2]+patrones_coordenadas[3]].copy()
        #cv2.imshow("CHOP",self.cv_image)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        self.history.append(self.cv_image.copy())
        
    def histogram(self):
        
        if len(self.cv_image.shape) == 2:  # blanco y negro
            hist = cv2.calcHist([self.cv_image], [0], None, [256], [0, 256])
            plt.plot(hist, color='black')
            plt.xlabel('Intensidad de píxel')
            plt.ylabel('Frecuencia')
            plt.title('Histograma de imagen en escala de grises')
            plt.show()
        else:
            colores = ('b', 'g', 'r')
            for i, color in enumerate(colores):
                hist = cv2.calcHist([self.cv_image], [i], None, [256], [0, 256])
                plt.plot(hist, color=color)  # Grafica cada canal con su color correspondiente
                
            plt.xlabel('Intensidad de píxel')
            plt.ylabel('Frecuencia')
            plt.title('Histograma de imagen en color')
            plt.show()

    def zoom_image(self,zoom):

        y, x= self.cv_image.shape[:2]
        self.cv_image = cv2.resize(self.cv_image,(x*zoom,y*zoom),interpolation=cv2.INTER_CUBIC)
        self.history.append(self.cv_image.copy())

        return "OK"
    
    def plane_extraction(self,plane,bw):
        """
        Extrae el plano a la imagen cv
        """
        selector = plane
        b, g, r = cv2.split(self.cv_image) #separo los planos de trabajo
        if selector == "RGB - Red Plane":
            #print(1)
            #self.cv_image = cv2.merge([b, g, np.zeros_like(r)]) #Elimino el plano Rojo
            self.cv_image = r
        elif selector == "RGB - Green Plane":
            #print(2)
            #self.cv_image = cv2.merge([b, np.zeros_like(g), r]) #Elimino el plano verde
            self.cv_image = g
        elif selector == "RGB - Blue Plane":
            #print(3)
            #self.cv_image = cv2.merge([np.zeros_like(b), g, r]) #Elimino el plano azul
            self.cv_image = b
        
        #if bw:
            #self.cv_image = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2GRAY)
            
        self.history.append(self.cv_image.copy())
        
        
    def clamp(self,rect,tipe=None):
        """
        Realiza el calculo de las distancias
        Atributos propios del rect:
        {
            rect.y() (inicio del punto)
            rect.height() (altura total, no confundir con posicion final de y (siendo esta y+height))
            rect.x() (inicio del punto)
            rect.width() (ancho total, no confundir con posicion final de x (siendo esta x+width))
        }
        img[rect.y():rect.y()+rect.height() ,rect.x() :rect.x() +rect.width() ] todos estos se deben convertir en int
        
        """
        ROI = self.cv_image[int(rect.y()):int(rect.y())+int(rect.height()),int(rect.x()):int(rect.x())+int(rect.width())]
        COORDS = np.column_stack(np.where(ROI > 0))
        topmost = COORDS[np.argmin(COORDS[:, 0])]
        bottommost = COORDS[np.argmax(COORDS[:, 0])]
        print(f"Punto más arriba en ROI: {topmost}")
        print(f"Punto más abajo en ROI: {bottommost}")
        