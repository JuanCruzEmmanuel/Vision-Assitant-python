from PyQt5.QtWidgets import QWidget, QInputDialog,QDialog,QVBoxLayout, QSpinBox, QLabel, QDialogButtonBox,QDoubleSpinBox
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect, QPoint,pyqtSignal
from LOGICAL.prosessing import ImageProcessor
import pickle
import sys
import os
import json
import cv2

class logger:
    def __init__ (self,text=None,debug=True):
        self.text = text
        self.debug = debug
    def set_text(self,text):
        self.text = text
    def printer(self):
        if self.text!=None:
            if self.debug:
                print(self.text)
            else:
                pass
        else:
            pass
        

class CanvasWidget(QWidget):
    patrones_lista = pyqtSignal(list) #Señal que se envia para controlar la tabla de patrones
    ocr_lista = pyqtSignal(list) #Señal que controla la tabla de ocr
    numeric_list = pyqtSignal(list) #Señal que controla la lista numerica
    def __init__(self, parent=None,ocr=None):
        super().__init__(parent)
        self.ocr = ocr
        self.processor = ImageProcessor(ocr=self.ocr)
        self.qt_image = None #Mantengo una imagen en formato Qt_imagen
        self.start_point = None
        self.end_point = None
        self.rectangles = []  # Lista de tuplas (QRect, etiqueta, color)
        self.patrones = []
        self.patrones_PATH  = [] #Para guardar los path por seguridad
        self.scale_factor = 1.0  # Factor de escala inicial
        self.translation = QPoint(0, 0)  # Para el desplazamiento
        self.last_mouse_pos = None  # Para seguimiento del movimiento del ratón
        self.patron = False
        self.CLAMP_FLAG = False #Controla la señal de CLAMP
        self._CLAMP_HISTORY = [] #Guardo los clamps que se realicen
        self.ejes_ = False
        self.save_actions = []
        self.GS = False
        self.SOURCE_FOLDER = None
        self.DESTINATION_FOLDER = None
        self.scrip_path = None
        self.OCR_FLAG = False #Variable que controla la accion de el reconocimiento de caracteres en imagen (OCR)
        self.OCR_LIST = []
        
        self.NUMERIC_FLAG = False
        self.NUMERIC_LIST = [] #lista para almacenar los datos
        self.INDEX_NUMERIC = -1 #Significa que no tengo nada
        #self.ocr = easyocr.Reader(['es', 'en'])
    def get_patern_list(self):
        
        """
        Devuelve la lista de patrones
        """   
        
        return self.patrones, self.patrones_PATH
    
    def get_ocr_list(self):
        """
        Devuelve la lista de OCR
        """
        return self.OCR_LIST
    
    def set_patrones_list(self,patrones,patrones_path):
        """
        Carga la lista de los patrones
        """
        
        self.patrones = patrones
        self.patrones_PATH = patrones_path
        self.update() #Actualizo los eventos
        
    def set_ocr_list(self,OCR_list):
        """
        Actualiza la lista de OCR
        """
        self.OCR_LIST = OCR_list
        self.update()
         
    def get_numeric_list(self):
        """
        Devuelve la lista numerica
        """
        return self.NUMERIC_LIST
    def set_numeric_list(self,lista_numerica):
        """
        Setea la lista numerica de manera externa
        """
        self.NUMERIC_LIST = lista_numerica
    def save_scripts(self,name="data",path = None):
        """
        Se guardara el scripts en un primer momento formato pickle\n
        :path: Direccion donde se guardara el scripts
        """
        name = "data" #Hasta que no se elija el nombre externamente, que se guarde como data... lo pongo aca, porque de por si esta como false
        if path==None:
            #En caso que no se especifique se guardara en /root/
            with open(f"{name}.pkl", "wb") as f:
                pickle.dump(self.save_actions, f)
                
        else:
            try: #En caso que ponga mal la direccion
                with open(fr"{path}/{name}.pkl", "wb") as f: #Puede ser que el slash sea para el otro lado
                    pickle.dump(self.save_actions, f)
            except:
                with open(f"{name}.pkl", "wb") as f:
                    pickle.dump(self.save_actions, f)
        
        print("Se ha guardado el script de manera correcta")
        for N,ACTION in enumerate(self.save_actions):
            print(f"Accion {N}: {ACTION[0]}")
    def load_image(self, file_name):
        self.processor.load_image(file_name) #Cargo la imagen para trabajarla como opencv
        self.qt_image = self.processor.get_qt_image()
        self.OCR_LIST=[] #Reinicia la lista de OCR
        self.patrones=[] #Creo que esta bien reiniciar esto
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

            for nombre,rect,text in self.OCR_LIST:
                painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
                painter.drawRect(rect)
                painter.drawText(rect.topLeft(), nombre)
                painter.drawText(rect.topRight(), text)
                
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
            if self.CLAMP_FLAG:
                self.OCR_FLAG =False #Para evitar conflictos con el OCR es mejor apagar el flag
                print("generic_name")
                #print(rect)
                self.processor.clamp(rect=rect)
                self.CLANP_FLAG=False
                
            if self.OCR_FLAG:
                self.CLAMP_FLAG =False #Para evitar conflictos con la deteccion de picos, desactivo la bandera
                #print("OCR")
                text = self.processor.OCR(rect=rect)
                self.OCR_FLAG=False
                if self.OCR_LIST ==[]:
                    N=0
                else:
                    N = len(self.OCR_LIST)
                nombre_ocr = f"OCR_{N}"
                
                self.OCR_LIST.append((nombre_ocr,rect,text))
                self.save_actions.append(("OCR",nombre_ocr,rect))
                self.ocr_lista.emit(self.OCR_LIST)
            # Obtener la etiqueta del usuario
            #label, ok = QInputDialog.getText(self, "Etiqueta", "Ingrese la etiqueta:")
            #if ok and label:
                #color = self.get_color_for_label(label)
                #self.rectangles.append((rect, label, color))
            if self.NUMERIC_FLAG:
                self.OCR_FLAG=False #desactivo la bandera para evitar conflictos
                self.CLAMP_FLAG=False #desactivo la bandera para evitar conflictos
                self.NUMERIC_FLAG=False #desactivo la bandera para evitar conflictos
                x,y = self.processor.toNumeric(rect=rect)
                N = len(self.NUMERIC_LIST)
                self.NUMERIC_LIST.append([f"curve_{N}",x,y]) #Nombre,x[],y[],(x_min,y_min),(x_max,y_max)
                self.numeric_list.emit(self.NUMERIC_LIST) #Emito la señal
                
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
            
    def select_pattern(self,path,name="Patron"):
        
        """
        Se encarga de recuadrar una imagen patron
        """
        if self.processor.cv_image is not None:
            self.patrones_PATH.append(path) #En caso que se realicen acciones con los patrones, se debe poder re actualizar
            y,h,x,w = self.processor.PATRON(path)
            rect = QRect(x,y,w,h)
            #print(rect)
            self.patrones.append((rect,name))
            self.patrones_lista.emit(self.patrones)
            self.save_actions.append(("load_patern", path, name))
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
                
        copia_paths = self.patrones_PATH.copy() #Importante el copy esto lo que hace es copiar la informacion pero no los cambios que se realicen al original, sino quedan enlazados
        for path in copia_paths:
            print(path)
            self.patrones=[]
            try:
                self.select_pattern(path=path)
            except:
                print("No se ha encontrado el patron")
                
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
        
    def apply_color_operators(self,operation,color):
        """
        Funcion que aplica la operacion a la imagen de trabajo
        :operation: Operacion que se va a realizar
        :color: tupla con formato (B,G,R)
        """
        
        ##Aca podria nuevamente preguntar si existe alguna imagen, aunque creo que no es necesario
        
        self.processor.color_operators(operation=operation,color=color)
        self.qt_image = self.processor.get_qt_image() #actualizo la imagen en formato QT
        self.save_actions.append(("apply_color_operators",operation,color))
        
        self.update()
