from PyQt6.QtGui import QPicture, QPainter
from PyQt6.QtCore import QPointF, QRectF
from pyqtgraph import GraphicsObject, mkPen, mkBrush
import pandas as pd


class CandlestickItem(GraphicsObject):
    def __init__(self, data_list_candlestick):
        super().__init__()

        self.setData(data_list_candlestick)

        self.generatePicture()

    def setData(self, data_list_candlestick):       # 重写了父类GraphicsObject的方法
        self.data_list_candlestick = data_list_candlestick  # data_list_candlestick must have fields: time, open, close, min, max # data_to_region是准备传给region_plot的一维数组

    def generatePicture(self):
        self.picture = QPicture()
        painter = QPainter(self.picture)        # 这里能不能反过来写
        w = (self.data_list_candlestick[1][0] - self.data_list_candlestick[0][0]) / 3         # 蜡烛间隔为w，蜡烛宽度为2w
        for (t, open, close, min, max) in self.data_list_candlestick:
            # 绘制线，最低价-最高价
            painter.setPen(mkPen('w'))
            painter.drawLine(QPointF(t, min), QPointF(t, max))
            # 绘制箱体，开盘价-收盘价
            if open < close:
                painter.setPen(mkPen('r'))              # 不设置pen没有边框
                painter.setBrush(mkBrush('r'))
            else:
                painter.setPen(mkPen('g'))              # 不设置pen没有边框
                painter.setBrush(mkBrush('g'))
            painter.drawRect(QRectF(t-w, open, w*2, close-open))
        painter.end()

    # 继承QGraphicsItem类实现自定义的图形项，必须先实现两个纯虚函数boundingRect()和paint()，前者用于定义Item的绘制范围，后者用于绘制图形项
    def paint(self, painter, *args):                    # 继承GraphicsObject后，paint()必须overload，里面参数*args不能删，否则报“paint() takes 2 arguments but 4 were given”
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):                             # 继承GraphicsObject后，boundingRect()必须overload
        return QRectF(self.picture.boundingRect())
