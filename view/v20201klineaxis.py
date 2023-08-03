from pyqtgraph import AxisItem


class KlineAxisItem:
    def __init__(self, data_klineaxis_list):

        self.setData(data_klineaxis_list)

        self.axis = self.createAxis()

    def setData(self, data_klineaxis_list):
        self.data_tradedate = data_klineaxis_list[0]        # 与kline_tradedate相同
        self.data_axis_length = data_klineaxis_list[1]      # 与kline length相同

    def createAxis(self):
        axis_1 = [(i, self.data_tradedate[i]) for i in range(0, self.data_axis_length, 10)]  # X轴刻度值sub-minor ticks，跨度为10
        axis_2 = [(i, self.data_tradedate[i]) for i in range(0, self.data_axis_length, 30)]  # X轴刻度值sub-minor ticks，跨度为30
        axis_3 = [(i, self.data_tradedate[i]) for i in range(0, self.data_axis_length, 90)]  # X轴刻度值minor ticks，跨度为90
        axis_4 = [(i, self.data_tradedate[i]) for i in range(0, self.data_axis_length, 270)]  # X轴刻度值major ticks，跨度为270
        kline_axis = AxisItem(orientation='bottom')  # 创建一个刻度项
        kline_axis.setTicks([axis_4, axis_3, axis_2, axis_1])  # 设置X轴刻度值，似乎最多设置4层，多了显示不了。一旦使用setTicks后，其他方法如tickstring/tickvalue/setstyle/setTickSpacing都不好用了，因为setTicks()会重写这些方法
        # self.k_plot.setAxisItems({'bottom': kline_axis})    # 参数必须为字典，key为 (‘left’, ‘bottom’, ‘right’, ‘top’) ，values为AxisItem()的实例
        # self.k_plot.getAxis("bottom").setTicks([axis_4, axis_3, axis_2, axis_1])  # 设置X轴刻度值self.axis_dict.items()
        return kline_axis
