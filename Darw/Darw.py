import os
import time
import sys

FileName = os.path.basename(sys.argv[0])
FilePath = sys.argv[0].replace(FileName,"")
UiName = FileName.replace(".py",".ui")
UiPath = FilePath +UiName
Ui_pyName = FilePath+"ui.py"
FileFlag = os.path.isfile(Ui_pyName)

if FileFlag == 0:
	sys_cmd	 = os.popen("pyuic5 "+UiPath+" -o "+Ui_pyName)
	time.sleep(1)

from ui import Ui_Form
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *



class m_window(QWidget,Ui_Form,QPainter):
	def __init__(self):
		super(m_window,self).__init__()
		self.setupUi(self)
		self.pushButton.clicked.connect(self.DrawPoint)
		self.pushButton_2.clicked.connect(self.DrawLine)
		self.pushButton_3.clicked.connect(self.DrawElipse)
		self.pushButton_4.clicked.connect(self.DrawRectangle)
		self.pushButton_5.clicked.connect(self.DrawText)
		self.pushButton_6.clicked.connect(self.DrawPolygon)
		self.pushButton_7.clicked.connect(self.DrawPie)
		self.pushButton_8.clicked.connect(self.DrawArc)
		self.pushButton_9.clicked.connect(self.DrawPath)
		self.Draw = ""
		self.Line_list = [0,0,0,0]
		self.Point_list = []
		self.Elipse_list = [0,0,0,0]
		self.Rectangle_list = [0,0,0,0]
		self.Polygon_list = []
		self.Pie_list = [0,0,0,0]
		self.Arc_list = [0,0,0,0]

	def DrawLine(self):
		self.update()
		self.Draw = "Line"		

	def DrawPoint(self):
		self.update()
		self.Draw = "Point"

	def DrawElipse(self):
		self.update()
		self.Draw = "Elipse"

	def DrawRectangle(self):
		self.update()
		self.Draw = "Rectangle"
	
	def DrawText(self):
		self.update()
		self.Draw = "Text"

	def DrawPolygon(self):
		self.update()
		self.Draw = "Polygon"

	def DrawArc(self):
		self.update()
		self.Draw = "Arc"

	def DrawPie(self):
		self.update()
		self.Draw = "Pie"

	def DrawPath(self):
		self.update()
		self.Draw = "Path"

	def paintEvent(self, QPaintEvent):
			painter = QPainter(self)
			painter.setPen(QColor(166,66,250))			
			painter.begin(self)	
			if self.Draw == "Line":			
				painter.drawLine(self.Line_list[0],self.Line_list[1],self.Line_list[2],self.Line_list[3])
				print("DrawLine")
			elif self.Draw == "Point":
				len_point_list = len(self.Point_list)/2
				for i  in range(int(len_point_list)):
					painter.drawPoint(self.Point_list[i*2],self.Point_list[i*2+1])
				print("DrawPoint")
			elif self.Draw == "Elipse":
				painter.drawEllipse(self.Elipse_list[0],self.Elipse_list[1],self.Elipse_list[2],self.Elipse_list[3])
				print("DrawElipse")
			elif self.Draw == "Rectangle":
				painter.drawRect(self.Rectangle_list[0],self.Rectangle_list[1],self.Rectangle_list[2],self.Rectangle_list[3])
				print("DrawRectangle")
			elif self.Draw == "Text":
				painter.drawText(120,120,"文字")
				print("DrawText")
			elif self.Draw == "Polygon":
				polygon = QPolygon()
				if len(self.Polygon_list) >= 6:
					polygon.setPoints(self.Polygon_list)
					print(len(self.Polygon_list))
					painter.drawPolygon(polygon)
				print("DrawPolygon")
			elif self.Draw == "Pie":
				painter.drawPie(self.Pie_list[0],self.Pie_list[1],self.Pie_list[2],self.Pie_list[3],0*16,120*16)
				print("DrawPie")
			elif self.Draw =="Arc":
				painter.drawArc(self.Arc_list[0],self.Arc_list[1],self.Arc_list[2],self.Arc_list[3],30*16,120*16)
				print("DrawArc")
			elif self.Draw == "Path":
				path = QPainterPath()
				path.addRect(100,100,100,100)
				path.addEllipse(150,150,60,80)
				painter.setBrush(Qt.blue)
				#path.setFillRule(Qt.WindingFill)
				path.setFillRule(Qt.OddEvenFill) 
				painter.drawPath(path)
				print("DrawPath")
			painter.end()

	def mousePressEvent(self, e):
		if self.Draw == "Line" :
			self.Line_list[0] = e.x()
			self.Line_list[1] = e.y()
			print("start",self.Line_list[0],self.Line_list[1])
		elif self.Draw =="Point":
			self.Point_list.append(e.x())
			self.Point_list.append(e.y())
			self.update()
		elif self.Draw == "Elipse":
			self.Elipse_list[0]=e.x()
			self.Elipse_list[1]=e.y()
		elif self.Draw == "Rectangle":
			self.Rectangle_list[0] = e.x()
			self.Rectangle_list[1] = e.y()
		elif self.Draw == "Polygon":
			self.Polygon_list.append(e.x())
			self.Polygon_list.append(e.y())
			print(self.Polygon_list)
			self.update()
		elif self.Draw == "Pie":
			self.Pie_list[0] = e.x()
			self.Pie_list[1] = e.y()
		elif self.Draw == "Arc":
			self.Arc_list[0] = e.x()
			self.Arc_list[1] = e.y()

		if e.button() == Qt.RightButton:
			self.Point_list.clear()
			self.Elipse_list = [0,0,0,0]
			self.Rectangle_list = [0,0,0,0]
			self.Polygon_list.clear()
			self.Pie_list = [0,0,0,0]
			self.Arc_list = [0,0,0,0]
			self.update()

	def mouseReleaseEvent(self, e):	
		if e.button() == Qt.LeftButton:
			print("左键")
		elif e.button() == Qt.RightButton:
			print("右键")
		elif e.button() == Qt.MidButton:
			print("点击滚轮")

	def mouseMoveEvent(self, e):
		if self.Draw == "Line" :
			self.Line_list[2] = e.x()
			self.Line_list[3] = e.y()
			print("end",self.Line_list[2],self.Line_list[3])
			self.update()
		elif self.Draw == "Elipse":
			self.Elipse_list[2] = e.x()-self.Elipse_list[0]
			self.Elipse_list[3] = e.y()-self.Elipse_list[1]
			self.update()
			print("Radius",self.Elipse_list[2],self.Elipse_list[3])
		elif self.Draw == "Rectangle":
			self.Rectangle_list[2] = e.x()-self.Rectangle_list[0]
			self.Rectangle_list[3] = e.y()-self.Rectangle_list[1]
			self.update()
		elif self.Draw == "Pie":
			self.Pie_list[2] = e.x() - self.Pie_list[0]
			self.Pie_list[3] = e.y() - self.Pie_list[1]
			self.update()
		elif self.Draw == "Arc":
			self.Arc_list[2] = e.x() - self.Arc_list[0]
			self.Arc_list[3] = e.y() - self.Arc_list[1]
			self.update()

							

app = QApplication(sys.argv)
window = m_window();
window.show()
sys.exit(app.exec_())