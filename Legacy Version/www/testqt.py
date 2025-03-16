"""
ScanPort 有问题待调试
keyerror下标溢出
"""
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys
import serial
from serial.tools import list_ports

class MyWindow(QWidget):
    _translate = QCoreApplication.translate
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.mSerial = serial.Serial()
        self.ScanComPort()
        self.SelectComPort()

        #self.ScanPort.clicked.connect(self.ScanComPort)
        self.Open.clicked.connect(self.OpenComPort)
        self.Close.clicked.connect(self.CloseComPort)
        self.comPort.currentIndexChanged.connect(self.SelectComPort)

        self.mTimer = QTimer()
        # self.mTimer.timeout.connect(self.ReceiverPortData)

    def init_ui(self):
        self.ui = uic.loadUi('F:/Tech/qtdesigner/serialshow.ui')
        
        self.ScanPort = self.ui.ScanPort
        self.Open = self.ui.Open
        self.Close = self.ui.Close
        self.comPort = self.ui.comPort
        self.comBaud = self.ui.comBaud
        self.label = self.ui.label


    def ScanComPort(self):
        self.comPort.clear() #list.clear()
        self.portDict = {}
        portlist = list(list_ports.comports())
        for port in portlist:
            print(port)
            self.portDict["%s" % port[0]] = "%s" % port[1] 
            self.comPort.addItem(port[0])
        if len(self.portDict) == 0:
            QMessageBox.critical(self, "警告", "未找到串口设备！", QMessageBox.Cancel, QMessageBox.Cancel)
        pass
     
    def SelectComPort(self):
        if len(self.portDict) > 0 :
            self.label.setText(self.portDict[self.comPort.currentText()])
        else:
            self.label.setText("未检测到串口设备！")
        pass
    
    def OpenComPort(self):
        self.mSerial.port = self.comPort.currentText()
        self.mSerial.baudrate = int(self.comBaud.currentText())
 
        if self.mSerial.isOpen():
            QMessageBox.warning(self, "警告", "串口已打开", QMessageBox.Cancel, QMessageBox.Cancel)
        else:
            try:
                self.Open.setEnabled(False)
                self.mSerial.open()
                self.mSerial.flushInput()
                self.mSerial.flushOutput()
                self.mTimer.start(1)
            except:
                QMessageBox.critical(self, "警告", "串口打开失败！", QMessageBox.Cancel, QMessageBox.Cancel)
                self.Open.setEnabled(True)
        print(self.mSerial)
        pass
 
    def CloseComPort(self):
        self.mTimer.stop()
        if self.mSerial.isOpen():
            self.Open.setEnabled(True)
            self.mSerial.flushInput()
            self.mSerial.flushOutput()
            self.mSerial.close()
        pass

    # def ReceiverPortData(self):
    #     '''
    #     接收串口数据，并解析出每一个数据项更新到波形图
    #     数据帧格式'$$:95.68,195.04,-184.0\r\n'
    #     每个数据帧以b'$$:'开头，每个数据项以','分割
    #     '''
    #     try:
    #         n = self.mSerial.inWaiting()
    #     except:
    #         self.CloseComPort()
        
    #     if n > 0:
    #         # 端口缓存内有数据
    #         try:
    #             self.recvdata = self.mSerial.readline(1024) # 读取一行数据最大长度1024字节

    #         except:
    #             pass
    #     pass
 
# class SerialReceiveThread(QThread,MyWindow):
#     def __init__(self):
#         super(SerialReceiveThread,self).__init__()
#     def run(self):       
#         while True:
#            jsondata = x.mSerial.readline().decode()  

if __name__ == '__main__':
    app = QApplication(sys.argv)
    x = MyWindow()
    # d = SerialReceiveThread()
    x.ui.show()
    # d.run()
    app.exec()