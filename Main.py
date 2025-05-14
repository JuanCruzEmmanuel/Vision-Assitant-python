import cv2

from UI.main_windows import Main
from PyQt5.QtWidgets import QApplication
import pickle
import easyocr
from cv2 import imwrite
#from Processing import Pipeline
def VisionAssistanse(action="F",dataPath = None):
    src = None
    if action =="T":
        app = QApplication([])
        window = Main()
        window.show()
        app.exec_()
    else:
        pass
        #with open(dataPath,"rb") as f:
            #pipeline = pickle.load(f)


        #for pipe in pipeline:
            #src = Pipeline(src=src, pipe = pipe)
            #cv2.imshow("img",src)
            #cv2.waitKey(0)
        #imwrite("Proccesing.jpeg",src)


VisionAssistanse(action="T",dataPath="data.pkl")