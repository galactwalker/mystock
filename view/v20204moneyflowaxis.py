from pyqtgraph import AxisItem


class MoneyFlowAxisItem:
    def __init__(self, data_moneyflowaxis_list):

        self.setData(data_moneyflowaxis_list)

        self.axis = self.createAxis()

    def setData(self, data_moneyflowaxis_list):
        self.data_tradedate = data_moneyflowaxis_list[0]
        self.data_axis_length = data_moneyflowaxis_list[1]

    def createAxis(self):
        axis_1 = [(i, self.data_tradedate[i]) for i in range(0, self.data_axis_length, 10)]  # X轴刻度值sub-minor ticks，跨度为10
        axis_2 = [(i, self.data_tradedate[i]) for i in range(0, self.data_axis_length, 30)]  # X轴刻度值sub-minor ticks，跨度为30
        axis_3 = [(i, self.data_tradedate[i]) for i in range(0, self.data_axis_length, 90)]  # X轴刻度值minor ticks，跨度为90
        axis_4 = [(i, self.data_tradedate[i]) for i in range(0, self.data_axis_length, 270)]  # X轴刻度值major ticks，跨度为270
        mf_axis = AxisItem(orientation='bottom')  # 创建一个刻度项
        mf_axis.setTicks([axis_4, axis_3, axis_2, axis_1])  # 设置X轴刻度值，似乎最多设置4层，多了显示不了。一旦使用setTicks后，其他方法如tickstring/tickvalue/setstyle/setTickSpacing都不好用了，因为setTicks()会重写这些方法
        return mf_axis
