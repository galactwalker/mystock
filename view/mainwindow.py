from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QVBoxLayout, QPushButton, QMessageBox, QTabWidget, \
    QStackedLayout, QTableView
from PyQt6.QtSql import QSqlTableModel, QSqlDatabase
from pyqtgraph import GraphicsLayoutWidget, LabelItem

from model.dataprocessor import DataProcessor
from model.sqliteconnection import SqliteConnection
from model.stockmodel import StockTableModel
from model.stockdb import StockDBConnection
from view.v20201regionitem import RegionItem
from view.v20206capitalaxis import CapitalAxisItem
from view.v20206capitalchart import CapitalChart
from view.v20202basicinfomation import BasicInfomation
from view.v20201btnlabel import BtnLabel
from view.v20201klineitem import CandlestickItem
from view.v20201klineaxis import KlineAxisItem
from view.v20201klineplot import KLinePlot
from view.v20201regionplot import RegionPlot
from view.v20101stockview import StockTableView
from view.v20201volumeitem import VolumeItem
from view.v20201volumeplot import VolumePlot
from view.v20204moneyflowaxis import MoneyFlowAxisItem
from view.v20204moneyflowitem import MoneyFlowItem
from view.v20204moneyflowplot import MoneyFlowPlot
from view.v20205hkholdaxis import HkHoldAxisItem
from view.v20205hkholditem import HkHoldItem
from view.v20205hkholdplot import HkHoldPlot


