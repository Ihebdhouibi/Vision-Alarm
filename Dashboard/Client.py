# This is the client Dhasboard

from PySide6 import QtWidgets, QtGui, QtCore
import sys


# class MyWidget(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()
#
#         self.hello = ["hello a", " Hello b"]
#         self.button = QtWidgets.QPushButton("Click me !")
#         self.text = QtWidgets.QLabel("Hello world ",
#                                      alignment=QtCore.Qt.AlignCenter)
#         self.layout = QtWidgets.QVBoxLayout(self)
#         self.layout.addWidget(self.text)
#         self.layout.addWidget(self.button)
#
#         self.button.clicked.connect(self.magic)
#
#     @QtCore.Slot()
#     def magic(self):
#         self.text.setText(random.choice(self.hello))
#
#
# app = QtWidgets.QApplication([])
# widget = MyWidget()
# widget.resize(800, 600)
# widget.show()
#
# sys.exit(app.exec_())

class Client(QtWidgets.QMainWindow):
    """
    This is our main Application window

    This window will be devided into three area :

    Left Panel for additional informations

    Right Panel for camera feed, which will be devided into 4 areas to stream each a single camera

    Bottom Panel for displaying alert history and interact with it

    Developed by : Iheb dhouibi

    """

    def __init__(self):
        super(Client, self).__init__()
        self.initUI()

    """
    initUI function : 
            * Set Title of the main window 
            * Add a layout to the main window
            * Add menubar
            * A status bar that shows how many cameras are streaming 
    """

    def initUI(self):
        self.setGui()

    # setGui function will setup vision alarm GUI

    def setGui(self):
        self.setWindowTitle('Vision Alarm')
        self.resize(1200, 800)
        # Status Bar showing how many camera streaming **** To be developed
        self.statusBar().showMessage('Streaming on ')
        self.menuBar().addMenu('Add camera')
        self.menuBar().addMenu('Remove camera')
        camera1 = self.streamCamera() # This function will stream live feeds from camera *** To be developed
        camera2 = QtWidgets.QLabel('Camera 2 ')
        camera3 = QtWidgets.QLabel('Camera 3 ')
        camera4 = QtWidgets.QLabel('Camera 4 ')
        alets = QtWidgets.QLabel('This is where alerts will be shown')

        layout1 = QtWidgets.QGridLayout()
        layout1.addWidget(camera1)
        layout1.addWidget(camera2)
        layout1.addWidget(camera3)
        layout1.addWidget(camera4)

        camerawidget = QtWidgets.QWidget()
        camerawidget.setLayout(layout1)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(camerawidget)
        layout.addWidget(alets)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)


    def streamCamera(self):
        return QtWidgets.QLabel('Camera 1 ')


# Launching the client

app = QtWidgets.QApplication(sys.argv)

window = Client()
window.show()

sys.exit(app.exec_())
