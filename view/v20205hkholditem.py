from PyQt6.QtGui import QPicture, QPainter, QColor
from PyQt6.QtCore import QRectF
from pyqtgraph import GraphicsObject, mkPen, mkBrush


class HkHoldItem(GraphicsObject):
    def __init__(self, data_hkhold):
        super().__init__()

        self.setData(data_hkhold)

        self.generatePicture()

    def setData(self, data_hkhold):
        self.data_hkhold = data_hkhold

    def generatePicture(self):
        self.picture = QPicture()
        painter = QPainter(self.picture)        # 这里能不能反过来写
        w = (self.data_hkhold[1][0] - self.data_hkhold[0][0]) / 3         # 间隔为w，蜡烛宽度为2w
        for (t, vol, ratio) in self.data_hkhold:
            painter.setPen(mkPen(QColor(255, 193, 37)))              # 不设置pen没有边框，没有边框显示效果有问题
            painter.setBrush(mkBrush(QColor(255, 193, 37)))
            painter.drawRect(QRectF(t-w, 0, w*2, vol))
        painter.end()

    # 继承QGraphicsItem类实现自定义的图形项，必须先实现两个纯虚函数boundingRect()和paint()，前者用于定义Item的绘制范围，后者用于绘制图形项
    def paint(self, painter, *args):                    # 继承GraphicsObject后，paint()必须overload，里面参数*args不能删，否则报“paint() takes 2 arguments but 4 were given”
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):                             # 继承GraphicsObject后，boundingRect()必须overload
        return QRectF(self.picture.boundingRect())
