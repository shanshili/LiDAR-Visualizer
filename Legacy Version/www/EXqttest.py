"""
面向对象编程 class self super
"""
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class window(QWidget):
   def __init__(self, parent = None):
      super(window, self).__init__(parent)
      self.resize(200,50)
      self.setWindowTitle("PyQt5")
      self.label = QLabel(self)#提供文本或图像显示
      self.label.setText("Hello World")
      font = QFont()
      font.setFamily("Arial")
      font.setPointSize(16)
      self.label.setFont(font)
      self.label.move(50,20)
def main():
   app = QApplication(sys.argv)# 实例化一个应用对象；sys.argv是一组命令行参数的列表。Python可以在shell里运行，这个参数提供对脚本控制的功能。
   ex = window()
   ex.show()# 让控件在桌面上显示出来。控件在内存里创建，之后才能在显示器上显示出来。
   sys.exit(app.exec_())# 确保主循环安全退出
if __name__ == '__main__':
   main()