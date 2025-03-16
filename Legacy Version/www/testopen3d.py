"""
可以显示3维坐标界面，但不能嵌入QT组件中
"""
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import open3d
import serial
from serial.tools import list_ports
import math
import sys
import numpy
import numpy.matlib 

datanum = 0
anglenum = 0
angle = numpy.matlib.zeros((3,64)) #X Y Z
point = numpy.matlib.zeros((3,64)) # n dis stren
basecol = 0
baserow = 0

class MyWindow(QWidget):
    _translate = QCoreApplication.translate
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.work = SerialThread()
        self.plotT = PlotThread()
        self.plotT.start()
        self.plotT.weightInit()
        self.WaveDisplay.addWidget(self.plotT.vis) ？？？
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
            
class PlotThread(QThread):   
    def __int__(self):
        # 初始化函数
        super().__init__()
        self.weightInit(self)

    def weightInit(self):
        # 绘制open3d坐标系
        axis_pcd = open3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1, origin=[0, 0, 0])
        test_pcd = open3d.geometry.PointCloud()  # 定义点            
        self.vis = open3d.visualization.Visualizer()
        self.vis.create_window(window_name="Open3D1")
        self.vis.get_render_option().point_size = 3
        self.vis.add_geometry(axis_pcd)
        self.vis.add_geometry(test_pcd)
 

    def run(self):
        print ("绘图线程")

    def plotpoint(self,str):
        data = eval(str) #json to dic 
        #print(data)
        pointunpack = Unpack(data)
        # print(pointunpack)
        if pointunpack != None:
            self.sp2 = gl.GLScatterPlotItem(pos=(pointunpack['x'],pointunpack['y'],pointunpack['z']), 
                                            color=(1/float(pointunpack['x']), 1/float(pointunpack['y']), 1/float(pointunpack['z']),1), size=5)  # 不带有任何颜色的白点
            self.opengl_weight.addItem(self.sp2)  

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
        pointsph = sph2rec(point[1],anglerow/360*2*math.pi,anglecol/360*2*math.pi)
        #print(pointsph)
        return pointsph
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    x = MyWindow()
    x.ui.show()
    app.exec()