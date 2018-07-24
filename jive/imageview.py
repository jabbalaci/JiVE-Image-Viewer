from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QGraphicsView


class ImageView(QGraphicsView):
    def __init__(self, parent) -> None:
        super().__init__()
        self.parent = parent

        self.setFrameShape(QFrame.NoFrame)    # no border in fullscreen mode

        # set background to black
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(palette)

    # help would be appreciated here
    # these don't work:

    # def mousePressEvent(self, event):
    #     print("pressed")
    #     """Go to the next / previous image, or be able to drag the image with a hand."""
    #     if event.button() == Qt.LeftButton:
    #         self.setDragMode(QGraphicsView.ScrollHandDrag)
    #     QGraphicsView.mousePressEvent(self, event)
    #
    # def mouseReleaseEvent(self, event):
    #     print("released")
    #     self.setDragMode(QGraphicsView.NoDrag)
    #     QGraphicsView.mouseReleaseEvent(self, event)
