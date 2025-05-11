import cv2,os
import numpy as np
from PyQt5.QtGui import QImage
import matplotlib.pyplot as plt
import easyocr
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
        self.ocr = easyocr.Reader(['es', 'en']) #Creo el objeto que lee
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
        Aplica el filtro adaptativo a la imagen OCV\n
        :blocksize: Size of a pixel neighborhood that is used to calculate a threshold value for the pixel: 3, 5, 7, and so on.\n
        :c: Constant subtracted from the mean or weighted mean (see the details below). Normally, it is positive but may be zero or negative as well.
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
        """
        En caso de cargar un patron lo puede recortar. \n
        
        Hay que buscar la forma que seleccionar varios patrones en simultaneo
        """
        
        print(self.patrones[0][1])
        patrones_coordenadas= self.patrones[0][1]
        self.cv_image = self.cv_image[patrones_coordenadas[0]:patrones_coordenadas[0]+patrones_coordenadas[1],patrones_coordenadas[2]:patrones_coordenadas[2]+patrones_coordenadas[3]].copy()
        #cv2.imshow("CHOP",self.cv_image)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        self.history.append(self.cv_image.copy())
        
    def histogram(self):
        """
        Calcula el histograma para luego mostrarlo en pantalla
        """
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
        """
        Aplica el zoom a la imagen CV\n
        :zoom: Constante que controla el zoom, entre 1 y 6
        """

        y, x= self.cv_image.shape[:2]
        self.cv_image = cv2.resize(self.cv_image,(x*zoom,y*zoom),interpolation=cv2.INTER_CUBIC)
        self.history.append(self.cv_image.copy())

        return "OK"
    
    def plane_extraction(self,plane,bw):
        """
        Extrae el plano a la imagen cv\n
        :plane: El plano que se va a extraer para trabajar\n
        :bw: Antes se trabajaba con un boton bw, pero ahora es siempre asi
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
        Realiza el calculo de las distancias\n
        Atributos propios del rect:\n
        {
            rect.y() (inicio del punto)\n
            rect.height() (altura total, no confundir con posicion final de y (siendo esta y+height))\n
            rect.x() (inicio del punto)\n
            rect.width() (ancho total, no confundir con posicion final de x (siendo esta x+width))\n
        }\n
        img[rect.y():rect.y()+rect.height() ,rect.x() :rect.x() +rect.width() ] todos estos se deben convertir en int\n
        
        """
        ROI = self.cv_image[int(rect.y()):int(rect.y())+int(rect.height()),int(rect.x()):int(rect.x())+int(rect.width())]
        COORDS = np.column_stack(np.where(ROI > 0))
        topmost = COORDS[np.argmin(COORDS[:, 0])]
        bottommost = COORDS[np.argmax(COORDS[:, 0])]
        print(f"Punto más arriba en ROI: {topmost}")
        print(f"Punto más abajo en ROI: {bottommost}")
        
    def OCR(self,rect):
        try:
            ROI = self.cv_image[int(rect.y()):int(rect.y())+int(rect.height()),int(rect.x()):int(rect.x())+int(rect.width())]
            read =self.ocr.readtext(ROI)
            TEXTO = ""
            for (bbox, text, prob) in read:
                print(f'Texto: {text}, Confianza: {prob:.2f}')
                if TEXTO == "":
                    TEXTO = text
                else:
                    TEXTO +=" "+text
            return TEXTO
        except:
            print("ERROR")
    def color_operators(self,operation,color):
        """
        Aplica la operacion seleccionada a la imagen CV\n
        :operation: Operacion seleccionada\n
        :color: Color en formato tupla (B,G,R)\n
        """
        
        R = color[2] #Obtengo las componente en rojo
        B = color[0] #Obtengo las componente en azul
        G = color[1] #obtengo las componente en verde
        selector = operation #Tal vez no se vea tan elegante, pero funciona dafac :)

        if selector =="Add":
            NP_COLOR = np.array([B,G,R],dtype=np.uint8)
            self.cv_image = cv2.add(self.cv_image,NP_COLOR)
        elif selector =="Subtract":
            NP_COLOR = np.array([B,G,R],dtype=np.uint8)
            self.cv_image = cv2.subtract(self.cv_image,NP_COLOR)
        elif selector =="Multiply":
            NP_COLOR = np.array([B/255,G/255,R/255],dtype=np.float32)
            self.cv_image = cv2.multiply(self.cv_image.astype(np.float32) ,NP_COLOR)
        elif selector =="Divide":
            try:
                NP_COLOR = np.array([255/B,255/G,255/R],dtype=np.float32)
                self.cv_image = cv2.divide(self.cv_image,NP_COLOR)
            except:
                self.cv_image = self.cv_image
        elif selector =="Absolute Difference":
            NP_COLOR = np.array([B,G,R],dtype=np.uint8)
            self.cv_image = cv2.absdiff(self.cv_image,NP_COLOR)
        elif selector =="Modulo":
            #NP_COLOR = np.array([1/B,1/G,1/R],dtype=np.uint8)
            self.cv_image = self.cv_image % np.array([B,G,R],dtype=np.uint8)
            
        elif selector =="And":
            NP_COLOR = np.array([B,G,R],dtype=np.uint8)
            self.cv_image = cv2.bitwise_and(self.cv_image,NP_COLOR)
        elif selector =="Not And":
            NP_COLOR = np.array([B,G,R],dtype=np.uint8)
            self.cv_image = cv2.bitwise_not(cv2.bitwise_and(self.cv_image,NP_COLOR))#Le aplico el not para hacer el inverso del and
        elif selector =="Or":
            NP_COLOR = np.array([B,G,R],dtype=np.uint8)
            self.cv_image = cv2.bitwise_or(self.cv_image,NP_COLOR)
        elif selector =="Not Or":
            NP_COLOR = np.array([B,G,R],dtype=np.uint8)
            self.cv_image = cv2.bitwise_not(cv2.bitwise_or(self.cv_image,NP_COLOR))
        elif selector == "Exclusive Or":
            NP_COLOR = np.array([B,G,R],dtype=np.uint8)
            self.cv_image = cv2.bitwise_xor(self.cv_image,NP_COLOR)
        elif selector =="Not Exclusive Or":
            NP_COLOR = np.array([B,G,R],dtype=np.uint8)
            self.cv_image = cv2.bitwise_not(cv2.bitwise_xor(self.cv_image,NP_COLOR))              
        else:
            self.cv_image = self.cv_image
            
        
        self.history.append(self.cv_image.copy())
        
        
    def color_manipulation(self,operation,range1,range2,color):
        """
        Modifica la imagen opencv\n
        :operation: substraction/change\n
        :range1: rango color 1 en hsv\n
        :range2: 2 rango de color en hsv\n
        :color: Color que va a reemplazar
        """
        #Realizo el metodo de unpack la tupla
        HUE1,SAT1,VAL1 = range1 
        HUE2,SAT2,VAL2 = range2
        
        if operation == "Substract":
            #print("ingrese papu")
            im_temp = self.cv_image.copy()
            HSV_IMAGE = cv2.cvtColor(self.cv_image,cv2.COLOR_BGR2HSV) #Cambio el plano de trabajo

            #para trabajar las imagenes voy a tener que usar los colores maximos y minimos
            #(hue,sat,value)
            low_color_1 = np.array([HUE1[0],SAT1[0],VAL1[0]])
            high_color_1 = np.array([HUE1[1],SAT1[1],VAL1[1]])
            mask = cv2.inRange(HSV_IMAGE, low_color_1, high_color_1)
        
            if HUE2[1]-HUE2[0]<100: #Totalmente arbitrario
                low_color_2 = np.array([HUE2[0],SAT2[0],VAL2[0]])
                high_color_2 = np.array([HUE2[1],SAT2[1],VAL2[1]])
                mask2 = cv2.inRange(HSV_IMAGE, low_color_2, high_color_2)
                
                mask = cv2.bitwise_or(mask,mask2) #En caso que exista, los uno
            

            im_temp[mask > 0] = [0, 0, 0]
            
            self.cv_image = im_temp
            
            self.history.append(self.cv_image.copy())
        elif operation =="Change":
            R,G,B = color
            
            im_temp = self.cv_image.copy()
            HSV_IMAGE = cv2.cvtColor(self.cv_image,cv2.COLOR_BGR2HSV) #Cambio el plano de trabajo

            #para trabajar las imagenes voy a tener que usar los colores maximos y minimos

            low_color_1 = np.array([HUE1[0],SAT1[0],VAL1[0]])
            high_color_1 = np.array([HUE1[1],SAT1[1],VAL1[1]])
            mask = cv2.inRange(HSV_IMAGE, low_color_1, high_color_1)
        
            if HUE2[1]-HUE2[0]<100: #Totalmente arbitrario
                low_color_2 = np.array([HUE2[0],SAT2[0],VAL2[0]])
                high_color_2 = np.array([HUE2[1],SAT2[1],VAL2[1]])
                mask2 = cv2.inRange(HSV_IMAGE, low_color_2, high_color_2)
                
                mask = cv2.bitwise_or(mask,mask2) #En caso que exista, los uno
                
            im_temp[mask > 0] = [B[1], G[1], R[1]] #Lo cambio por el color deseado
            
            self.cv_image = im_temp
            
            self.history.append(self.cv_image.copy())
        else:
            print("ERROR")