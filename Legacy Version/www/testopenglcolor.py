"""
主线程、串口线程，GUI线程,点计算线程池
解决点色彩问题，使用opengl，还是没用上
"""

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtOpenGL import QGLWidget
import pyqtgraph.opengl as gl
from OpenGL import GL 
import serial
from serial.tools import list_ports
import math
import sys
from concurrent.futures import ThreadPoolExecutor

datanum = 0
anglenum = 0
angle = [0.0,0.0,0.0] #X Y Z
point = [0,0,0] # n dis stren
basecol = 0
baserow = 0
pointunpack = {}

class MyWindow(QWidget):
    _translate = QCoreApplication.translate
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.work = SerialThread()
        self.plotT = PlotThread()
        self.plotT.start()
        self.plotT.weightInit()
        self.WaveDisplay.addWidget(self.plotT.opengl_weight)
        self.ScanComPort()
        self.SelectComPort()

        #self.ScanPort.clicked.connect(self.ScanComPort)
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
        self.work.mSerial.port = self.comPort.currentText()
        self.work.mSerial.baudrate = int(self.comBaud.currentText())
        if self.work.mSerial.isOpen():
            QMessageBox.warning(self, "警告", "串口已打开", QMessageBox.Cancel, QMessageBox.Cancel)
        else:
            try:
                self.Open.setEnabled(False)#按钮失效
                self.work.mSerial.open()        #打开串口
                self.label.setText("已连接")
                self.work.mSerial.flushInput()
                self.work.mSerial.flushOutput()
                self.work.start()          #启动线程
                self.work.trigger.connect(self.displaySerial) #信号绑定到槽
                #self.mTimer.start(1)       #间隔1ms         
            except:
                QMessageBox.critical(self, "警告", "串口打开失败！", QMessageBox.Cancel, QMessageBox.Cancel)
                self.Open.setEnabled(True)
        print(self.work.mSerial)
        pass

    def CloseComPort(self):
        # self.mTimer.stop()
        if self.work.mSerial.isOpen():
            self.Open.setEnabled(True)
            self.work.mSerial.flushInput()
            self.work.mSerial.flushOutput()
            self.work.mSerial.close()
            self.label.setText("已断开连接")
            self.work.terminate()
        pass

class SerialThread(QThread):
    trigger = pyqtSignal(str)
    mSerial = serial.Serial()
    # 自定义信号对象。参数str就代表这个信号可以传一个字符串
    def __int__(self):
        # 初始化函数
        super().__init__()

    def run(self):
        #重写线程执行的run函数
        #触发自定义信号
        # 通过自定义信号把待显示的字符串传递给槽函数
        print ("启动线程")
        while True:
            jsondata = self.mSerial.readline().decode()
            #print(jsondata)
            self.trigger.emit(jsondata)
            # data = eval(jsondata) #json to dic 
            # #print(data)
            # pointunpack = Unpack(data)
            
class PlotThread(QThread,QGLWidget):   
    def __int__(self):
        # 初始化函数
        super(QThread,self).__init__()
        super(QGLWidget,self).__init__()???####没用上啊  
        self.weightInit(self)

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

    def run(self):
        print ("绘图线程")


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
    app = QApplication(sys.argv)
    x = MyWindow()
    x.ui.show()
    app.exec()
    pool.shutdown()