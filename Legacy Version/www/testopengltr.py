"""
主线程、串口线程，GUI线程,点计算线程池
>试图不用qtread,因为据说qtread 没有真正起到线程的作用
>但是没成功 多父类继承问题
"""

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import pyqtgraph.opengl as gl
import serial
from serial.tools import list_ports
import math
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

datanum = 0
anglenum = 0
angle = [0.0,0.0,0.0] #X Y Z
point = [0,0,0] # n dis stren
basecol = 0
baserow = 0
pointunpack = {}
mSerial = serial.Serial()

class MyWindow(QWidget):
    _translate = QCoreApplication.translate
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.plotT = PlotThread()
        self.plotT.start()
        self.plotT.weightInit()
        self.WaveDisplay.addWidget(self.plotT.opengl_weight)
        self.ScanComPort()
        self.SelectComPort()

        self.Open.clicked.connect(self.OpenComPort)
        self.Close.clicked.connect(self.CloseComPort)
        self.comPort.currentIndexChanged.connect(self.SelectComPort)

    def init_ui(self):
        self.ui = uic.loadUi('F:/Tech/qtdesigner/serialshow.ui')
        
        self.ScanPort = self.ui.ScanPort
        self.Open = self.ui.Open
        self.Close = self.ui.Close
        self.comPort = self.ui.comPort
        self.comBaud = self.ui.comBaud
        self.label = self.ui.label
        self.ReceiveDisplay = self.ui.ReceiveDisplay
        self.WaveDisplay = self.ui.WaveDisplay

    def displaySerial(self,str):
        # 由于自定义信号时自动传递一个字符串参数，所以在这个槽函数中要接受一个参数
        self.ReceiveDisplay.addItem(str)
        self.ReceiveDisplay.setCurrentRow(self.ReceiveDisplay.count() - 1)
        self.plotT.plotpoint(str)

    def ScanComPort(self):
        self.comPort.clear() #list.clear()
        self.portDict = {}
        portlist = list(list_ports.comports())
        for port in portlist:
            print(port)
            self.portDict["%s" % port[0]] = "%s" % port[1] 
            self.comPort.addItem(port[0]) #增加comBOX项目
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
        global mSerial
        mSerial.port = self.comPort.currentText()
        mSerial.baudrate = int(self.comBaud.currentText())
        if mSerial.isOpen():
            QMessageBox.warning(self, "警告", "串口已打开", QMessageBox.Cancel, QMessageBox.Cancel)
        else:
            try:
                self.Open.setEnabled(False)#按钮失效
                mSerial.open()        #打开串口
                self.label.setText("已连接")
                mSerial.flushInput()
                mSerial.flushOutput()
                receive = pool.submit(SerialThread).result()  ############       #启动线程
                self.displaySerial(receive) #信号绑定到槽
            except:
                QMessageBox.critical(self, "警告", "串口打开失败！", QMessageBox.Cancel, QMessageBox.Cancel)
                self.Open.setEnabled(True)
        print(mSerial)
        pass

    def CloseComPort(self):
        # self.mTimer.stop()
        if mSerial.isOpen():
            self.Open.setEnabled(True)
            mSerial.flushInput()
            mSerial.flushOutput()
            mSerial.close()
            self.label.setText("已断开连接")
        pass

def SerialThread():
    print ("串口线程")
    jsondata = mSerial.readline().decode()
    return jsondata ???

class PlotThread(QThread): 
    def __int__(self):
        # 初始化函数
        super().__init__()

    def weightInit(self):
        self.opengl_weight = gl.GLViewWidget()
        self.opengl_weight.opts['distance'] = 1500
        self.opengl_weight.setBackgroundColor('k')
        gl_glgrideitem = gl.GLGridItem()  # 添加网格
        gl_glgrideitem.setSize(x=2000,y=2000,z=2000)
        gl_glgrideitem.setSpacing(x=50,y=50,z=50)
        gl_glgrideitem.setColor('b')
        self.opengl_weight.addItem(gl_glgrideitem)
        gl_axis = gl.GLAxisItem()   # 添加xyz坐标轴
        gl_axis.setSize(x=1200,y=1200,z=1200)
        self.opengl_weight.addItem(gl_axis)   

    def plotpoint(self,str):
        global pointunpack
        data = eval(str) #json to dic 
        #print(data)
        pointunpack = pool.submit(Unpack,data).result()
        # print(pointunpack)
        if pointunpack != None:
            self.sp2 = gl.GLScatterPlotItem(pos=(pointunpack['x'],pointunpack['y'],pointunpack['z']), 
                                             color=self.Colorplette(pointunpack), size=5)  # 不带有任何颜色的白点
            self.opengl_weight.addItem(self.sp2)
    
    def Colorplette(self,pointunpack):
        x = abs(pointunpack['z']//1000)/2
        y = abs(pointunpack['z']//100)/2
        z = abs(pointunpack['z']//10)/2
        #print([x,y,z,1])
        return [x,y,z,1]

def sph2rec(dis,anglerow, anglecol):
    r = 35
    xx =  r * math.cos(anglecol-math.pi/4) * math.cos(anglerow-math.pi/2)
    yy = r * math.cos(anglecol-math.pi/4) * math.sin(anglerow-math.pi/2)
    zz = r* math.sin(anglecol-math.pi/4)
    xb = dis * math.cos(anglecol) * math.cos(anglerow)
    yb = dis * math.cos(anglecol) * math.sin(anglerow)
    zb = dis* math.sin(anglecol)
    x = xb - xx
    y = yb - yy
    z = zb - zz
    #print("sph2rec",x,y,z)
    point = {'x':round(x,2),'y':round(y,2),'z':round(z,2)}
    #print("sph2re",point)
    return point

def Unpack(data):
    global angle,point,datanum,anglenum,basecol,baserow
    if('X' in data):    
        angle[0] = data['X']
        angle[1] = data['Y']
        angle[2] = data['Z']    
        datanum = 0
        anglenum += 1
    elif('n' in data):
        datanum += 1
        point[0] = data['n']
        point[1] = data['d']
        point[2] = data['s']
        if point[0]%8 != 0:
            basecol = point[0]%8+1
        else:
            basecol = 8
        baserow = point[0]//8+1
        anglecol = (4-baserow)*5.625 + angle[0]
        anglerow = (4-basecol)*5.625 + angle[2]
        #print(point[1],anglecol,anglerow)
        pointsph = pool.submit(sph2rec,point[1],anglerow/360*2*math.pi,anglecol/360*2*math.pi)
        #print("unpack:",pointsph.result())
        return pointsph.result()
    
# 创建一个包含2条线程的线程池
pool = ThreadPoolExecutor(max_workers=2)    

if __name__ == '__main__':
    # 向线程池提交一个task, 50会作为action()函数的参数
    app = QApplication(sys.argv)
    x = MyWindow()
    x.ui.show()
    app.exec()
    pool.shutdown()