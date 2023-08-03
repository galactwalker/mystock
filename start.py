import sys
from PyQt6.QtWidgets import QApplication
from view.mainwindow import Window

"""
    设计思路：大多数类都是使用的一种思路，不继承类，而是创建一个相关类，以这个是相关类的一个属性来实例化一个类的设置好的对象，譬如StockTableView类中：
    self.view = self.createView()
    def createView(self):
        tableView = QTableView()
        ...
        return tableView
    工厂设计模式因为无法直接使用类中的方法而被放弃，改用继承。
"""

app = QApplication(sys.argv)

mainWindow = Window()
mainWindow.show()

sys.exit(app.exec())
