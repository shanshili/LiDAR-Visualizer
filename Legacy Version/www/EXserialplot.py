import sys
import numpy as np

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import serial
import serial.tools.list_ports
from ui_main import Ui_MainWindow
import pyqtgraph as pg


class AppMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(AppMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("串口数据波形显示工具")
        self.PosX = 0
        self.dataIndex = 0          # 数据列表当前索引
        self.dataMaxLength = 10000  # 数据列表最大长度
        self.dataheader = b'$$:'    # 数据帧开头
        self.dataX = np.zeros(self.dataMaxLength, dtype=float)
        self.dataY = np.zeros(self.dataMaxLength, dtype=float)
        self.dataZ = np.zeros(self.dataMaxLength, dtype=float)
        self.dataH = np.zeros(self.dataMaxLength, dtype=float)

        self.mSerial = serial.Serial()
        self.ScanComPort()
        self.SelectComPort()
        
        self.btnScanPort.clicked.connect(self.ScanComPort)
        self.btnOpenPort.clicked.connect(self.OpenComPort)
        self.btnClosePort.clicked.connect(self.CloseComPort)
        self.cmbComPort.currentIndexChanged.connect(self.SelectComPort)

        self.mTimer = QTimer()
        self.mTimer.timeout.connect(self.ReceiverPortData)

        self.plotM.setAntialiasing(True)
        # self.plotM.setBackground()
        self.canvasX = self.plotM.plot(self.dataX, pen=pg.mkPen(color='r', width=1))
        self.canvasY = self.plotM.plot(self.dataY, pen=pg.mkPen(color='g', width=1))
        self.canvasZ = self.plotM.plot(self.dataZ, pen=pg.mkPen(color='b', width=1))
        self.canvasH = self.plotM.plot(self.dataH, pen=pg.mkPen(color='y', width=1))

    def ScanComPort(self):
        self.cmbComPort.clear()
        self.portDict = {}
        portlist = list(serial.tools.list_ports.comports())
        for port in portlist:
            self.portDict["%s" % port[0]] = "%s" % port[1]
            self.cmbComPort.addItem(port[0])
        if len(self.portDict) == 0:
            QMessageBox.critical(self, "警告", "未找到串口设备！", QMessageBox.Cancel, QMessageBox.Cancel)
        pass
    
    def SelectComPort(self):
        if len(self.portDict) > 0 :
            self.labComPortName.setText(self.portDict[self.cmbComPort.currentText()])
        else:
            self.labComPortName.setText("未检测到串口设备！")
        pass

    def OpenComPort(self):
        self.mSerial.port = self.cmbComPort.currentText()
        self.mSerial.baudrate = int(self.cmbBaudrate.currentText())

        if self.mSerial.isOpen():
            QMessageBox.warning(self, "警告", "串口已打开", QMessageBox.Cancel, QMessageBox.Cancel)
        else:
            try:
                self.btnOpenPort.setEnabled(False)
                self.mSerial.open()
                self.mSerial.flushInput()
                self.mSerial.flushOutput()
                self.mTimer.start(1)
            except:
                QMessageBox.critical(self, "警告", "串口打开失败！", QMessageBox.Cancel, QMessageBox.Cancel)
                self.btnOpenPort.setEnabled(True)
        print(self.mSerial)
        pass

    def CloseComPort(self):
        self.mTimer.stop()
        if self.mSerial.isOpen():
            self.btnOpenPort.setEnabled(True)
            self.mSerial.flushInput()
            self.mSerial.flushOutput()
            self.mSerial.close()
        pass

    def ReceiverPortData(self):
        '''
        接收串口数据，并解析出每一个数据项更新到波形图
        数据帧格式'$$:95.68,195.04,-184.0\r\n'
        每个数据帧以b'$$:'开头，每个数据项以','分割
        '''
        try:
            n = self.mSerial.inWaiting()
        except:
            self.CloseComPort()

        if n > 0:
            # 端口缓存内有数据
            try:
                self.recvdata = self.mSerial.readline(1024) # 读取一行数据最大长度1024字节

                if self.recvdata.decode('UTF-8').startswith(self.dataheader.decode('UTF-8')):
                    rawdata = self.recvdata[len(self.dataheader) : len(self.recvdata) - 2]
                    data = rawdata.split(b',')
                    # print(rawdata)
                    
                    if self.dataIndex < self.dataMaxLength:
                        # 接收到的数据长度小于最大数据缓存长度，直接按索引赋值，索引自增1
                        # print(rawdata, rawdata[0], rawdata[1], rawdata[2], self.dataX[self.dataIndex], self.dataY[self.dataIndex], self.dataZ[self.dataIndex])
                        self.dataX[self.dataIndex] = float(data[0])
                        self.dataY[self.dataIndex] = float(data[1])
                        self.dataZ[self.dataIndex] = float(data[2])
                        self.dataH[self.dataIndex] = float(data[3])
                        self.dataIndex = self.dataIndex + 1
                    else:
                        # 寄收到的数据长度大于或等于最大数据缓存长度，丢弃最前一个数据新数据添加到数据列尾
                        self.dataX[:-1] = self.dataX[1:]
                        self.dataY[:-1] = self.dataY[1:]
                        self.dataZ[:-1] = self.dataZ[1:]
                        self.dataH[:-1] = self.dataH[1:]

                        self.dataX[self.dataIndex - 1] = float(data[0])
                        self.dataY[self.dataIndex - 1] = float(data[1])
                        self.dataZ[self.dataIndex - 1] = float(data[2])
                        self.dataH[self.dataIndex - 1] = float(data[3])
                    
                    # 更新波形数据
                    self.canvasX.setData(self.dataX)
                    self.canvasY.setData(self.dataY)
                    self.canvasZ.setData(self.dataZ)
                    self.canvasH.setData(self.dataH)

                    # self.canvasX.setPos(self.PosX, 0)
                    # self.canvasY.setPos(self.PosX, 0)
                    # self.canvasZ.setPos(self.PosX, 0)
            except:
                pass
        pass

    def SendPortData(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AppMainWindow()
    win.show()
    sys.exit(app.exec_())
