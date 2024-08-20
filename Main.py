import cv2

from GUI import MainWindow
from PyQt5.QtWidgets import QApplication
import pickle
from cv2 import imwrite
from Processing import Pipeline
def VisionAssistanse(action="F",dataPath = None):
    src = None
    if action =="T":
        app = QApplication([])
        window = MainWindow()
        window.show()
        app.exec_()
    else:
        with open(dataPath,"rb") as f:
            pipeline = pickle.load(f)


        for pipe in pipeline:
            src = Pipeline(src=src, pipe = pipe)
            #cv2.imshow("img",src)
            #cv2.waitKey(0)
        imwrite("Proccesing.jpeg",src)


VisionAssistanse(action="F",dataPath="data.pkl")