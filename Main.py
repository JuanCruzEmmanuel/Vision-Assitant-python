from GUI import MainWindow
from PyQt5.QtWidgets import QApplication
def VisionAssistanse(action="F"):
    if action =="T":
        app = QApplication([])
        window = MainWindow()
        window.show()
        app.exec_()
    else:
        pass


VisionAssistanse(action="T")