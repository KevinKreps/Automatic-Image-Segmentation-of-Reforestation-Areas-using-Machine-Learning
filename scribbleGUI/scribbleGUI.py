from PySide2.QtCore import Qt, QRectF
from PySide2.QtGui import QImage, qRgba, QPainter, QPen, QColor, QBrush
from PySide2.QtWidgets import QWidget


class Scribble(QWidget):
    def __init__(self, parent=None, scribbleImagePath=""):
        QWidget.__init__(self, parent)
        self.show()
        self.raise_()

        # Available space to display on
        self.imageAreaWidth = 0
        self.imageAreaHeight = 0

        # Real number of pixels (unscaled)
        self.scribbleWidth = 1
        self.scribbleHeight = 1

        # Scaling factor between the real image size and the size after scaling to fit the imageArea
        self.scaleFactor = 1.0

        self.scribbling = False  # if scribbling at this time and moment
        self.penMoved = False  # if the pen already moved while scribbling
        self.myPenWidth = 1
        self.myPenColor = QColor(0, 0, 255, 255)
        self.lastPoint = None

        self.scribbleImagePath = scribbleImagePath
        self.image = None

    def refreshScribble(self, width, height):
        self.imageAreaWidth = width
        self.imageAreaHeight = height
        self.setGeometry(0, 0, self.imageAreaWidth, self.imageAreaHeight)

    def setColor(self, color):  # QColor object
        self.myPenColor = color

    def setPenSize(self, size):
        self.myPenWidth = size

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.lastPoint = event.pos()
            self.scribbling = True
            self.penMoved = False

    def mouseMoveEvent(self, event):
        if self.scribbling:
            self.drawLineTo(event.pos())
            self.penMoved = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.scribbling:
            self.drawLineTo(event.pos())
            if self.myPenColor == QColor(255, 0, 0, 255):
                self.drawCircle(event.pos())
            self.scribbling = False
            self.penMoved = False

    def setupScribble(self, width, height):
        self.scribbleWidth = width
        self.scribbleHeight = height
        if self.scribbleImagePath == "":
            self.image = QImage(self.scribbleWidth, self.scribbleHeight, QImage.Format_ARGB32)
            # print(self.image.depth())  # prints 32
            self.image.fill(qRgba(0, 0, 0, 0))
        else:
            self.image = QImage(self.scribbleImagePath)
            self.image = self.image.convertToFormat(QImage.Format_ARGB32)
        self.update()

    def drawCircle(self, point):
        painter = QPainter(self.image)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.setRenderHint(QPainter.Antialiasing)

        brush = QBrush(QColor(0, 0, 255, 255), Qt.SolidPattern)
        pen = QPen(brush, 0.2 * self.myPenWidth / self.scaleFactor, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        radius = 1.5 * self.myPenWidth / self.scaleFactor
        rectangle = QRectF((point.x() / self.scaleFactor) - (radius / 2),
                           (point.y() / self.scaleFactor) - (radius / 2),
                           radius, radius)
        painter.drawEllipse(rectangle)

        self.update()

    def drawLineTo(self, endPoint):
        if not self.penMoved:
            endPoint.setX(endPoint.x() + 1)  # ensures a dot is being drawn if there was just a click and no mouse move
        painter = QPainter(self.image)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.setRenderHint(QPainter.Antialiasing)

        brush = QBrush(self.myPenColor, Qt.SolidPattern)
        pen = QPen(brush, self.myPenWidth / self.scaleFactor, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        # pen = QPen(self.myPenColor, self.myPenWidth, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(self.lastPoint / self.scaleFactor, endPoint / self.scaleFactor)

        self.update()

        self.lastPoint = endPoint

    def paintEvent(self, event):
        painter = QPainter(self)
        dirtyRect = event.rect()
        scaledImage = self.image.scaled(self.imageAreaWidth, self.imageAreaHeight, Qt.KeepAspectRatio,
                                        Qt.FastTransformation)
        self.scaleFactor = float(scaledImage.width()) / float(self.scribbleWidth)
        painter.drawImage(dirtyRect, scaledImage, dirtyRect)
