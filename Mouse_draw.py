# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPolygon, QPainterPath


def mousePressEvent(self, e):
    print("鼠标按下事件")

def mouseReleaseEvent(self, e):
    print("鼠标释放事件")
    if e.button() == QtCore.Qt.LeftButton:
        print("左键")
    elif e.button() == QtCore.Qt.RightButton:
        print("右键")
    elif e.button() == QtCore.Qt.MidButton:
        print("点击滚轮")

def mouseMoveEvent(self, e):
    print("鼠标移动事件")

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
