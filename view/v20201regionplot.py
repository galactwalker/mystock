from pyqtgraph import LinearRegionItem, PlotItem


class RegionPlot(PlotItem):

    def __init__(self, data_fromkline):
        super().__init__()

        self.setData(data_fromkline)

        self.createPlot()

    def setData(self, data_fromkline):
        self.data_fromkline = data_fromkline

    def createPlot(self):

        # 设置视图风格
        self.setMouseEnabled(x=False, y=False)  # 禁止x轴y轴的鼠标滚动缩放
        self.setMaximumHeight(80)
        self.showAxes(selection=(True, False, False, False), size=(40, 0, 0, 0))  # selection left,top,right,bottom & size left,bottom,right,top
