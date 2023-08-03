from PyQt6.QtGui import QPicture, QPainter
from PyQt6.QtCore import QRectF
from pyqtgraph import GraphicsObject, mkPen, mkBrush


class MoneyFlowItem(GraphicsObject):
    def __init__(self, data_moneyflow_list):
        super().__init__()

        self.setData(data_moneyflow_list)

        self.generatePicture()

    def setData(self, data_moneyflow_list):
        self.data_moneyflow_list = data_moneyflow_list  # data must have fields: time, open, close, min, max

    def generatePicture(self):
        self.picture = QPicture()
        painter = QPainter(self.picture)        # 这里能不能反过来写
        w = (self.data_moneyflow_list[1][0] - self.data_moneyflow_list[0][0]) / 3         # 间隔为w，蜡烛宽度为2w
        for (t, buy, sell) in self.data_moneyflow_list:
            painter.setPen(mkPen('r'))              # 不设置pen没有边框，没有边框显示效果有问题
            painter.setBrush(mkBrush('r'))
            painter.drawRect(QRectF(t-w, 0, w*2, buy))
            painter.setPen(mkPen('g'))              # 不设置pen没有边框，没有边框显示效果有问题
            painter.setBrush(mkBrush('g'))
            painter.drawRect(QRectF(t-w, 0, w*2, -sell))
        painter.end()

    # 继承QGraphicsItem类实现自定义的图形项，必须先实现两个纯虚函数boundingRect()和paint()，前者用于定义Item的绘制范围，后者用于绘制图形项
    def paint(self, painter, *args):                    # 继承GraphicsObject后，paint()必须overload，里面参数*args不能删，否则报“paint() takes 2 arguments but 4 were given”
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):                             # 继承GraphicsObject后，boundingRect()必须overload
        return QRectF(self.picture.boundingRect())
