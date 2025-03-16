"""
X Y Z float
n d s int
"""

import serial
from serial.tools import list_ports
import math

datanum = 0
anglenum = 0
angle = [0.0,0.0,0.0] #X Y Z
point = [0,0,0] # n dis stren
basecol = 0
baserow = 0

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
    point = {'x':x,'y':y,'z':z}
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
        return pointsph
         


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
            data = eval(jsondata) #json to dic 
            #print(data)
            pointunpack = Unpack(data)
            print(pointunpack)
