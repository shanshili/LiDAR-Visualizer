'''
尝试使用矩阵处理
'''

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import pyqtgraph.opengl as gl
import serial
from serial.tools import list_ports
import math
import sys
import numpy
import numpy.matlib 

datanum = 0
anglenum = 0
angle = numpy.matlib.zeros((3,300000)) #X Y Z
point = numpy.matlib.zeros((3,64)) # n dis stren
x = [1,2,3,4,5,6,7,8,1,2,3,4,5,6,7,8,1,2,3,4,5,6,7,8,1,2,3,4,5,6,7,8,1,2,3,4,5,6,7,8,1,2,3,4,5,6,7,8,1,2,3,4,5,6,7,8,1,2,3,4,5,6,7,8,]
basecol = numpy.asarray(x)
baserow = numpy.asarray(x)
onem = numpy.ones((1,64))
eightm = onem*8

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
        pointunpack = Copedata(str)
        self.plotT.plotpoint(pointunpack)

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
            
class PlotThread(QThread):
    def __int__(self):
        # 初始化函数
        super().__init__()
        self.weightInit(self)

    def weightInit(self):
        self.opengl_weight = gl.GLViewWidget()
        self.opengl_weight.opts['distance'] = 1500
        self.opengl_weight.setWindowTitle('pyqtgraph example: GLScatterPlotItem')
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

    def plotpoint(self,pointunpack):
        # data = eval(str) #json to dic 
        # #print(data)
        # pointunpack = Copedata(data)
        #print(pointunpack)
        if pointunpack != None:
            n = 0   
            #print(pointunpack['x'])
            while n < 64:
                #print(n,'=',pointunpack['x'][0,n])
                self.sp2 = gl.GLScatterPlotItem(pos=(pointunpack['x'][0,n],pointunpack['y'][0,n],pointunpack['z'][0,n]), 
                                                color=(1/float(pointunpack['x'][0,n]), 1/float(pointunpack['y'][0,n]), 1/float(pointunpack['z'][0,n]),1), size=5)  # 不带有任何颜色的白点
                self.opengl_weight.addItem(self.sp2)  
                n += 1

def sph2rec(dis,anglerow, anglecol):
    r = 35
    xx =  r * numpy.multiply(numpy.cos(anglecol-onem*math.pi/4),numpy.cos(anglerow-onem*math.pi/2))
    yy = r * numpy.multiply(numpy.cos(anglecol-onem*math.pi/4) ,numpy.sin(anglerow-onem*math.pi/2))
    zz = r* numpy.sin(anglecol-onem*math.pi/4)
    xb = numpy.multiply(dis,numpy.multiply(numpy.cos(anglecol) ,numpy.cos(anglerow)))
    yb = numpy.multiply(dis,numpy.multiply(numpy.cos(anglecol) ,numpy.sin(anglerow)))
    zb = numpy.multiply(dis,numpy.sin(anglecol))
    x = xb - xx
    y = yb - yy
    z = zb - zz
    #print("sph2rec",x,y,z)
    point = {'x':x.A,'y':y.A,'z':z.A}
    return point

def Unpack(data):
    global angle,point,datanum,anglenum,basecol,baserow,onem,eightm
    if('X' in data):    
        angle[0,anglenum] = data['X']
        angle[1,anglenum] = data['Y']
        angle[2,anglenum] = data['Z']    
        datanum = 0
        anglenum += 1
    elif('n' in data):
        datanum += 1
        point[0,data['n']-1] = data['n']
        point[1,data['n']-1]= data['d']
        point[2,data['n']-1]= data['s']
    if((numpy.all(point==0)!=True)and(datanum==0)):  #所有点不为空,且计数结束
        anglecol = ((onem*4)-baserow)*5.625 + angle[0,anglenum-1]
        anglerow = ((onem*4)-basecol)*5.625 + angle[2,anglenum-1]
        #print(point[1],anglecol,anglerow)
        pointsph = sph2rec(point[1],anglerow/360*2*math.pi,anglecol/360*2*math.pi)
        return pointsph
    else:
        return None
    
def Copedata(jsondata):
    pointdic = eval(jsondata)
    unpack = Unpack(pointdic)
    return unpack
    
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    x = MyWindow()
    x.ui.show()
    app.exec()