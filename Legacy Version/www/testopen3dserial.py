"""
串口接收成功，但界面卡死
"""
from multiprocessing import Process
import time
import open3d
import math
import numpy
import numpy.matlib 
import serial
from serial.tools import list_ports

datanum = 0
anglenum = 0
angle = [0.0,0.0,0.0] #X Y Z
point = [0,0,0] # n dis stren
basecol = 0
baserow = 0
pointunpack = numpy.asarray([0,0,0])

class MyThread(Process):
    global pointunpack 
    def __init__(self):
        super().__init__()
    def run(self):
        self.mSerial = serial.Serial("COM6", 115200)
        while True:
            jsondata = self.mSerial.readline().decode()
            #print(jsondata)
            pointunpack = eval(jsondata) #json to dic 
            print("th1:",pointunpack)
            #mutex.acquire()  # 上锁
            #mutex.release()  # 解锁
            

# class open3dclass:
#     def __init__(self):
#         super().__init__()  
class MyThreadplot(Process):
    global pointunpack 
    def __init__(self):
        super().__init__()
    def run(self):      
        # 绘制open3d坐标系
        self.axis_pcd = open3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1, origin=[0, 0, 0])  ？？？
        self.test_pcd = open3d.geometry.PointCloud()  # 定义点          
        self.vis = open3d.visualization.Visualizer()
        self.vis.create_window(window_name="Open3D1")
        self.vis.get_render_option().point_size = 3
        self.vis.add_geometry(self.axis_pcd)
        self.vis.add_geometry(self.test_pcd)
        self.vis.poll_events()
        self.vis.update_renderer()
        print("建立绘画线程")

        while True:
            #mutex.acquire()  # 上锁
            if numpy.all(pointunpack==0)!=True:
                data  =  Unpack(pointunpack)
                self.test_pcd.points = open3d.utility.Vector3dVector(data)  # 定义点云坐标位置
                self.test_pcd.colors = open3d.utility.Vector3dVector(data)  # 定义点云的颜色
                # update_renderer显示当前的数据
                self.vis.poll_events()
                self.vis.update_renderer()
            #mutex.release()  # 解锁


#mutex = threading.Lock()

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
    point = numpy.asarray([round(x,2),round(y,2),round(z,2)])
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
        print(pointsph)
        return pointsph
    
if __name__ == '__main__':
    # op3d = open3dclass()
    port_list = list(list_ports.comports())
    num = len(port_list)
    if num <= 0:
        print("找不到任何串口设备")
    else:
        for i in range(num):
            # 将 ListPortInfo 对象转化为 list
            port = list(port_list[i])
            print(port)
    t = MyThread()
    t2 = MyThreadplot()    
    t2.start()
    time.sleep(2)
    t.start()
    # t1 = threading.Thread(target=op3d.open3dinit)
    # t2 = threading.Thread(target=op3d.mserial)
    # t1.start()
    # t2.start()