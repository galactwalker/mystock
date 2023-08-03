from pyqtgraph import FillBetweenItem, PlotWidget


class CapitalChart:
    def __init__(self, data_caspital):

        self.setData(data_caspital)

        self.item = self.createChart()

    def setData(self, data_caspital):
        self.curvedata1 = data_caspital[0]
        self.curvedata2 = data_caspital[1]
        self.curvedata3 = data_caspital[2]

    def createChart(self):
        p = PlotWidget()
        p.setMouseEnabled(y=False)                  # 禁止y轴的鼠标滚动缩放

        data = [0 for i in range(7965)]             # 存疑，这个数据是否需要从datapro传过来？
        curve0 = p.plot(data, pen='w')

        curve1 = p.plot(self.curvedata1, pen='k')
        curve2 = p.plot(self.curvedata2, pen='k')
        curve3 = p.plot(self.curvedata3, pen='k')
        curves = [curve0, curve1, curve2, curve3]

        brushes = [(180, 82, 205), (195, 89, 221), (209, 95, 238)]          # MediumOrchid色

        fills = [FillBetweenItem(curves[i], curves[i + 1], brushes[i]) for i in range(3)]   # FillBetweenItem(),面积图的涂色Item，列表里面创建了2个
        for fill in fills:                                                                  # 添加入PlotWidget
            p.addItem(fill)

        return p






