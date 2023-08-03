from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QKeyEvent
from PyQt6.QtWidgets import QTableView, QAbstractItemView, QFrame


class StockTableView:

    def __init__(self):
        self.view = self.createView()
        #self.view.clicked.connect(self.mousePressed)

    def createView(self):
        tableView = QTableView()
        tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)      # 设置只能选中整行
        tableView.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)       # 设置只能选中多行
        tableView.setSortingEnabled(True)                                                   # 点击标题排序
        tableView.resizeColumnsToContents()
        tableView.setAlternatingRowColors(True)                                             # 行间隔颜色
        tableView.setStyleSheet('gridline-color:white;border:0px solid gray')               # tableView内无框线；tableView无外框
        return tableView

    # def keyPressed(self):                       # 鼠标按下，发送signal给MainWindow
    #     e = QKeyEvent()
    #     qKeyEvent = self.view.keyPressEvent(e)
    #     return qKeyEvent
