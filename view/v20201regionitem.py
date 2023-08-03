from pyqtgraph import LinearRegionItem


class RegionItem(LinearRegionItem):

    def __init__(self, region_plot_data, data_fromkline):
        super().__init__()

        self.setData(region_plot_data, data_fromkline)

        self.generatePicture()

    def setData(self, region_plot_data, data_fromkline):
        self.region_plot_data = region_plot_data
        self.data_fromkline = data_fromkline

    def generatePicture(self):
        self.setClipItem(self.region_plot_data)  # region绑定的数据，用来设置边界。是region_plot生成的二手数据。 # bound the LinearRegionItem to the plotted data
        self.setZValue(10)
        # 设定初始框选位置：从最右侧向左数1000的区域
        self.setRegion([len(self.data_fromkline) - 1000, len(self.data_fromkline)])

    def kline_update_region(self, window, viewRange):              # 与K线互动
        rgn = viewRange[0]
        self.setRegion(rgn)
