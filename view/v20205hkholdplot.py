from PyQt6.QtCore import pyqtSignal, QPointF
from pyqtgraph import PlotItem, InfiniteLine, mkPen


class HkHoldPlot(PlotItem):
    def __init__(self, data_hkhold_list):
        super().__init__()

        self.setData(data_hkhold_list)

        self.createPlot()

    def setData(self, data_hkhold_list):
        self.x_max = data_hkhold_list[0]
        self.y_max = data_hkhold_list[1]

    def createPlot(self):
        # 设置视图风格
        self.setLimits(xMin=0, xMax=self.x_max, yMin=0, yMax=self.y_max)
        self.setMouseEnabled(y=False)  # 禁止y轴的鼠标滚动缩放
        self.showGrid(x=True, y=True)  # 设置网格可见
        self.setMaximumHeight(150)
        self.showAxes(selection=(True, False, False, True), size=(40, 15, 0, 0))     # selection left,top,right,bottom & size left,bottom,right,top
