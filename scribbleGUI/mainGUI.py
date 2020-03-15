import os
import time

import imageio
import numpy as np

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap, QImage, qRgba, QPainter, QPen, QColor
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PySide2 import QtCore
import pyside_dynamic

from scribbleGUI import Scribble

import PySide2.QtCore

# Prints PySide2 version
# e.g. 5.11.1a1
print(PySide2.__version__)

# Gets a tuple with each version component
# e.g. (5, 11, 1, 'a', 1)
print(PySide2.__version_info__)

# Prints the Qt version used to compile PySide2
# e.g. "5.11.2"
print(PySide2.QtCore.__version__)

# Gets a tuple with each version components of Qt used to compile PySide2
# e.g. (5, 11, 2)
print(PySide2.QtCore.__version_info__)


class MyWindow(QMainWindow):
    def __init__(self, parent=None, imagePath="", scribbleImagePath=""):
        QMainWindow.__init__(self, parent)
        pyside_dynamic.loadUi('mainWindow.ui', self)
        self.show()
        self.setWindowTitle("BaBa - Scribble")

        # connections
        self.bodenBtn.clicked.connect(lambda: self.changedPen('boden'))
        self.baumBtn.clicked.connect(lambda: self.changedPen('baum'))
        self.radiergummiBtn.clicked.connect(lambda: self.changedPen('radiergummi'))
        self.bodenSlider.valueChanged.connect(self.refreshSliderValues)
        self.baumSlider.valueChanged.connect(self.refreshSliderValues)
        self.radiergummiSlider.valueChanged.connect(self.refreshSliderValues)

        self.okBtn.clicked.connect(self.okAction)

        # menu
        self.penType = 'boden'
        self.sliderValues = {"boden": self.bodenSlider.value(),
                             "baum": self.baumSlider.value(),
                             "radiergummi": self.radiergummiSlider.value()}

        # dimensions
        self.imageAreaWidth = 0
        self.imageAreaHeight = 0

        # Image
        self.imagePath = imagePath
        self.imagePixmap = QPixmap(self.imagePath)
        self.imageLabel = QLabel(self.pictureArea)
        self.imageLabel.setAlignment(Qt.AlignTop)
        self.imageLabel.show()

        # Scribble
        self.scribble = Scribble(self.pictureArea, scribbleImagePath)
        self.scribble.setupScribble(self.imagePixmap.width(), self.imagePixmap.height())
        self.scribbleMat = None

        # refreshes and reloads: initial trigger
        self.refreshSliderValues()
        self.refreshDimensions()

    # refreshes the variables holding the currently available space for images
    # and calls the necessary refreshes
    def refreshDimensions(self):
        self.imageAreaWidth = self.pictureArea.width()
        self.imageAreaHeight = self.pictureArea.height()

        self.refreshImages()
        self.scribble.refreshScribble(self.imageAreaWidth, self.imageAreaHeight)

    # refreshes the images in terms of setting the QLabels to their respective QPixmap with correct scaling
    def refreshImages(self):
        self.imageLabel.setPixmap(
            self.imagePixmap.scaled(self.imageAreaWidth, self.imageAreaHeight, Qt.KeepAspectRatio,
                                            Qt.FastTransformation))
        self.imageLabel.setGeometry(0, 0, self.imageAreaWidth, self.imageAreaHeight)

    # fires, when a resize occurs
    def resizeEvent(self, event):
        if event.oldSize().width() != -1:  # dismiss the initial call of resizeEvent
            self.refreshDimensions()

    # fires, when one of the pen changing buttons is pressed
    def changedPen(self, penType):
        self.penType = penType
        self.refreshSliderValues()

        self.bodenBtn.setChecked(False)
        self.baumBtn.setChecked(False)
        self.radiergummiBtn.setChecked(False)

        if penType == 'baum':
            self.baumBtn.setChecked(True)
            self.scribble.setColor(QColor(255, 0, 0, 255))  # r g b a
        elif penType == 'boden':
            self.bodenBtn.setChecked(True)
            self.scribble.setColor(QColor(0, 0, 255, 255))  # r g b a
        elif penType == 'radiergummi':
            self.radiergummiBtn.setChecked(True)
            self.scribble.setColor(QColor(0, 0, 0, 0))  # r g b a

    # refreshes all the slider values and sets the correct pen size
    def refreshSliderValues(self):
        self.sliderValues["boden"] = self.bodenSlider.value()
        self.sliderValues["baum"] = self.baumSlider.value()
        self.sliderValues["radiergummi"] = self.radiergummiSlider.value()
        self.scribble.setPenSize(self.sliderValues[self.penType])

    # fires, when ok button is pressed
    def okAction(self):
        # collect and prepare the data for further processing
        width = self.scribble.image.width()
        height = self.scribble.image.height()
        scribbleQImage = self.scribble.image.rgbSwapped()
        scribbleBits = scribbleQImage.constBits()
        self.scribbleMat = np.array(scribbleBits).reshape(height, width, 4)  # Copies the data
        #self.scribbleMat = np.delete(self.scribbleMat, 3, 2)  # 3rd(alpha) color(on axis 2)

        self.close()


def getDataFromGUI(imagePath, scribbleImagePath):
    QtCore.QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QApplication()
    mywindow = MyWindow(imagePath=imagePath, scribbleImagePath=scribbleImagePath)

    app.exec_()

    return mywindow.scribbleMat


if __name__ == "__main__":
    inputImagesPath = "inputImages/Atlaszeder"
    scribbleImagesPath = "scribbleData/Atlaszeder/"
    files = [f for f in os.listdir(inputImagesPath) if os.path.isfile(os.path.join(inputImagesPath, f))]

    # choose file
    #i = np.random.randint(0, len(files))
    #imageFilename = files[i]

    #imageFilename = "test9.jpg"

    for imageFilename in files:
        imagePath = os.path.join(inputImagesPath, imageFilename)
        print(imagePath)

        scribbleImagePath = ""
        if False:  # change boolean as needed
            files = [f for f in os.listdir(scribbleImagesPath) if os.path.isfile(os.path.join(scribbleImagesPath, f))]
            files = [f for f in files if f[: len(imageFilename) - 4] == imageFilename[:-4]]
            files.sort()

            scribbleImageFilename = files[-1]  # get the newest file
            scribbleImagePath = os.path.join(scribbleImagesPath, scribbleImageFilename)
            print(scribbleImagePath)

        scribbleMat = getDataFromGUI(imagePath, scribbleImagePath)

        timestr = time.strftime("%Y%m%d_%H%M%S")
        imageio.imwrite(scribbleImagesPath + imageFilename[:-4] + 'Scribble_' + timestr + '.png', scribbleMat)