#*************************************************FLAG******************************************************************
    def apply_clamp(self):
        """
        Activa la flag del clamp
        """
        self.CLAMP_FLAG = not self.CLAMP_FLAG
        
    def apply_ocr(self):
        """
        Aplica el control del ocr
        """
        self.OCR_FLAG = not self.OCR_FLAG
        
    def apply_image_to_numeric(self):
        """
        Para poder seleccionar la parte donde quiero convertir la imagen en numerico
        """
        self.NUMERIC_FLAG = not self.NUMERIC_FLAG
        
    def apply_color_manipulation(self,operation,color1,color2,color_change):
        """
        Funcion que aplica filtrado por color y poder eliminarlo o cambiarlo\n\n\n
        Hay que tener en consideracion que cada color tiene su valor minimo y maximo es decir\n
        color = ((hue_min,hue_max),(sat_min,sat_max),(val_min,val_max))\n
        :operation: puede ser substraction o change\n
        :color1: rango de color en hsv\n
        :color2: rango de color en hsv\n
        :color_change: color por el cual se va a reemplazar el rango
        """
        self.processor.color_manipulation(operation=operation,range1=color1,range2=color2,color=color_change)
        self.qt_image = self.processor.get_qt_image() #actualizo la imagen en formato QT
        self.save_actions.append(("apply_color_manipulation",operation,color1,color2,color_change))
        
        self.update()
        
        
    def apply_filter_many_times(self,debug=True):
        N=0
        PATRONES = []
        if self.SOURCE_FOLDER !=None: #En caso que no haya source no hace nada
            if self.scrip_path != None:
                with open(self.scrip_path, 'rb') as f:
                    FILTER_PROCESS = pickle.load(f)
                image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')

                for filename in os.listdir(self.SOURCE_FOLDER):
                    sumary = {} #Para crear un dic a exportar
                    if filename.lower().endswith(image_extensions):
                        image_path = os.path.join(self.SOURCE_FOLDER, filename)
                        img = cv2.imread(image_path)
                        height, widht= img.shape[:2]
                        sumary["vanilla image"] = {
                            "Name":image_path,
                            "Height":height,
                            "Widht":widht
                        }
                        if debug==True:

                            print(f"Procesando: {image_path}")
                        for process in FILTER_PROCESS:
                            if process[0]=="load_image":
                                pass #Ya que no lo necesito en este caso, porque selecciona las imagenes del folder
                            
                            elif process[0]=="apply_grayscale":
                                img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) #Blanco y negro
                                
                            elif process[0]=="apply_flip":
                                img = cv2.rotate(img,cv2.ROTATE_180) #Flip 180°
                                
                            elif process[0]=="load_patern":
                                matches = False
                                PATRON = cv2.imread(process[1],0) #process[1] = path
                                FIG = img.copy()
                                METODO = cv2.TM_CCOEFF_NORMED
                                coincidencias = cv2.matchTemplate(cv2.cvtColor(FIG, cv2.COLOR_BGR2GRAY), PATRON, METODO)
                                _, max_val, _, max_loc = cv2.minMaxLoc(coincidencias)
                                if max_val != 0.0:
                                    matches = True
                                    # Obtén las dimensiones del patrón
                                    ancho_patron, alto_patron = PATRON.shape[::-1]
                                    punto_inicio = max_loc
                                    PATRONES.append(((punto_inicio[1],alto_patron, punto_inicio[0],ancho_patron),process[2])) #y,h,x,w; process[2]=nombre
                                sumary[f"Pattern loaded {N}"]={
                                    "Name":process[2],
                                    "Path":process[1],
                                    "Y":punto_inicio[1],
                                    "Height":alto_patron,
                                    "X":punto_inicio[0],
                                    "Widht":ancho_patron,
                                    "Match":matches
                                }
                                N+=1
                            elif process[0]=="apply_threshold_filter":
                                img = cv2.adaptiveThreshold(img,255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                        cv2.THRESH_BINARY,process[1],process[2]) #process[1]=kernel,process[2]=c
                                sumary["Threshold Filter"] = {
                                    "Type":"cv2.ADAPTIVE_THRESH_GAUSSIAN_C",
                                    "Kernel" : process[1],
                                    "C" : process[2]
                                }
                            elif process[0]=="chop_loaded_pattern":
                                patrones_coordenadas= PATRONES[0][0] #En este caso solo va a cortar el patron que se encuentre en la posicion 0
                                img = img[patrones_coordenadas[0]:patrones_coordenadas[0]+patrones_coordenadas[1],patrones_coordenadas[2]:patrones_coordenadas[2]+patrones_coordenadas[3]].copy()
                                sumary["Choped"] = {
                                    "Chop" :"Yes",
                                    "Name":"ID"
                                }
                            elif process[0]=="apply_zoom":
                                y, x= img.shape[:2]
                                img = cv2.resize(img,(x*process[1],y*process[1]),interpolation=cv2.INTER_CUBIC) #process[1] = zoom
                                sumary["Zoom"] = {
                                    "Y":y,
                                    "X":x,
                                    "Zoom":process[1],
                                    "Type":"cv2.INTER_CUBIC"
                                }
                            elif process[0]=="apply_plane_extraction":
                                pass
                            elif process[0]=="apply_color_operators":
                                pass
                            elif process[0]=="apply_zapply_color_manipulationoom":
                                pass
                            elif process[0]=="OCR":
                                #self.save_actions.append(("OCR",nombre_ocr,rect))
                                nombre_ocr = process[1]
                                rect = process[2]
                                try:
                                    ROI = self.cv_image[int(rect.y()):int(rect.y())+int(rect.height()),int(rect.x()):int(rect.x())+int(rect.width())]
                                    read =self.ocr.readtext(ROI)
                                    TEXTO = ""
                                    for (bbox, text, prob) in read:
                                        #print(f'Texto: {text}, Confianza: {prob:.2f}')
                                        if TEXTO == "":
                                            TEXTO = text
                                        else:
                                            TEXTO +="  "+text
                                    return TEXTO
                                except:
                                    print("ERROR")
                                sumary[nombre_ocr] = {
                                    "Type" :"OCR",
                                    "rect":rect,
                                    "Text":TEXTO
                                }
                        #loop de procesos, se debe guardar la imagen en el path
                        filename = f"editado_{filename}"
                        sumary_file = f"sumary_{filename}.json"
                        if debug ==True:
                            print(f"Se guardo en {filename}")
                        path_guardado = os.path.join(self.DESTINATION_FOLDER, filename)
                        path_guardado_sumary = os.path.join(self.DESTINATION_FOLDER, sumary_file)
                        cv2.imwrite(path_guardado,img)
                        with open(path_guardado_sumary,"w") as sumary_file:
                            json.dump(sumary,sumary_file,ensure_ascii=False, indent=4)
            #Termina el loop de imagenes
    def apply_script_and_continue_editing(self, debug=True):
        log = logger(debug=debug)
        sumary = {}  # Para crear un dic a exportar

        if self.qt_image is not None:
            log.set_text(text="ingreso 1")
            log.printer()

            if self.scrip_path is not None:
                log.set_text(text="El path del script es distinto de vacío")
                log.printer()

                with open(self.scrip_path, 'rb') as f:
                    FILTER_PROCESS_FULL = pickle.load(f)
                    log.set_text(text="Se cargó correctamente el path")
                    log.printer()

                for FILTER_PROCESS in FILTER_PROCESS_FULL:
                    try:
                        if FILTER_PROCESS[0] == "load_image":
                            pass  # Ya está cargada
                        elif FILTER_PROCESS[0] == "load_patern":
                            self.select_pattern(path=FILTER_PROCESS[1], name=FILTER_PROCESS[2])
                            log.set_text(text=f"Se cargó el patrón con el nombre {FILTER_PROCESS[2]}")
                            log.printer()
                            sumary[f"Pattern loaded {FILTER_PROCESS[2]}"] = {
                                "Name": FILTER_PROCESS[2],
                                "Path": FILTER_PROCESS[1]
                            }
                        elif FILTER_PROCESS[0] == "chop_loaded_pattern":
                            self.chop_loaded_pattern()
                            log.set_text(text="Se ha recortado el patrón")
                            log.printer()
                            sumary["Choped"] = {
                                "Chop": "Yes",
                                "Name": "ID"
                            }
                        elif FILTER_PROCESS[0] == "apply_zoom":
                            self.apply_zoom(zoom=FILTER_PROCESS[1])
                            log.set_text(text="Se ha aplicado zoom")
                            log.printer()
                            sumary["Zoom"] = {
                                "Zoom": FILTER_PROCESS[1],
                                "Type": "cv2.INTER_CUBIC"
                            }
                        elif FILTER_PROCESS[0] == "apply_grayscale":
                            self.apply_grayscale()
                            log.set_text(text="Se ha aplicado escala de grises")
                            log.printer()
                            sumary["Grayscale"] = {"Applied": True}
                        elif FILTER_PROCESS[0] == "apply_flip":
                            self.apply_flip()
                            log.set_text(text="Se ha rotado la imagen")
                            log.printer()
                            sumary["Flip"] = {"Applied": True}
                        elif FILTER_PROCESS[0] == "apply_threshold_filter":
                            self.apply_threshold_filter(kernel=FILTER_PROCESS[1], c=FILTER_PROCESS[2])
                            log.set_text(text=f"Se ha aplicado el filtro de umbralizado con un kernel de {FILTER_PROCESS[1]} y una matriz c de {FILTER_PROCESS[2]}")
                            log.printer()
                            sumary["Threshold Filter"] = {
                                "Type": "cv2.ADAPTIVE_THRESH_GAUSSIAN_C",
                                "Kernel": FILTER_PROCESS[1],
                                "C": FILTER_PROCESS[2]
                            }
                        elif FILTER_PROCESS[0] == "apply_color_manipulation":
                            self.apply_color_manipulation(operation=FILTER_PROCESS[1], color1=FILTER_PROCESS[2], color2=FILTER_PROCESS[3], color_change=FILTER_PROCESS[4])
                            log.set_text(text="Se aplica manipulación de colores")
                            log.printer()
                            sumary["Color Manipulation"] = {
                                "Operation": FILTER_PROCESS[1],
                                "Color1": FILTER_PROCESS[2],
                                "Color2": FILTER_PROCESS[3],
                                "Change": FILTER_PROCESS[4]
                            }
                        elif FILTER_PROCESS[0] == "apply_color_operators":
                            self.apply_color_operators(operation=FILTER_PROCESS[1], color=FILTER_PROCESS[2])
                            log.set_text(text="Se aplica operación de colores")
                            log.printer()
                            sumary["Color Operator"] = {
                                "Operation": FILTER_PROCESS[1],
                                "Color": FILTER_PROCESS[2]
                            }
                        elif FILTER_PROCESS[0] == "apply_plane_extraction":
                            self.apply_plane_extraction(plane=FILTER_PROCESS[1], bw=FILTER_PROCESS[2])
                            log.set_text(text="Se aplica extracción de plano de color")
                            log.printer()
                            sumary["Plane Extraction"] = {
                                "Plane": FILTER_PROCESS[1],
                                "BW": FILTER_PROCESS[2]
                            }
                        elif FILTER_PROCESS[0] == "OCR":
                            text = self.processor.OCR(rect=FILTER_PROCESS[2])
                            self.OCR_LIST.append((FILTER_PROCESS[1], FILTER_PROCESS[2], text))
                            self.save_actions.append(("OCR", FILTER_PROCESS[1], FILTER_PROCESS[2]))
                            self.ocr_lista.emit(self.OCR_LIST)
                            sumary[FILTER_PROCESS[1]] = {
                                "Type": "OCR",
                                "rect": str(FILTER_PROCESS[2]),
                                "Text": text
                            }
                        else:
                            log.set_text(text="No ha funcionado")
                            log.printer()
                    except Exception as e:
                        log.set_text(text=f"Error en filtro {FILTER_PROCESS[0]}: {e}")
                        log.printer()
                        pass

                log.set_text(text="Se ha finalizado")
                log.printer()

        # Guardar el resumen en la misma carpeta del script
        script_dir = os.path.dirname(self.scrip_path)  # Ruta del directorio que contiene el script
        summary_path = os.path.join(script_dir, "summary_script_run.json")

        try:
            with open(summary_path, "w", encoding="utf-8") as summary_file:
                json.dump(sumary, summary_file, ensure_ascii=False, indent=4)
            if debug:
                print(f"Resumen guardado en: {summary_path}")
        except Exception as e:
            print(f"Error al guardar el resumen: {e}")