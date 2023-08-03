from PyQt6.QtCore import pyqtSignal, QPointF
from pyqtgraph import PlotItem, InfiniteLine, mkPen


class VolumePlot(PlotItem):
    def __init__(self, data_volume_list):
        super().__init__()

        self.setData(data_volume_list)

        self.createPlot()

    def setData(self, data_volume_list):
        self.x_max = data_volume_list[0]
        self.y_max = data_volume_list[1]

    def createPlot(self):

        # 设置视图风格
        self.setLimits(xMin=0, xMax=self.x_max, yMin=0, yMax=self.y_max)
        self.setMouseEnabled(y=False)  # 禁止y轴的鼠标滚动缩放
        self.showGrid(x=True, y=True)  # 设置网格可见
        self.setMaximumHeight(150)
        self.showAxes(selection=(True, False, False, True), size=(40, 15, 0, 0))     # selection left,top,right,bottom & size left,bottom,right,top

        # 十字光标crosshair，内置于kline_plot
        self.vLine = InfiniteLine(angle=90, movable=False, pen=mkPen('w'))
        self.hLine = InfiniteLine(angle=0, movable=False, pen=mkPen('w'), label='{value:0.2f}', labelOpts={'fill': (0, 200, 0, 100), 'position': 0.98})
        self.addItem(self.vLine, ignoreBounds=True)
        self.addItem(self.hLine, ignoreBounds=True)

    # 与kline_plot的crosshair同步的信号
    sigto_kline_cross = pyqtSignal(QPointF)

    def mouseMoved(self, evt):                                  # 十字光标crosshair和text_cross的信号
        pos = evt
        if self.sceneBoundingRect().contains(pos):
            mousePoint = self.vb.mapSceneToView(pos)            # 用户窗口scene坐标转实际的view坐标（即真实的xy轴上的坐标）
            self.vLine.setPos(mousePoint.x())
            self.hLine.show()
            self.hLine.setPos(mousePoint.y())

            # 发射信号，使vol_plot的crosshair同步
            self.sigto_kline_cross.emit(mousePoint)

    def mouseMovedFromK(self, mousePoint):
        self.vLine.setPos(mousePoint.x())
        self.hLine.hide()
