"""
X Y Z float
n d s int
"""

import serial
from serial.tools import list_ports
import math
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


def sph2rec(dis,anglerow, anglecol):
    r = 35
    xx =  r * numpy.multiply(numpy.cos(anglecol-onem*math.pi/4),numpy.cos(anglerow-onem*math.pi/2))
    yy = r * numpy.multiply(numpy.cos(anglecol-onem*math.pi/4) ,numpy.sin(anglerow-onem*math.pi/2))
    zz = r* numpy.sin(anglecol-onem*math.pi/4)
    xb = numpy.multiply(dis.A,numpy.multiply(numpy.cos(anglecol) ,numpy.cos(anglerow)))
    yb = numpy.multiply(dis.A,numpy.multiply(numpy.cos(anglecol) ,numpy.sin(anglerow)))
    zb = numpy.multiply(dis.A,numpy.sin(anglecol))
    x = xb - xx
    y = yb - yy
    z = zb - zz
    #print("sph2rec",x,y,z)
    point = {'x':x,'y':y,'z':z}
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
        print(point[1],anglecol,anglerow)
        pointsph = sph2rec(point[1],anglerow/360*2*math.pi,anglecol/360*2*math.pi)
        return pointsph
    
def Copedata(jsondata):
    pointdic = eval(jsondata)
    unpack = Unpack(pointdic)
    return unpack

if __name__ == '__main__':
    # 获取端口列表，列表中为 ListPortInfo 对象
    port_list = list(list_ports.comports())
    num = len(port_list)
    if num <= 0:
        print("找不到任何串口设备")
    else:
        for i in range(num):
            # 将 ListPortInfo 对象转化为 list
            port = list(port_list[i])
            print(port)
        ser = serial.Serial("COM6", 115200)  # 连接到串口，波特率为 9600
        while True:
            jsondata = ser.readline().decode()  # 读取一行数据并解码
            pointunpack=Copedata(jsondata)
            #print(pointunpack)
