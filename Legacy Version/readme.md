This is a leaning log of python

基于面阵雷达

# 基础

## 串口读取、解包Json数据

testserial.py

serialunpack.py

## 使用QT designer 创建界面(该文件非最终版)

serialshow.py

##  界面业务逻辑

testqt.py

qtserial.py

**test230324.py** 串口滚动显示
主线程QT串口显示
Qthread线程串口读取

# 绘图方式的讨论

### QT

### OPENGL

**testopengl.py** 
主线程：UI显示
QT线程 串口读取、三维绘图 

testopenglcolor.py 解决点色彩问题

### OPEN3D

不兼容于QT组件中，只能单独显示

界面卡顿

**testopen3d.py** 可以显示3维坐标界面，但不能嵌入QT组件中
主线程：UI显示
QT线程 串口读取、三维绘图 

testopen3d2.py 绘制特定已知点



# 多线程方案的讨论

基于不同包的多线程方案 ：QThread   threading

testopenglsigTr.py 测试单线程效率效果
testopenglpool.py 尝试线程池

存在的的问题

testopengltr.py 试图不用qtread,因为据说qtread 没有真正起到线程的作用  但是没成功 多父类继承问题
**testopengltr2.py** 怀疑非run下的不在线程里

**testopengltr2-copy.py** 适配系统Ⅲ

> work.trigger

testopen3dserial.py 多进程

# 运算优化方案

## 多线程

## 使用矩阵进行运算（解决运算太慢的问题）

serialunpackNumpy.py 终端显示版本

**testopenglarraycope.py**
主线程：UI显示
QT线程 串口读取、三维绘图 

## 更换绘图方案

## 读写数据方案 使用pcd文件

读取数据写入文件

testpcd.py

因为没有做出定时读取而失败（Timer）



示例及测试文件：

EXopen3dgui.py
EXqttest.py
EXserialplot.py
EXserialui.py
EXtestplot.py
EXtestselplot.py

testarray.py