class Window(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        # 取个股数据，从数据库，用于“个股详情”
        stock = ""
        self.getAndProc_stockDatas(stock)

        # 窗口
        self.setWindowTitle("股票系统")
        self.setGeometry(50, 50, 1460, 760)

        # 中央组件Widget及Layout（横向）
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralLayout = QHBoxLayout()
        self.centralWidget.setLayout(self.centralLayout)

        # 01左侧标签界面（纵向）
        self.labelLayout = QVBoxLayout()
        self.centralLayout.addLayout(self.labelLayout)

        # 01左侧标签界面 01加载4个label，并添加signal&slot
        self.label1 = BtnLabel("股票集")
        self.label1.mousepress_signal.connect(self.to_stock_collection_page)  # 连接到右侧界面stackedlayout的QWidget
        self.label1.mousepress_signal.connect(self.set_state)  # 接收鼠标按下BtnLabel的signal，清除其他BtnLabel的按下状态。
        self.label2 = BtnLabel("个股数据")
        self.label2.mousepress_signal.connect(self.to_stock_page)  # 连接到右侧界面stackedlayout的QWidget
        self.label2.mousepress_signal.connect(self.set_state)  # 接收鼠标按下BtnLabel的signal，清除其他BtnLabel的按下状态。
        self.label3 = BtnLabel("空白")
        self.label3.mousepress_signal.connect(self.to_sm_page)  # 连接到右侧界面stackedlayout的QWidget
        self.label3.mousepress_signal.connect(self.set_state)  # 接收鼠标按下BtnLabel的signal，清除其他BtnLabel的按下状态。
        self.label4 = BtnLabel("回收站")
        self.label4.mousepress_signal.connect(self.to_recycle_page)  # 连接到右侧界面stackedlayout的QWidget
        self.label4.mousepress_signal.connect(self.set_state)  # 接收鼠标按下BtnLabel的signal，清除其他BtnLabel的按下状态。

        self.labelLayout.addWidget(self.label1)
        self.labelLayout.addWidget(self.label2)
        self.labelLayout.addWidget(self.label3)
        self.labelLayout.addWidget(self.label4)

        # 02右侧主界面（采用QStackedLayout）
        self.stackedlayout = QStackedLayout()
        self.centralLayout.addLayout(self.stackedlayout)

        # 02右侧主界面 01第一层股票集
        self.stock_collection_page = QTabWidget()
        self.stackedlayout.addWidget(self.stock_collection_page)

        # 创建“精选股票”的数据库连接，连接名connection name为“stockmain”（It is rather recommended, to connect to the database before creating any window）
        stock_main_conn = StockDBConnection("D:/financeDB/StockSelection.sqlite", "stockmain").database     # "stockmain"只是connection name

        # 02右侧主界面 01第一层股票集 01tab精选股票 Widget及Layout
        self.my_selec = QWidget()
        self.stock_collection_page.addTab(self.my_selec, "精选股票")
        self.my_selec_layout = QHBoxLayout()
        self.my_selec.setLayout(self.my_selec_layout)

        # 02右侧主界面 01第一层股票集 01tab精选股票 table
        stock_main_conn.open()  # 数据库connection.open()必须置于tablemodel之前，否则内容不显示
        headers = ("ts_code", "股票代码", "股票名称", "地域", "所属行业", "市场类型", "上市日期", "股票全称", "英文全称", "拼音缩写",
                   "交易所代码", "交易货币", "L上市D退市P暂停", "H沪股通S深股通N否", "退市日期")
        self.tablemodel1 = StockTableModel(stock_main_conn, "StockGlobal", headers)     # "StockGlobal"才是数据库的table name
        self.tableview1 = StockTableView()
        self.tableview1.view.setModel(self.tablemodel1.model)
        self.my_selec_layout.addWidget(self.tableview1.view)
            # 连接个股数据页面
        self.tableview1.view.clicked.connect(lambda qModelIndex: self.to_stockvision(qModelIndex, "selectable"))  # 发射clicked信号参数qModelIndex，同时发送自定义参数"selectable"，以对slot说明信号来源
        # 对上述lambda函数的特别说明，不仅保留QTableView().clicked的默认参数qModelIndex，而且在同时发射了一个自定义参数"selectable"

        # 02右侧主界面 01第一层股票集 01tab精选股票 buttons
        self.to_recycle_btn = QPushButton("转入回收站")
        self.to_recycle_btn.clicked.connect(self.btn_move_to_stockrecycle)
        layout1v = QVBoxLayout()
        layout1v.addWidget(self.to_recycle_btn)
        layout1v.addStretch()  # 平均分布
        self.my_selec_layout.addLayout(layout1v)

        # 创建数据库连接，连接名connection name为“stockpred”
        my_predc_conn = StockDBConnection("D:/financeDB/StockPrediction.sqlite", "stockpred").database

        # 02右侧主界面 01第一层股票集 02tab预测预警 Widget及Layout
        self.my_predc = QWidget()
        self.stock_collection_page.addTab(self.my_predc, "预测预警")
        self.my_predc_layout = QHBoxLayout()
        self.my_predc.setLayout(self.my_predc_layout)

        # 02右侧主界面 01第一层股票集 02tab预测预警 table
        my_predc_conn.open()  # 数据库connection.open()必须置于tablemodel之前，否则内容不显示
        headers = ('ts_code', '股票代码', '股票名称', 'ed30', 'ed60', 'ed100', 'ed200', 'et30', 'et60', 'et200', 'ld30', 'ld60', 'ld100',
                   'ld200', 'lt30', 'lt60', 'lt200', 'sd30', 'sd60', 'sd100', 'sd200', 'st30', 'st60', 'st200', 'hd30',
                   'hd60', 'hd100', 'hd200', 'ht30', 'ht60', 'ht200', 'md30', 'md60', 'mt30', 'mt60', 'mt200', 'sum1')
        self.predtablemodel = StockTableModel(my_predc_conn, "table1", headers)     # "table1"是数据库的table name
        self.predtableview = StockTableView()
        self.predtableview.view.setModel(self.predtablemodel.model)
        self.my_predc_layout.addWidget(self.predtableview.view)
            # 连接个股数据页面
        self.predtableview.view.clicked.connect(lambda qModelIndex: self.to_stockvision(qModelIndex, "predtable"))      # 发射clicked信号参数qModelIndex，同时发送自定义参数"predtable"，以对slot说明信号来源
            # 对上述lambda函数的特别说明，不仅保留QTableView().clicked的默认参数qModelIndex，而且在同时发射了一个自定义参数"predtable"
            # 以下是另外一种形式：
            # import functools
            # self.predtableview.view.clicked.connect(functools.partial(self.to_stockvision, 'predtable'))

        # 02右侧主界面 02第二层个股数据 Widget及Layout
        self.stock_page = QTabWidget()
        self.stackedlayout.addWidget(self.stock_page)

        # 02右侧主界面 02第二层个股数据 01tabK线详情 Widget及Layout
        self.ktab_widget = QWidget()
        self.stock_page.addTab(self.ktab_widget, "K线详情")
        self.ktab_layout = QVBoxLayout()
        self.ktab_widget.setLayout(self.ktab_layout)

        # 02右侧主界面 02第二层个股数据 01tabK线详情 Widget及Layout
        self.kchart_widget = GraphicsLayoutWidget()
        self.ktab_layout.addWidget(self.kchart_widget)
        self.kchart_layout = self.kchart_widget.addLayout()  # addLayout()只能创建新GraphicsLayout，如果想加载已有GraphicsLayout，可以使用addItem()。还有一个选项：从QWidget的角度，可以使用setLayout()，但未经实验。
        self.kchart_layout.setSpacing(0)  # 布局内item之间的间距
        self.kchart_layout.setContentsMargins(0, 0, 0, 0)  # 上下左右四个边距

        # 02右侧主界面 02第二层个股数据 01tabK线详情 01K线图
            # label
        self.k_label = LabelItem(text='日线 风华高科 000636', color=(240, 190, 131), justify='left')
        self.k_label.setFixedHeight(20)
        self.kchart_layout.addItem(self.k_label, row=0, col=0)
            # K线plot
        self.kline_plot = KLinePlot(self.data_kline_list)
        self.kchart_layout.addItem(self.kline_plot, row=1, col=0)
            # 设置K线item
        self.kline_item = CandlestickItem(self.data_kline_candlestick)
        self.kline_plot.addItem(self.kline_item)

        # 02右侧主界面 02第二层个股数据 01tabK线详情 02成交量vol
            # label
        self.vol_label = LabelItem(text='成交量 单位：万', color=(240, 190, 131), justify='left')
        self.vol_label.setFixedHeight(20)
        self.kchart_layout.addItem(self.vol_label, row=2, col=0)
            # 成交量plot
        self.vol_plot = VolumePlot(self.data_volume_list)
        self.kchart_layout.addItem(self.vol_plot, row=3, col=0)
            # 设置刻度 显示在vol图下方
        self.kline_axis = KlineAxisItem(self.data_klineaxis_list)
        self.vol_plot.setAxisItems({'bottom': self.kline_axis.axis})  # 参数必须为字典，key为 (‘left’, ‘bottom’, ‘right’, ‘top’) ，value为AxisItem()的实例，注意需要加.axis属性才能返回设置好的AxisItem()实例
            # 设置成交量item
        self.volume_item = VolumeItem(self.data_volume)
        self.vol_plot.addItem(self.volume_item)
            # 与k线图显示对齐
        self.vol_plot.setXLink(self.kline_plot)

        # 02右侧主界面 02第二层个股数据 01tabK线详情 03region
            # region plot
        self.region_plot = RegionPlot(self.data_to_region)              # K线的收盘价数据赋予region_plot，创建region_plot
        self.kchart_layout.addItem(self.region_plot, row=4, col=0)
            # 从kline得到的‘close’数据，必须是一维数据，plot到region_plot。生成的region_plot_data用于传递给regionitem
        self.region_plot_data = self.region_plot.plot(self.data_to_region, pen="w")
            # region item
        self.region_item = RegionItem(self.region_plot_data, self.data_to_region)   # region_plot_data是region_plot传递给region_item的数据
        self.region_plot.addItem(self.region_item, ignoreBounds=True)           # "ignoreBounds=True" tell the ViewBox to exclude this item when doing auto-range calculations.
            # kline与region互动
        self.kline_plot.sigRangeChanged.connect(self.region_item.kline_update_region)  # region感应kline
        self.region_item.sigRegionChanged.connect(lambda: self.kline_plot.region_update_kline(self.region_item.getRegion()))  # kline感应region，借助lambda函数把变动范围传递给region，范围是一个元组
        self.region_item.sigRegionChanged.emit(1)                # 为了让kline界面初始化时即与region界面同步，所以emit一次信号。sigRegionChanged需要传一个参数，随便传一个1

        # 02右侧主界面 02第二层个股数据 01tabK线详情 04十字光标
        self.kline_plot.scene().sigMouseMoved.connect(self.kline_plot.mouseMoved)   # scene()只能在mainwindow中使用，在kline_plot类中无法使用
        self.vol_plot.scene().sigMouseMoved.connect(self.vol_plot.mouseMoved)
        self.kline_plot.sigto_vol_cross.connect(self.vol_plot.mouseMovedFromK)      # kline与vol的crosshair同步
        self.vol_plot.sigto_kline_cross.connect(self.kline_plot.mouseMovedFromV)    # kline与vol的crosshair同步

        # 02右侧主界面 02第二层个股数据 02tab基本信息 Widget及Layout
        self.basicinfo_widget = QWidget()
        self.stock_page.addTab(self.basicinfo_widget, "基本信息")
        self.basicinfo_layout = QHBoxLayout()
        self.basicinfo_widget.setLayout(self.basicinfo_layout)
            # 基本信息
        self.basic_info = BasicInfomation(self.data_stockcom)
        self.basicinfo_layout.addLayout(self.basic_info.layout)

        # 02右侧主界面 02第二层个股数据 03tab管理层信息 Widget及Layout
        self.manager_widget = QWidget()
        self.stock_page.addTab(self.manager_widget, "管理层")
        self.manager_layout = QHBoxLayout()
        self.manager_widget.setLayout(self.manager_layout)
            # 连接数据库
        self.conn_manager = QSqlDatabase.addDatabase("QSQLITE", "manager_conn")      # manager_conn只是connection name，用于调用的
        self.conn_manager.setDatabaseName(r"D:\financeDB\SZ000636.sqlite")           # 前面加r表示不转义
        self.conn_manager.open()                                                     # 数据库connection.open()必须置于tablemodel之前，否则内容不显示
            # table
        self.tableModel_manager = QSqlTableModel(db=self.conn_manager)               # 参数只能是QSqlDatabase()
        self.tableModel_manager.setTable("managers")                            # database的表名，会把表头加入tablemodel，但不会加数据
        self.tableModel_manager.select()                                        # database的数据加入tablemodel
        self.tableview_manager = QTableView()
        self.tableview_manager.setModel(self.tableModel_manager)
        self.manager_layout.addWidget(self.tableview_manager)

        # 02右侧主界面 02第二层个股数据 04tab资金流 Widget及Layout
        self.mftab_widget = QWidget()
        self.stock_page.addTab(self.mftab_widget, "资金流")
        self.mftab_layout = QVBoxLayout()
        self.mftab_widget.setLayout(self.mftab_layout)

        # 02右侧主界面 02第二层个股数据 04tab资金流 01资金流图的Widget及Layout
        self.mfchart_widget = GraphicsLayoutWidget()
        self.mftab_layout.addWidget(self.mfchart_widget)
        self.mfchart_layout = self.mfchart_widget.addLayout()   # addLayout()只能创建新GraphicsLayout，如果想加载已有GraphicsLayout，可以使用addItem()。还有一个选项：从QWidget的角度，可以使用setLayout()，但未经实验。
        self.mfchart_layout.setSpacing(0)                       # 布局内item之间的间距
        self.mfchart_layout.setContentsMargins(0, 0, 0, 0)      # 上下左右四个边距

        # 02右侧主界面 02第二层个股数据 04tab资金流 01超大单流入流出
            # moneyflow elg label
        self.mfelg_label = LabelItem(text='超大单流入流出', color=(240, 190, 131), justify='left')
        self.mfelg_label.setFixedHeight(20)
        self.mfchart_layout.addItem(self.mfelg_label, row=1, col=0)
            # moneyflow elg plot
        self.mfelg_plot = MoneyFlowPlot(self.data_moneyflowelg_list, maximumHeight=200)
        self.mfchart_layout.addItem(self.mfelg_plot, row=2, col=0)
            # 设置moneyflow elg item
        self.mfelg_item = MoneyFlowItem(self.data_moneyflowelg)
        self.mfelg_plot.addItem(self.mfelg_item)

        # 02右侧主界面 02第二层个股数据 04tab资金流 02超大单净流入
            # moneyflow net elg plot
        self.mfnetelg_plot = MoneyFlowPlot(self.data_moneyflownetelg_list, maximumHeight=100)
        self.mfchart_layout.addItem(self.mfnetelg_plot, row=3, col=0)
        self.mfnetelg_plot.setXLink(self.mfelg_plot)
            # 设置moneyflow net elg item
        self.mfnetelg_item = MoneyFlowItem(self.data_moneyflownetelg)
        self.mfnetelg_plot.addItem(self.mfnetelg_item)

        # 02右侧主界面 02第二层个股数据 04tab资金流 03大单流入流出
            # moneyflow lg label
        self.mflg_label = LabelItem(text='大单流入流出', color=(240, 190, 131), justify='left')
        self.mflg_label.setFixedHeight(20)
        self.mfchart_layout.addItem(self.mflg_label, row=4, col=0)
            # moneyflow lg plot
        self.mflg_plot = MoneyFlowPlot(self.data_moneyflowlg_list, maximumHeight=200)
        self.mfchart_layout.addItem(self.mflg_plot, row=5, col=0)
        self.mflg_plot.setXLink(self.mfelg_plot)
            # 设置moneyflow lg item
        self.mflg_item = MoneyFlowItem(self.data_moneyflowlg)
        self.mflg_plot.addItem(self.mflg_item)

        # 02右侧主界面 02第二层个股数据 04tab资金流 04大单净流入
            # moneyflow net lg plot
        self.mfnetlg_plot = MoneyFlowPlot(self.data_moneyflownetlg_list, maximumHeight=100)
        self.mfchart_layout.addItem(self.mfnetlg_plot, row=6, col=0)
        self.mfnetlg_plot.setXLink(self.mfelg_plot)
            # 设置刻度 显示在moneyflow图下方
        self.mf_axis = MoneyFlowAxisItem(self.data_moneyflowaxis_list)
        self.mfnetlg_plot.setAxisItems({'bottom': self.mf_axis.axis})  # 参数必须为字典，key为 (‘left’, ‘bottom’, ‘right’, ‘top’) ，value为AxisItem()的实例，注意需要加.axis属性才能返回设置好的AxisItem()实例
            # 设置moneyflow net lg item
        self.mfnetlg_item = MoneyFlowItem(self.data_moneyflownetlg)
        self.mfnetlg_plot.addItem(self.mfnetlg_item)

        # 02右侧主界面 02第二层个股数据 05tab港资持股 Widget及Layout
        self.hkhold_widget = GraphicsLayoutWidget()
        self.stock_page.addTab(self.hkhold_widget, "港资持股")
        self.hkhold_layout = self.hkhold_widget.addLayout()     # addLayout()只能创建新GraphicsLayout，如果想加载已有GraphicsLayout，可以使用addItem()。还有一个选项：从QWidget的角度，可以使用setLayout()，但未经实验。
        self.hkhold_layout.setSpacing(0)                        # 布局内item之间的间距
        self.hkhold_layout.setContentsMargins(0, 0, 0, 0)       # 上下左右四个边距
            # hkhold label
        self.hkhold_label = LabelItem(text='港资持股', color=(240, 190, 131), justify='left')
        self.hkhold_label.setFixedHeight(20)
        self.hkhold_layout.addItem(self.hkhold_label, row=1, col=0)
            # hkhold plot
        self.hkhold_plot = HkHoldPlot(self.data_hkhold_list)
        self.hkhold_layout.addItem(self.hkhold_plot, row=2, col=0)
            # 设置刻度
        self.hkhold_axis = HkHoldAxisItem(self.data_hkholdaxis_list)
        self.hkhold_plot.setAxisItems({'bottom': self.hkhold_axis.axis})  # 参数必须为字典，key为 (‘left’, ‘bottom’, ‘right’, ‘top’) ，value为AxisItem()的实例，注意需要加.axis属性才能返回设置好的AxisItem()实例
            # 设置hkhold item
        self.hkhold_item = HkHoldItem(self.data_hkhold)
        self.hkhold_plot.addItem(self.hkhold_item)

        # 02右侧主界面 02第二层个股数据 06tab资金总图
            # Widget及Layout
        self.capital_widget = CapitalChart(self.data_capital)        # 此处如果在PlotWidget上再添加一个PlotItem，图像显示会倒转，所以只使用一个PlotWidget
        self.stock_page.addTab(self.capital_widget.item, "资金总图")
            # axis
        self.capital_axis = CapitalAxisItem(self.data_capitalaxis_list)
        self.capital_widget.item.setAxisItems({'bottom': self.capital_axis.axis})

        # 02右侧主界面 04第四层回收站
        # 创建一个数据库连接，连接名connection name为“stockrecycle” （It is rather recommended, to connect to the database before creating any window）
        stock_recycle_conn = StockDBConnection("D:/financeDB/StockRecycle.sqlite", "stockrecycle").database     # "stockrecycle"是connection name
        self.recycle_page = QWidget()
        self.stackedlayout.addWidget(self.recycle_page)
        self.recycle_layout = QHBoxLayout()
        self.recycle_page.setLayout(self.recycle_layout)

        # 右侧主界面：第四层，回收站table
        stock_recycle_conn.open()
        headers = ("ts_code", "股票代码", "股票名称", "地域", "所属行业", "市场类型", "上市日期", "股票全称", "英文全称", "拼音缩写",
                   "交易所代码", "交易货币", "L上市D退市P暂停", "H沪股通S深股通N否", "退市日期")
        self.tablemodel2 = StockTableModel(stock_recycle_conn, "stockre", headers)      # "stockre"是数据库的table name
        self.tableview2 = StockTableView()
        self.tableview2.view.setModel(self.tablemodel2.model)
        self.recycle_layout.addWidget(self.tableview2.view)

    def btn_move_to_stockrecycle(self):  # 从stock_collection_page移除到回收站
        # 确认信息框
        messageBox = QMessageBox.warning(
            self,
            "Warning!",
            "确认要移动到回收站吗?",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        )

        if messageBox == QMessageBox.StandardButton.Ok:
            # 从tableview1中，获取选中行的 List[QModelIndex]，用来传递给tablemodel1
            index_list = self.tableview1.view.selectionModel().selectedRows()  # → List[QModelIndex]
            # 抽取数据,从tablemodel1中，到List[QsqlRecord]列表
            records = self.tablemodel1.getDatas(index_list)
            # 传递数据，从List[QsqlRecord]列表，到tablemodel2
            self.tablemodel2.receiveDatas(records)
            # 删除tablemodel1的选定记录
            self.tablemodel1.deleteDatas(index_list)

    def to_stock_collection_page(self):     # 按label1连接到右侧界面stackedlayout的第一页“股票集”
        self.stackedlayout.setCurrentWidget(self.stock_collection_page)

    def to_stock_page(self):                # 按label2连接到右侧界面stackedlayout的第二页“个股数据”
        self.stackedlayout.setCurrentWidget(self.stock_page)

    def to_sm_page(self):                   # 按label3连接到右侧界面stackedlayout的第三个QWidget
        pass

    def to_recycle_page(self):              # 按label4连接到右侧界面stackedlayout的第四页“回收站”
        self.stackedlayout.setCurrentWidget(self.recycle_page)

    def set_state(self):  # 接收鼠标按下BtnLabel的signal，清除其他BtnLabel的按下状态。不适合放回BtnLabel类中，因为与窗体其他BtnLabel和其他组件有互动。
        sender_label = self.sender()  # 提取鼠标按下的那个BtnLabel
        btn_label_list = [self.label1, self.label2, self.label3, self.label4]
        btn_label_list.remove(sender_label)  # 先把鼠标按下的BtnLabel剔除
        for btn_label in btn_label_list:  # 遍历
            if btn_label.press_state == 1:  # 找到状态为1的按钮
                btn_label.press_state = 0  # 先把它的状态设置为0
                btn_label.reset()  # 然后把它重置

    def to_stockvision(self, qModelIndex, table):
        if QGuiApplication.keyboardModifiers() == Qt.KeyboardModifier.AltModifier:      # 判断Alt键是否按下，实现Alt+LeftClick
            record = 0
            # 判断signal来自哪个tab
            if table == "predtable":
                # signal发送的qModelIndex是鼠标点击行row的index，用predtablemodel.getData()，抽取到QsqlRecord
                record = self.predtablemodel.getData(qModelIndex)
            elif table == "selectable":
                record = self.tablemodel1.getData(qModelIndex)
            # 从QsqlRecord中，拿到点击行row的st_code
            ts_code = record.value(0)
            stock_name = record.value(2)
            print(ts_code, stock_name)

            # 左侧按钮界面的按钮设置
            self.label2.press_state = 1     # 状态设置为1，“按下”
            self.label2.reset()             # 重置，使按下效果在界面上显示
                
            # ts_code更新到个股界面
            self.getAndProc_stockDatas(ts_code)
            # 个股界面 数据更新和界面更新
            self.stockUpdate(ts_code, stock_name)
            # 连接到个股界面，右侧界面stackedlayout的第一个QWidget
            self.stackedlayout.setCurrentWidget(self.stock_page)

    # 个股界面 数据更新和界面更新
    def stockUpdate(self, ts_code, stock_name):

        # 01日线
            # 十字光标的删除必须放最前面，否则会把刷新后的十字光标删除
        self.kline_plot.removeItem(self.kline_plot.vLine)
        self.kline_plot.removeItem(self.kline_plot.hLine)
        self.vol_plot.removeItem(self.vol_plot.vLine)
        self.vol_plot.removeItem(self.vol_plot.hLine)
            # 日线label
        self.k_label.setText("日线  " + stock_name + "  " + ts_code)
            # 日线plot
        self.kline_plot.setData(self.data_kline_list)
        self.kline_plot.createPlot()
            # 日线item
        self.kline_item.setData(self.data_kline_candlestick)
        self.kline_item.generatePicture()
            # 成交量plot
        self.vol_plot.setData(self.data_volume_list)
        self.vol_plot.createPlot()
            # 刻度axis
        self.kline_axis.setData(self.data_klineaxis_list)
        self.kline_axis.createAxis()
            # 成交量item
        self.volume_item.setData(self.data_volume)
        self.volume_item.generatePicture()
            # region plot
        self.region_plot.setData(self.data_to_region)
        self.region_plot.createPlot()
            # 从kline得到的‘close’数据，必须是一维数据，plot到region_plot。生成的region_plot_data用于传递给regionitem
        self.region_plot_data = self.region_plot.plot(self.data_to_region, pen="w", clear=True)     # region_plot的第1个item (clear=True，plot前，先清除之前的plots)
            # region item
        self.region_item.setData(self.region_plot_data, self.data_to_region)
        self.region_item.generatePicture()
        self.region_plot.addItem(self.region_item, ignoreBounds=True)                   # region_plot的第2个item

        # 02公司基本信息
            # 先删除self.basic_info.layout的旧组件（这里因为BasicInfomation()不是用的继承方法，而是工厂方法，每次调用createBscPrp()，全部组件都会new一遍，而旧组件会挡住新组件）
        while self.basic_info.layout.count():
            child = self.basic_info.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.basicinfo_layout.takeAt(0).deleteLater()         # 把self.basic_info.layout也删掉

        self.basic_info.setData(self.data_stockcom)
        self.basic_info.layout = self.basic_info.createBscPrp()
        self.basicinfo_layout.addLayout(self.basic_info.layout)    # 组件都删完了，需要把self.basic_info.layout再安装一下

        # 03管理层
        filename = ts_code[7:9] + ts_code[:6]
        self.conn_manager.setDatabaseName(r"D:\financeDB\%s.sqlite" % filename)
        self.conn_manager.open()  # 数据库connection.open()必须置于tablemodel之前，否则内容不显示
        self.tableModel_manager.select()  # database的数据加入tablemodel

        # 资金流
            # elg plot
        self.mfelg_plot.setData(self.data_moneyflowelg_list, maximumHeight=200)
        self.mfelg_plot.createPlot()
            # elg item
        self.mfelg_item.setData(self.data_moneyflowelg)
        self.mfelg_item.generatePicture()
            # net elg plot
        self.mfnetelg_plot.setData(self.data_moneyflownetelg_list, maximumHeight=100)
        self.mfnetelg_plot.createPlot()
            # net elg item
        self.mfnetelg_item.setData(self.data_moneyflownetelg)
        self.mfnetelg_item.generatePicture()
            # lg plot
        self.mflg_plot.setData(self.data_moneyflowlg_list, maximumHeight=200)
        self.mflg_plot.createPlot()
            # lg item
        self.mflg_item.setData(self.data_moneyflowlg)
        self.mflg_item.generatePicture()
            # net lg plot
        self.mfnetlg_plot.setData(self.data_moneyflownetlg_list, maximumHeight=100)
        self.mfnetlg_plot.createPlot()
            # 刻度
        self.mf_axis.setData(self.data_moneyflowaxis_list)
        self.mf_axis.createAxis()
            # net lg item
        self.mfnetlg_item.setData(self.data_moneyflownetlg)
        self.mfnetlg_item.generatePicture()

        # 港资
            # hkhold plot
        self.hkhold_plot.setData(self.data_hkhold_list)
        self.hkhold_plot.createPlot()
            # 刻度
        self.hkhold_axis.setData(self.data_hkholdaxis_list)
        self.hkhold_axis.createAxis()
            # hkhold item
        self.hkhold_item.setData(self.data_hkhold)
        self.hkhold_item.generatePicture()

        # 资金总图
        self.capital_widget.item.clear()                # 先删除self.capital_widget.item的旧组件
        self.capital_widget.item.deleteLater()          # 把self.capital_widget.item自身也删掉

        self.capital_widget.setData(self.data_capital)
        self.capital_widget.item = self.capital_widget.createChart()
        self.stock_page.addTab(self.capital_widget.item, "资金总图")
            # 刻度
        self.capital_axis.setData(self.data_capitalaxis_list)
        self.capital_axis.axis = self.capital_axis.createAxis()
        self.capital_widget.item.setAxisItems({'bottom': self.capital_axis.axis})

    # def keyPressEvent(self, event):
    #     modifiers = event.modifiers()
    #     if modifiers == Qt.KeyboardModifier.ShiftModifier:
    #         print("Shift 键被按下了！")
    #     elif modifiers == Qt.KeyboardModifier.ControlModifier:
    #         print("Ctrl 键被按下了！")
    #     elif modifiers == Qt.KeyboardModifier.AltModifier:
    #         print("Alt 键被按下了！")

    def getAndProc_stockDatas(self, ts_code):
        # SqliteConnection()取数据
        if ts_code == "":
            ts_code = "000636.SZ"
        sqlite_conn = SqliteConnection(ts_code)
        data_fromdb_daily = sqlite_conn.dataFromDB_daily()                         # 01日线            K线
        data_fromdb_stockcom = sqlite_conn.dataFromDB_stockcom()                   # 02公司基本信息      基本信息
        data_fromdb_managers = sqlite_conn.dataFromDB_managers()                   # 03管理层           资金总图
        data_fromdb_stkrewards = sqlite_conn.dataFromDB_stkrewards()               # 04管理层薪酬及持股   资金总图
        data_fromdb_moneyflow = sqlite_conn.dataFromDB_moneyflow()                 # 05资金流           资金流
        data_fromdb_hkhold = sqlite_conn.dataFromDB_hkhold()                       # 06港资             港资持股    资金总图
        data_fromdb_top10holders = sqlite_conn.dataFromDB_top10holders()           # 07十大股东          资金总图
        data_fromdb_top10floatholders = sqlite_conn.dataFromDB_top10floatholders() # 08十大流通股股东     资金总图
        data_fromdb_margindetail = sqlite_conn.dataFromDB_margindetail()           # 09融资融券          资金总图
        data_fromdb_bakdaily = sqlite_conn.dataFromDB_bakdaily()                   # 13备用行情（获得总股本）资金总图
        data_fromdb_tradecal = sqlite_conn.dataFromDB_tradecal()                   # 16交易日历（全局）    资金总图
        sqlite_conn.close()  # 数据采集完成后，关闭数据库

        # DataProcessor()处理数据，列示控件所需全部数据
        data_processor = DataProcessor(data_fromdb_daily, data_fromdb_stockcom, data_fromdb_managers,
                                       data_fromdb_stkrewards, data_fromdb_moneyflow, data_fromdb_hkhold,
                                       data_fromdb_top10holders, data_fromdb_top10floatholders,
                                       data_fromdb_margindetail, data_fromdb_bakdaily, data_fromdb_tradecal)
        self.data_kline_candlestick = data_processor.data_kline_candlestick             # 用于K线Item
        self.data_to_region = data_processor.data_to_region                             # 用于region初始化
        self.data_kline_list = data_processor.data_kline_list                           # 用于K线Plot
        self.data_volume = data_processor.data_volume                                   # 用于成交量Item
        self.data_volume_list = data_processor.data_volume_list                         # 用于成交量Plot
        self.data_klineaxis_list = data_processor.data_klineaxis_list                   # 用于kline_axis
        self.data_stockcom = data_processor.data_stockcom                               # 用于基本信息
        self.data_moneyflowelg = data_processor.data_moneyflowelg                       # 用于资金流elg Item
        self.data_moneyflowelg_list = data_processor.data_moneyflowelg_list             # 用于资金流elg Plot
        self.data_moneyflownetelg = data_processor.data_moneyflownetelg                 # 用于资金流净值elg Item
        self.data_moneyflownetelg_list = data_processor.data_moneyflownetelg_list       # 用于资金流净值elg Plot
        self.data_moneyflowlg = data_processor.data_moneyflowlg                         # 用于资金流lg Item
        self.data_moneyflowlg_list = data_processor.data_moneyflowlg_list               # 用于资金流lg Plot
        self.data_moneyflownetlg = data_processor.data_moneyflownetlg                   # 用于资金流净值lg Item
        self.data_moneyflownetlg_list = data_processor.data_moneyflownetlg_list         # 用于资金流净值lg Plot
        self.data_moneyflowaxis_list = data_processor.data_moneyflowaxis_list           # 用于资金流axis
        self.data_hkhold = data_processor.data_hkhold                                   # 用于港资Item
        self.data_hkhold_list = data_processor.data_hkhold_list                         # 用于港资PLot
        self.data_hkholdaxis_list = data_processor.data_hkholdaxis_list                 # 用于港资axis
        self.data_capital = data_processor.data_caspital                                # 用于资金总图
        self.data_capitalaxis_list = data_processor.data_capitalaxis_list               # 用于资金总图axis
