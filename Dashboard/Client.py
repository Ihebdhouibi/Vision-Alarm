# This is the client Dhasboard

from PySide6 import QtWidgets, QtGui, QtCore
import sys
import random


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
        super().__init__()
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
        # To be developed
        self.statusBar().showMessage('Streaming on ')
        self.menuBar().addMenu('Add camera')
        self.menuBar().addMenu('Remove camera')

        # dockWidget = QtWidgets.QDockWidget('Dock', self)
        #
        # dockWidget.setFloating(False)
        # self.addDockWidget(self, Qt.RightDockWidgetArea, dockWidget)


# Launching the client

app = QtWidgets.QApplication()

window = Client()
window.show()

sys.exit(app.exec_())
