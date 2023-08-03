from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QLabel, QFrame
from PyQt6.QtCore import pyqtSignal, Qt


class BtnLabel(QLabel):
    mousepress_signal = pyqtSignal()
    mousemove_signal = pyqtSignal()

    def __init__(self, label_text):
        super().__init__()
        # 不变的属性
        self.setText(label_text)
        self.setFrameShape(QFrame.Shape.Panel)          # 不要设置为STYLEDpanel，否则后面的一些属性设置无效，因为styled是与整个窗口风格相适应。
        self.setLineWidth(2)
        # 随鼠标变化的属性
        self.setMouseTracking(True)                     # 窗口部件跟踪鼠标是否生效。如果鼠标跟踪失效（默认），当鼠标被移动的时候只有在至少一个鼠标按键被按下时，这个窗口部件才会接收鼠标移动事件。
        self.setAutoFillBackground(True)                # 不加这句，则颜色不生效
        self.palette = QPalette()
        self.press_state = 0                            # 鼠标按下状态，自定义状态，0未按状态，1按下状态，初始化为0。
        self.reset()                                    # 既为初始化设置，鼠标事件后也调用来重新设置属性。

    def reset(self):                                    # 按键的主要效果都在本方法中，通过判断按键状态0或1，进行相应加载
        if self.press_state == 0:
            self.setFrameShadow(QFrame.Shadow.Raised)
            self.palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
            self.setPalette(self.palette)
        elif self.press_state == 1:
            self.setFrameShadow(QFrame.Shadow.Sunken)
            self.palette.setColor(QPalette.ColorRole.Window, QColor(255, 218, 185))
            self.setPalette(self.palette)

    def mousePressEvent(self, e):                       # 鼠标按下，发送signal给MainWindow
        self.mousepress_signal.emit()                   # 分发给两个slot，一个负责展示右侧界面QStackedLayout的相应页面，另一个负责清除其他BtnLabel的按下状态。
        self.press_state = 1                            # 设置本BtnLabel的状态为1按下
        self.reset()                                    # 重新设置本BtnLabel

    def enterEvent(self, e):                            # 鼠标进入，不需要判断鼠标的按下状态press_state
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.palette.setColor(QPalette.ColorRole.Window, QColor(255, 218, 185))
        self.setPalette(self.palette)

    def leaveEvent(self, e):                            # 鼠标离开
        self.reset()                                    # 在BtnLabel的任一状态下，leaveEvent的效果与BtnLabel的效果都一致，所以事件发生时reset()就可以
