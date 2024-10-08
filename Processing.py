import cv2,os
import numpy as np
from PyQt5.QtGui import QImage

class ImageProcessor:
    def __init__(self):
        self.cv_image = None
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


    def select_patron(self,y1,y2,x1,x2,nombre):
        print(y1,y2,x1,x2)
        muestra = self.cv_image.copy()
        muestra = muestra[y1:y1+y2, x1:x1+x2]
        cv2.imwrite(nombre+".jpeg",muestra)


    def color_mask(self,range,range_2=None):
        pass

    def PATRON(self,path):
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

    def recorte_directo(self,path):
        self.patron = cv2.imread(path,0)
        fig = self.cv_image.copy()
        metodo = cv2.TM_CCOEFF_NORMED
        coincidencias = cv2.matchTemplate(cv2.cvtColor(fig, cv2.COLOR_BGR2GRAY), self.patron, metodo)
        _, max_val, _, max_loc = cv2.minMaxLoc(coincidencias)
        if max_val != 0.0:
            ancho_patron, alto_patron = self.patron.shape[::-1]
            punto_inicio = max_loc
            punto_fin = (punto_inicio[0] + ancho_patron, punto_inicio[1] + alto_patron)

        print(ancho_patron,alto_patron)
        print(punto_inicio)
        self.cv_image = self.cv_image[punto_inicio[1]:punto_inicio[1]+alto_patron,punto_inicio[0]:punto_inicio[0]+ancho_patron].copy()
        #cv2.imshow("test",self.cv_image)
        #cv2.waitKey(0)
        self.history.append(self.cv_image.copy())


    def ejes(self):
        y,h,x,w = self.patrones[-1][1]
        return y,h,x,w

    def apply_grayscale(self):
        if self.cv_image is not None:
            if len(self.cv_image.shape) != 2:
                self.cv_image = cv2.cvtColor(self.cv_image,cv2.COLOR_BGR2GRAY)
                #cv2.imshow("gs",self.cv_image)
                #cv2.waitKey(0)
                self.history.append(self.cv_image.copy())
            else:
                pass

    def undo(self):
        if self.cv_image is not None:
            if len(self.history) > 1:
                self.history.pop()
                self.cv_image = self.history[-1]

    def resize(self,zoom):

        if self.cv_image is not None:
            if len(self.cv_image.shape) == 3:  # colored image
                y, x, _ = self.cv_image.shape
                if zoom >= 1:
                    y_zoomed = y*zoom
                    x_zoomed = x*zoom
                    self.cv_image = cv2.resize(self.cv_image, (x_zoomed, y_zoomed), interpolation=cv2.INTER_CUBIC)
                    self.history.append(self.cv_image.copy())
                else:
                    y_zoomed = y*zoom
                    x_zoomed = x*zoom
                    self.cv_image = cv2.resize(self.cv_image, (x_zoomed, y_zoomed), interpolation=cv2.INTER_AREA)
                    self.history.append(self.cv_image.copy())
            else:  # GS image
                y, x = self.cv_image.shape
                if zoom >= 1:
                    y_zoomed = y * zoom
                    x_zoomed = x * zoom
                    self.cv_image = cv2.resize(self.cv_image, (x_zoomed, y_zoomed), interpolation=cv2.INTER_CUBIC)
                    self.history.append(self.cv_image.copy())
                else:
                    y_zoomed = y * zoom
                    x_zoomed = x * zoom
                    self.cv_image = cv2.resize(self.cv_image, (x_zoomed, y_zoomed), interpolation=cv2.INTER_AREA)
                    self.history.append(self.cv_image.copy())

    def adaptiveThreshold(self,blocksize,c):
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

    def flip(self):
        self.cv_image = cv2.rotate(self.cv_image,cv2.ROTATE_180)
        self.history.append(self.cv_image.copy())

    def DILATE(self,kernel,iter):
        if self.cv_image is not None:

            KERNEL = np.ones((kernel,kernel),np.uint8)

            self.cv_image = cv2.dilate(self.cv_image,kernel=KERNEL,iterations=iter)

            self.history.append(self.cv_image.copy())

    def ERODE(self,kernel,iter):
        if self.cv_image is not None:

            KERNEL = np.ones((kernel,kernel),np.uint8)

            self.cv_image = cv2.erode(self.cv_image,kernel=KERNEL,iterations=iter)

            self.history.append(self.cv_image.copy())

    def brightnessAndContrast(self,alpha,beta):
        """

        :param alpha: contrast factor
        :param beta: brightness factor
        :return: alpha*image+beta
        """

        self.cv_image = cv2.convertScaleAbs(self.cv_image,alpha = alpha, beta= beta)
        self.history.append(self.cv_image.copy())

    def get_qt_image(self):
        if self.cv_image is not None:
            height, width = self.cv_image.shape[:2]
            print(height,width)
            if len(self.cv_image.shape) == 2:  # Grayscale
                return QImage(self.cv_image.data, width, height,width,QImage.Format_Grayscale8)
            else:  # Color
                return QImage(self.cv_image.data, width, height, 3 * width, QImage.Format_BGR888)

        return None


def Pipeline(src=None,pipe=None):
    """

    :param src: cv2 image
    :param pipe: tuple with pipeline action
    :return: proccesing cv2 image
    """

    app = pipe[0]
    if app == "load_image":
        src = cv2.imread(pipe[1])
        return src
        """
        pipe[1]: image PATH 
        """


    elif app == "apply_grayscale":
        src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        return src


    elif app =="apply_zoom":
        if len(src.shape) == 3:
            y, x, _ = src.shape
            src = cv2.resize(src, (x*pipe[1], y*pipe[1]), cv2.INTER_CUBIC)
            return src
        else:
            y, x = src.shape
            src = cv2.resize(src,(x*pipe[1], y*pipe[1]), cv2.INTER_CUBIC)
            return src
    elif app == "apply_threshold_filter":
        if len(src.shape) == 2:
            src = cv2.bitwise_not(src)
            src = cv2.adaptiveThreshold(src, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                  cv2.THRESH_BINARY, pipe[1], pipe[2])
            return src

    elif app == "apply_flip":
        return cv2.rotate(src, cv2.ROTATE_180)


