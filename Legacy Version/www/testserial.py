import serial
#from serial import tools
from serial.tools import list_ports
import json
import threading

jsondata = ""

# def Serial():
#     jsondata = ser.readline().decode()  # 读取一行数据并解码
# def Jsonload():
#     data = json.loads(jsondata)
#     print(jsondata)  # 打印读取到的数据

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
        ser = serial.Serial("COM5", 115200)  # 连接到串口，波特率为 9600
        while True:
            jsondata = ser.readline().decode()  # 读取一行数据并解码
            data = eval(jsondata)
            print(data)
            # th1 = threading.Thread(target=Serial)
            # th2 = threading.Thread(target=Jsonload)
            # th1.start()
            # th2.start()
        


