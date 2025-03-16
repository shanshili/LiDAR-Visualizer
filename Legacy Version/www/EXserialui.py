import sys

from PySide2.QtCore import Slot, QTimer, QObject, Signal
from PySide2.QtWidgets import QMainWindow, QApplication, QMessageBox, QTextBrowser
from ui_Serial import Ui_MainWindow  # 调用包中的Ui_MainWindow类
import serial
from serial.tools import list_ports
import threading

# 定义数据接收类
class QmyMain_Screen_Uart_RX_Data_Signal(QObject):
    text = Signal(QTextBrowser, str)    # 定义信号


# 实例化类
Uart_RX_Data_Signal = QmyMain_Screen_Uart_RX_Data_Signal()


class QmyMain_Screen(QMainWindow):

    # 析构函数 类结束之后调用的方法
    def __del__(self):
        print("__del__")

    # 构造函数，在调用类之后就会执行的方法
    def __init__(self, parent=None):
        super(QmyMain_Screen, self).__init__(parent)  # 调用父类中的__init__方法
        self.ui = Ui_MainWindow()  # 实例化类 我们在这里定义实例化对象名带有ui 这样我们后面在调用的时候就可
        # 以方便知道那部分是ui中的方法，那部分是我们逻辑中大方法，实现ui和逻辑代码的区分和隔离
        self.ui.setupUi(self)  # 调用ui中类 实现界面加载显示

        self.Serial = serial.Serial()           # 实例化串口
        self.Serial_Next_Port_Number = []       # 上次串口号
        self.Serial_Open_state = False          # 串口打开标志
        # 创建一个线程用来接收串口数据
        self.Serial_Data_RX_Thread = threading.Thread(target=self.Serial_Data_RX_Thread_Function, daemon=True)

        self.Serial_Port_Check_Timer = QTimer()                                                 # 实例化类
        self.Serial_Port_Check_Timer.setInterval(1000)                                          # 设置定时器时间周期
        self.Serial_Port_Check_Timer.timeout.connect(self.Serial_Port_Check_Timer_Timeout)      # 设置并关联定时器槽函数
        self.Serial_Port_Check_Timer.start()                                                    # 启动定时器

        self.Serial_Next_Port_Number = self.Serial_Scan_Uart_Port()                             # 获取下当前的所有
        self.ui.cBox_Serial_Port_Number.addItems(self.Serial_Next_Port_Number)                  # 将串口数据添加到组合编辑框中

        self.ui.pBtn_Serial_Send_Data.clicked.connect(self.pBtn_Serial_Send_Data_Slot)          # 连接槽函数
        self.ui.pBtn_Serial_Open.clicked.connect(self.pBtn_Serial_Open_Slot)                    # 连接槽函数
        self.ui.pBtn_Serial_Close.clicked.connect(self.pBtn_Serial_Close_Slot)                  # 连接槽函数
        self.ui.pBtn_Serial_Clear_RX_Data.clicked.connect(self.pBtn_Serial_Clear_RX_Data_Slot)  # 连接槽函数
        self.ui.pBtn_Serial_Clear_TX_Data.clicked.connect(self.pBtn_Serial_Clear_TX_Data_Slot)  # 连接槽函数
        Uart_RX_Data_Signal.text.connect(self.Uart_RX_Data_Signal_Print_Data_to_Gui)            # 连接槽函数

    # 静态方法 作为被关联的槽函数
    @staticmethod
    def Uart_RX_Data_Signal_Print_Data_to_Gui(my_QTextBrowser, text):
        my_QTextBrowser.append(str(text))                                    # 添加数据
        my_QTextBrowser.ensureCursorVisible()                                # 确保光标可见
        my_QTextBrowser.moveCursor(my_QTextBrowser.textCursor().End)         # 将光标移动到最后

    # 串口接收数据线程
    def Serial_Data_RX_Thread_Function(self):
        while True:
            try:
                if self.Serial.is_open:                     # 串口打开则接收数据
                    get_data = self.Serial.readline()       # 读取串口数据
                    if get_data.decode('utf-8'):            # 将str数据转换成 utf-8格式判断其是否不为空
                        # 信号发送数据，信号绑定槽函数就会执行槽函数
                        Uart_RX_Data_Signal.text.emit(self.ui.tB_Serial_Data_RX_Show, get_data.decode('utf-8'))
            except Exception as error:
                print(error)

    # 定时器检测串口号是否发生变化
    def Serial_Port_Check_Timer_Timeout(self):
        now_port = self.Serial_Scan_Uart_Port()         # 获取当前的所有串口
        if now_port == self.Serial_Next_Port_Number:    # 串口不变的情况下
            pass
        else:  # 串口有变化的时候
            # 当前连接的串口不在了 可能被拔出了
            try:
                if self.Serial.is_open and (now_port != self.Serial_Next_Port_Number):
                    QMessageBox.information(self, "Error", "串口已拔出", QMessageBox.Yes, QMessageBox.Yes)
                    # print("当前连接的串口不在了", now_port)
                    self.Serial.close()                             # 关闭串口
                    self.ui.pBtn_Serial_Close.setEnabled(True)      # 使能点击状态
                    self.ui.pBtn_Serial_Open.setEnabled(True)       # 使能点击状态
            except Exception as error:
                print(error)
            finally:
                # print("串口发生变化", now_port)
                self.ui.cBox_Serial_Port_Number.clear()             # 先清空原有数据
                self.ui.cBox_Serial_Port_Number.addItems(now_port)  # 将变化的添加到列表中
                self.Serial_Next_Port_Number = now_port             # 更新上一次串口号

    # 扫描串口号
    @staticmethod
    def Serial_Scan_Uart_Port():
        Serial_port_List = list(serial.tools.list_ports.comports())  # 获取串口列表
        now_port = []  # 清空列表数据
        for number in Serial_port_List:     # 循环获取列表中单个元素
            # 单个元素为类 serial.tools.list_ports.ListPortInfo 获取类中的 device 属性，添加在列表中
            now_port.append(number.device)  # 将串口设备添加到列表中
        return now_port  # 返回列表

    # 发送数据按钮槽函数
    @Slot()
    def pBtn_Serial_Send_Data_Slot(self):
        text = self.ui.lEdit_Serial_Send_Data.text()        # 获取输入内容
        try:
            if text and self.Serial.is_open:
                # print(text.encode('utf-8'))
                self.Serial.write(text.encode('utf-8'))     # 发送数据将数据转换成 utf-8 格式发送
        except Exception as error:
            print(error)

    # 打开串口槽函数
    @Slot()
    def pBtn_Serial_Open_Slot(self):
        stop_bit = (1, 1.5, 2)
        check_bit = ('N', 'O', 'E')  # 'N' 无校验 'O' 奇校验 'E'偶校验
        choice_serial_port_number = self.ui.cBox_Serial_Port_Number.currentText()
        choice_serial_baud_rate = int(self.ui.cBox_Serial_Baud_Rate.currentText())
        choice_serial_data_bit = int(self.ui.cBox_Serial_Data_Bit.currentText())
        choice_serial_check_bit = self.ui.cBox_Serial_Check_Bit.currentIndex()
        choice_serial_stop_bit = self.ui.cBox_Serial_Stop_Bit.currentIndex()
        # print("open serial", choice_serial_port_number,
        #       choice_serial_baud_rate,
        #       choice_serial_data_bit,
        #       check_bit[choice_serial_check_bit],
        #       stop_bit[choice_serial_stop_bit]
        #       )
        try:
            self.Serial = serial.Serial(port=choice_serial_port_number,
                                        baudrate=choice_serial_baud_rate,
                                        bytesize=choice_serial_data_bit,
                                        parity=check_bit[choice_serial_check_bit],
                                        stopbits=stop_bit[choice_serial_stop_bit])
            if self.Serial.is_open:
                self.ui.pBtn_Serial_Open.setEnabled(False)
                self.ui.pBtn_Serial_Close.setEnabled(True)
                self.ui.cBox_Serial_Port_Number.setEnabled(False)
                self.ui.cBox_Serial_Baud_Rate.setEnabled(False)
                self.ui.cBox_Serial_Data_Bit.setEnabled(False)
                self.ui.cBox_Serial_Stop_Bit.setEnabled(False)
                self.ui.cBox_Serial_Check_Bit.setEnabled(False)
                print("串口已经打开", self.Serial.name)
        except Exception as error:
            if "拒绝访问" in str(error):
                QMessageBox.information(self, "Error", "串口拒绝访问", QMessageBox.Yes, QMessageBox.Yes)
            else:
                QMessageBox.information(self, "Error", "打开失败", QMessageBox.Yes, QMessageBox.Yes)
            self.ui.pBtn_Serial_Open.setEnabled(True)
            print(error)
        # 判断第一次打开串口之后才开启线程不然，在创建就打开的时候会影响软件打开速度
        if self.Serial.is_open and (not self.Serial_Open_state):    # 串口打开成功
            self.Serial_Data_RX_Thread.start()                      # 开启线程
            self.Serial_Open_state = True                           # 设置打开标志位 防止重复开启线程

    # 关闭按钮槽函数
    @Slot()
    def pBtn_Serial_Close_Slot(self):
        try:
            if self.Serial.is_open:
                self.ui.pBtn_Serial_Close.setEnabled(False)
                self.ui.pBtn_Serial_Open.setEnabled(True)
                self.ui.cBox_Serial_Port_Number.setEnabled(True)
                self.ui.cBox_Serial_Baud_Rate.setEnabled(True)
                self.ui.cBox_Serial_Data_Bit.setEnabled(True)
                self.ui.cBox_Serial_Stop_Bit.setEnabled(True)
                self.ui.cBox_Serial_Check_Bit.setEnabled(True)
                self.Serial.close()
        except Exception as error:
            self.ui.pBtn_Serial_Close.setEnabled(True)
            print(error)

    # 清空接收数据按钮槽函数
    @Slot()
    def pBtn_Serial_Clear_RX_Data_Slot(self):
        self.ui.tB_Serial_Data_RX_Show.clear()

    # 清空发送数据按钮槽函数
    @Slot()
    def pBtn_Serial_Clear_TX_Data_Slot(self):
        self.ui.lEdit_Serial_Send_Data.clear()


if __name__ == "__main__":
    # 初始化窗口系统并且使用在argv中的argc个命令行参数构造一个应用程序对象app
    app = QApplication(sys.argv)
    # 实例化对象
    my_Main_Screen = QmyMain_Screen()
    # 调用类中的方法
    my_Main_Screen.show()
    # 1.app.exec_()的作用是运行主循环，必须调用此函数才能开始事件处理，调用该方法进入程序的主循环直到调用exit（）结束。
    # 主事件循环从窗口系统接收事件，并将其分派给应用程序小部件。如果没有该方法，那么在运行的时候还没有进入程序的主循环就
    # 直接结束了，所以运行的时候窗口会闪退。
    # app.exec_()在退出时会返回状态代码
    # 2.不用sys.exit(app.exec_()),只使用app.exec_()，程序也可以正常运行，但是关闭窗口后进程却不会退出。
    # sys.exit(n)的作用是退出应用程序并返回n到父进程
    sys.exit(app.exec_())
