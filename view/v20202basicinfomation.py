from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QGridLayout, QLineEdit, QTextEdit


class BasicInfomation:
    def __init__(self, data_stockcom):

        self.setData(data_stockcom)

        self.layout = self.createBscPrp()

    def setData(self, data_stockcom):
        self.data_stockcom = data_stockcom


    def createBscPrp(self):
        title = QLabel("基本信息")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label01 = QLabel("公告日期:")
        text01 = QLineEdit(self.data_stockcom[0])
        label02 = QLabel("交易所")
        text02 = QLineEdit(self.data_stockcom[1])
        label03 = QLabel("法人代表")
        text03 = QLineEdit(self.data_stockcom[2])
        label04 = QLabel("总经理")
        text04 = QLineEdit(self.data_stockcom[3])
        label05 = QLabel("董秘")
        text05 = QLineEdit(self.data_stockcom[4])
        label06 = QLabel("注册资本")
        text06 = QLineEdit(str(self.data_stockcom[5]))
        label07 = QLabel("注册日期")
        text07 = QLineEdit(self.data_stockcom[6])
        label08 = QLabel("省份")
        text08 = QLineEdit(self.data_stockcom[7])
        label09 = QLabel("城市")
        text09 = QLineEdit(self.data_stockcom[8])
        label10 = QLabel("人数")
        text10 = QLineEdit(str(self.data_stockcom[9]))
        label11 = QLabel("办公室")
        text11 = QLineEdit(self.data_stockcom[10])
        label12 = QLabel("公司主页")
        text12 = QLineEdit(self.data_stockcom[11])
        label13 = QLabel("公司介绍")
        text13 = QTextEdit(self.data_stockcom[12])
        label14 = QLabel("公司介绍")
        text14 = QTextEdit(self.data_stockcom[13])
        label15 = QLabel("公司介绍")
        text15 = QTextEdit(self.data_stockcom[14])

        layout = QGridLayout()
        layout.addWidget(title, 0, 0, 1, 4)
        layout.addWidget(label01, 1, 0)
        layout.addWidget(text01, 1, 1)
        layout.addWidget(label02, 1, 2)
        layout.addWidget(text02, 1, 3)
        layout.addWidget(label03, 2, 0)
        layout.addWidget(text03, 2, 1)
        layout.addWidget(label04, 3, 0)
        layout.addWidget(text04, 3, 1)
        layout.addWidget(label05, 4, 0)
        layout.addWidget(text05, 5, 1)
        layout.addWidget(label06, 2, 2)
        layout.addWidget(text06, 2, 3)
        layout.addWidget(label07, 3, 2)
        layout.addWidget(text07, 3, 3)
        layout.addWidget(label08, 5, 0)
        layout.addWidget(text08, 5, 1)
        layout.addWidget(label09, 5, 2)
        layout.addWidget(text09, 5, 3)
        layout.addWidget(label10, 6, 0)
        layout.addWidget(text10, 6, 1)
        layout.addWidget(label11, 6, 2)
        layout.addWidget(text11, 6, 3)
        layout.addWidget(label12, 7, 0)
        layout.addWidget(text12, 7, 1)
        layout.addWidget(label13, 8, 0)
        layout.addWidget(text13, 8, 1, 1, 3)
        layout.addWidget(label14, 9, 0)
        layout.addWidget(text14, 9, 1, 1, 3)
        layout.addWidget(label15, 10, 0)
        layout.addWidget(text15, 10, 1, 1, 3)
        return layout

