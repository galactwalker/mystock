from PyQt6.QtCore import pyqtSignal, QPointF
from pyqtgraph import PlotItem, InfiniteLine, mkPen


class MoneyFlowPlot(PlotItem):
    def __init__(self, data_moneyflow_list, maximumHeight):
        super().__init__()

        self.setData(data_moneyflow_list, maximumHeight)

        self.createPlot()

    def setData(self, data_moneyflow_list, maximumHeight):
        self.x_max = data_moneyflow_list[0]
        self.y_max = data_moneyflow_list[1]
        self.y_min = data_moneyflow_list[2]
        self.maximumHeight = maximumHeight

    def createPlot(self):
        # 设置视图风格
        self.setLimits(xMin=0, xMax=self.x_max, yMin=self.y_min, yMax=self.y_max)
        self.setMouseEnabled(y=False)  # 禁止y轴的鼠标滚动缩放
        self.showGrid(x=True, y=True)  # 设置网格可见
        self.setMaximumHeight(self.maximumHeight)
        self.showAxes(selection=(True, False, False, False), showValues=True, size=(40, 15, 0, 0))     # selection left,top,right,bottom & size left,bottom,right,top
