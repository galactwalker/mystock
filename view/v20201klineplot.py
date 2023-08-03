from pyqtgraph import PlotItem, InfiniteLine, GraphicsScene, mkPen, TextItem
from PyQt6.QtCore import QPointF, pyqtSignal


class KLinePlot(PlotItem):

    def __init__(self, data_kline_list):            # 传入的kline_list列表里面有7个参数
        super().__init__()

        self.setData(data_kline_list)               # 获取数据

        self.createPlot()                           # 初始化plot核心函数

    def setData(self, data_kline_list):             # 重写了父类PlotItem的方法
        self.x_max = data_kline_list[0]             # to→ createPlot()设定plot范围 & to→ mouseMoved()判断index范围
        self.y_max = data_kline_list[1]             # to→ createPlot()设定plot范围
        self.trade_date_list = data_kline_list[2]   # to→ mouseMoved()
        self.open_list = data_kline_list[3]         # to→ mouseMoved()
        self.close_list = data_kline_list[4]        # to→ mouseMoved()
        self.high_list = data_kline_list[5]         # to→ mouseMoved()
        self.low_list = data_kline_list[6]          # to→ mouseMoved()


    def createPlot(self):

        # 设置视图风格

        self.setLimits(xMin=0, xMax=self.x_max, yMin=0, yMax=self.y_max)        # plot对图表的最大显示范围
        self.setMouseEnabled(y=False)                                           # 禁止y轴的鼠标滚动缩放
        self.showGrid(x=True, y=True)                                           # 设置网格可见
        self.setMaximumHeight(700)
        self.showAxes(selection=(True, False, False, False), size=(40, 0, 0, 0))     # selection left,top,right,bottom & size left,bottom,right,top

        # 十字光标crosshair，内置于kline_plot
        self.vLine = InfiniteLine(angle=90, movable=False, pen=mkPen('w'))
        self.hLine = InfiniteLine(angle=0, movable=False, pen=mkPen('w'), label='{value:0.2f}', labelOpts={'fill': (0, 200, 0, 100), 'position': 0.98})
        self.addItem(self.vLine, ignoreBounds=True)
        self.addItem(self.hLine, ignoreBounds=True)
        # 十字光标crosshair label，使用TextItem()不受缩放影响
        self.text_cross = TextItem()
        self.addItem(self.text_cross, ignoreBounds=True)

    def region_update_kline(self, region_turple):               # 与Region互动
        minX, maxX = region_turple
        self.setXRange(minX, maxX, padding=0)                   # padding不可删，否则kline与region的互动感应会莫名停滞

    # 与vol_plot的crosshair同步的信号
    sigto_vol_cross = pyqtSignal(QPointF)

    def mouseMoved(self, evt):                                  # 十字光标crosshair和text_cross的信号
        pos = evt
        if self.sceneBoundingRect().contains(pos):
            mousePoint = self.vb.mapSceneToView(pos)            # 用户窗口scene坐标转实际的view坐标（即真实的xy轴上的坐标）
            index = int(mousePoint.x())
            if 0 < index < self.x_max:
                self.text_cross.setHtml(
                            "<p style='color:white'><strong>日期：{0}</strong></p>"
                            "<p style='color:white'>开盘：{1}</p>"
                            "<p style='color:white'>收盘：{2}</p>"
                            "<p style='color:white'>最高价：<span style='color:red;'>{3}</span></p>"
                            "<p style='color:white'>最低价：<span style='color:green;'>{4}</span></p>".format(
                                self.trade_date_list[index], self.open_list[index], self.close_list[index],
                                self.high_list[index], self.low_list[index]))

                # text_cross的坐标
                upper_left_scene = QPointF(50, 30)                          # k线图的原点，大约在scene坐标(50，30)
                upper_left_view = self.vb.mapSceneToView(upper_left_scene)  # 转化成view坐标，以在view中设置text_cross的位置
                self.text_cross.setPos(upper_left_view)

            self.vLine.setPos(mousePoint.x())
            self.hLine.show()
            self.hLine.setPos(mousePoint.y())

            # 发射信号，使vol_plot的crosshair同步
            self.sigto_vol_cross.emit(mousePoint)

    def mouseMovedFromV(self, mousePoint):
        self.vLine.setPos(mousePoint.x())
        self.hLine.hide()
