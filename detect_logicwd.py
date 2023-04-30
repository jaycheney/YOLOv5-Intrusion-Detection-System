# -*- coding: utf-8 -*-
# @Modified by: Ying CHEN
# @ProjectName:yolov5-pyqt5

import sys
import time
import argparse
import random
import torch
import torch.backends.cudnn as cudnn
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


# YOLOv5部分
from utils.torch_utils import select_device
from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression, scale_coords
from utils.datasets import letterbox
from utils.plots import plot_one_box2

# QT界面部分
from ui.detect_ui_new_v2 import Ui_MainWindow  # 导入detect_ui的界面

import json

#   区域入侵的工具脚本，需要
from line_draw import *

# 用于保存上传视频或者图片的resize前后 分辨率比例，这个应该是需要的
o_n_x_scale = 1
o_n_y_scale = 1


# 这个变量是QT中判断是否开启区域入侵功能的，和组件绑定
runqin_check_for_draw = False


class UI_Logic_Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(UI_Logic_Window, self).__init__(parent)
        self.timer_video = QtCore.QTimer()  # 创建定时器

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.checkBox.setChecked(False)
        self.init_slots()

        self.cap = cv2.VideoCapture()
        self.num_stop = 1  # 暂停与播放辅助信号，note：通过奇偶来控制暂停与播放
        self.output_folder = 'output/'
        self.vid_writer = None

        self.draw_area = 0
        self.ruqin_check = False
        self.opt = ''

        self.model_path ="best.pt"

        # json文件路径
        self.openfile_area = ''

        # 权重初始文件名
        self.openfile_name_model = None

        # 区域入侵绘制多边形区域
        # 另外一种写法：如标注文件那样实现，获取某点的像素坐标再进行连线
        self.ui.pushButton.clicked.connect(self.DrawPolygon)
        self.Draw = ""
        self.Polygon_list = []

    # 控件绑定相关操作
    def init_slots(self):
        self.ui.pushButton_2.clicked.connect(self.botton_area_open)
        self.ui.checkBox.stateChanged.connect(self.ruqin_flag)

        self.ui.pushButton_img.clicked.connect(self.button_image_open)
        self.ui.pushButton_video.clicked.connect(self.button_video_open)
        self.ui.pushButton_camer.clicked.connect(self.button_camera_open)

        self.define_model()

        self.define_video()



        self.ui.pushButton_init.clicked.connect(self.model_init)
        self.ui.pushButton_stop.clicked.connect(self.button_video_stop)
        self.ui.pushButton_finish.clicked.connect(self.finish_detect)

        self.timer_video.timeout.connect(self.show_video_frame)  # 定时器超时，将槽绑定至show_video_frame

    # 获取到一开始定义的是否开启区域入侵的变量，与QT里的勾选框有关
    def ruqin_flag(self):
        global runqin_check_for_draw

        self.ruqin_check = self.ui.checkBox.isChecked()
        runqin_check_for_draw = self.ruqin_check

    # 打开json文件来获取到选择的区域，这个逻辑可以转移到web端，这里用的是QT的函数来实现文件打开读取
    def botton_area_open(self):
        self.openfile_area, _ = QFileDialog.getOpenFileName(self.ui.pushButton_2, '上传区域入侵json文件',
                                                            'ruqin/')
        if not self.openfile_area:
            QtWidgets.QMessageBox.warning(self, u"警告", u"打开区域入侵json文件失败", buttons=QtWidgets.QMessageBox.Ok,
                                          defaultButton=QtWidgets.QMessageBox.Ok)
        else:
            print('区域入侵json文件地址为：' + str(self.openfile_area))
            self.draw_area = 1  # 载入json中的区域后置为1


    # 读取QT中的下拉框选择的模型权重参数，并拼接成正确的路径便于系统读取
    def define_model(self):
        select_value = self.ui.comboBox.currentText()
        root = os.getcwd()
        file_root = os.path.join(root, 'weights')
        if select_value != '请选择模型':
            self.openfile_name_model = file_root + select_value

    # 与上一个函数配合使用，加载模型权重文件
    def open_model(self):
        self.openfile_name_model, _ = QFileDialog.getOpenFileName(self.ui.pushButton_weights, '选择weights文件',
                                                                  'weights/')
        if not self.openfile_name_model:
            QtWidgets.QMessageBox.warning(self, u"警告", u"打开权重失败", buttons=QtWidgets.QMessageBox.Ok,
                                          defaultButton=QtWidgets.QMessageBox.Ok)
        else:
            print('加载weights文件地址为：' + str(self.openfile_name_model))

    # 加载相关参数，并初始化模型
    def model_init(self):
        # 模型相关参数配置
        self.model_path = self.get_model_path()
        # self.model_path = "weights/best.pt"
        print("这是当前的模型路径 ",self.model_path)
        parser = argparse.ArgumentParser()
        parser.add_argument('--weights', nargs='+', type=str, default=self.model_path, help='model.pt path(s)')
        parser.add_argument('--source', type=str, default='data/images', help='source')  # file/folder, 0 for webcam

        parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
        parser.add_argument('--conf-thres', type=float, default=0.25, help='object confidence threshold')
        parser.add_argument('--iou-thres', type=float, default=0.45, help='IOU threshold for NMS')
        parser.add_argument('--device', default='cpu', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
        parser.add_argument('--view-img', action='store_true', help='display results')
        parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
        parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
        parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
        parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
        parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
        parser.add_argument('--augment', action='store_true', help='augmented inference')
        parser.add_argument('--update', action='store_true', help='update all models')
        parser.add_argument('--project', default='runs/detect', help='save results to project/name')
        parser.add_argument('--name', default='exp', help='save results to project/name')
        parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
        self.opt = parser.parse_args()
        print('查看YOLO V5参数 ', self.opt)
        # 默认使用opt中的设置（权重等）来对模型进行初始化
        source, weights, view_img, save_txt, imgsz = self.opt.source, self.opt.weights, self.opt.view_img, self.opt.save_txt, self.opt.img_size

        # 若openfile_name_model不为空，则使用此权重进行初始化
        if self.openfile_name_model:
            weights = self.openfile_name_model
            print("Using button choose model")

        self.device = select_device(self.opt.device)
        self.half = self.device.type != 'cpu'  # half precision only supported on CUDA

        cudnn.benchmark = True

        # Load model
        self.model = attempt_load(weights, map_location=self.device)  # load FP32 model
        stride = int(self.model.stride.max())  # model stride
        self.imgsz = check_img_size(imgsz, s=stride)  # check img_size
        if self.half:
            self.model.half()  # to FP16

        # Get names and colors
        self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in self.names]
        print("model initial done")
        # 设置提示框
        QtWidgets.QMessageBox.information(self, u"消息", u"模型加载完成", buttons=QtWidgets.QMessageBox.Ok,
                                          defaultButton=QtWidgets.QMessageBox.Ok)


    # 加载直播路径，也是用的QT的组件下拉框来获取
    def define_video(self):
        dict = {'钢筋加工厂':"http://hls01open.ys7.com/openlive/e5515428d3fc42***.hd.m3u8",
                "主墩":"http://hls01open.ys7.com/openlive/82a225609bd74bb9a88***.hd.m3u8",
                "桥球机":"http://hls01open.ys7.com/openlive/5bf79ffa81bc412a9***.hd.m3u8",
                "特大桥":"http://hls01open.ys7.com/openlive/f960100902e647318***.hd.m3u8",
                "请选择视频":"0"}
        select_value = self.ui.comboBox_2.currentText()
        result = dict[select_value]
        return result



    def get_model_path(self):

        model_path = "weights/" + self.ui.comboBox.currentText() +".pt"
        return model_path

    # 目标检测
    def detect(self, name_list, img, area_poly=None):
        '''
        :param name_list: 文件名列表
        :param img: 待检测图片
        :return: info_show:检测输出的文字信息
        '''
        showimg = img
        pt_in_dangerous_area = 0
        info_show = ""
        # 判断是否勾选了入侵功能，是否有相关的区域（涉及到QT的相关勾选框组件，ruqin_check和draw_label都是）
        if self.ruqin_check and len(self.draw_label.Polygon_origin2canvas_list) != 0:
            # self.draw_area = 0

            draw_detect_area_poly = np.array(self.draw_label.Polygon_origin2canvas_list, np.int32)
        # 这个函数是line_draw脚本里的工具函数，与QT无关
            draw_poly_area_dangerous(showimg, draw_detect_area_poly, False)
        elif self.ruqin_check and self.draw_area:
            draw_poly_area_dangerous(showimg, self.openfile_area)  # 画上危险区域框
            # 危险区域的画法需要判断

        with torch.no_grad():
            if self.opt == '':
                QtWidgets.QMessageBox.warning(self, u"警告", u"请先加载模型", buttons=QtWidgets.QMessageBox.Ok,
                                              defaultButton=QtWidgets.QMessageBox.Ok)

            else:
                img = letterbox(img, new_shape=self.opt.img_size)[0]
                # Convert
                img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
                img = np.ascontiguousarray(img)
                img = torch.from_numpy(img).to(self.device)
                img = img.half() if self.half else img.float()  # uint8 to fp16/32
                img /= 255.0  # 0 - 255 to 0.0 - 1.0
                if img.ndimension() == 3:
                    img = img.unsqueeze(0)
                # Inference
                pred = self.model(img, augment=self.opt.augment)[0]
                # Apply NMS
                pred = non_max_suppression(pred, self.opt.conf_thres, self.opt.iou_thres, classes=self.opt.classes,
                                           agnostic=self.opt.agnostic_nms)

                # Process detections
                for i, det in enumerate(pred):
                    if det is not None and len(det):
                        # Rescale boxes from img_size to im0 size
                        det[:, :4] = scale_coords(img.shape[2:], det[:, :4], showimg.shape).round()
                        for *xyxy, conf, cls in reversed(det):
                            label = '%s %.2f' % (self.names[int(cls)], conf)
                            name_list.append(self.names[int(cls)])
                            # 判断是否在危险区域内
                            if self.ruqin_check and len(self.draw_label.Polygon_draw_list) != 0:
                                draw_area_poly = self.draw_label.Polygon_origin2canvas_list
                                # 这个工具函数也是line_draw里的函数
                                if person_in_poly_area_dangerous(xyxy, draw_area_poly) == True:
                                    # 返回 1 表明是在危险区域，框住人
                                    single_info = plot_one_box2(xyxy, showimg, label=label, color=self.colors[int(cls)],
                                                                line_thickness=2)

                                    class_info = single_info.split(":")[2]
                                    # if(class_info.__contains__("person")):
                                    #     # 统计此时区域内的人数
                                    #     pt_in_dangerous_area += 1
                                    #     ruqin_count = "此时非法入侵物体数：" + str(pt_in_dangerous_area) + "\n"
                                    #     old_infos = info_show.split("\n")
                                    #     position_info_list = old_infos[1:len(old_infos)]
                                    #     position_info = "\n".join(position_info_list)
                                    #     info_show = ruqin_count + position_info + "\n" + single_info
                                    # 统计此时区域内的人数
                                    pt_in_dangerous_area += 1
                                    ruqin_count = "此时非法入侵物体数：" + str(pt_in_dangerous_area) + "\n"
                                    old_infos = info_show.split("\n")
                                    position_info_list = old_infos[1:len(old_infos)]
                                    position_info = "\n".join(position_info_list)
                                    info_show = ruqin_count + position_info + "\n" + single_info



                            elif self.ruqin_check and self.draw_area:
                                if person_in_poly_area_dangerous(xyxy, area_poly) == True:

                                    # 返回 1 表明是在危险区域，框住人
                                    single_info = plot_one_box2(xyxy, showimg, label=label, color=self.colors[int(cls)],
                                                                line_thickness=2)
                                    # if (class_info.__contains__("person")):
                                    #     # 统计此时区域内的人数
                                    #     pt_in_dangerous_area += 1
                                    #     ruqin_count = "此时非法入侵人数：" + str(pt_in_dangerous_area) + "\n"
                                    #     old_infos = info_show.split("\n")
                                    #     position_info_list = old_infos[1:len(old_infos)]
                                    #     position_info = "\n".join(position_info_list)
                                    #     info_show = ruqin_count + position_info + "\n" + single_info
                                    # 统计此时区域内的人数
                                    pt_in_dangerous_area += 1
                                    ruqin_count = "此时非法入侵物体数：" + str(pt_in_dangerous_area) + "\n"
                                    old_infos = info_show.split("\n")
                                    position_info_list = old_infos[1:len(old_infos)]
                                    position_info = "\n".join(position_info_list)
                                    info_show = ruqin_count + position_info + "\n" + single_info
                            else:
                                single_info = plot_one_box2(xyxy, showimg, label=label, color=self.colors[int(cls)],
                                                            line_thickness=2)
                                # print(single_info)
                                info_show = info_show + single_info + "\n"
        return info_show

    # 打开图片并检测
    def button_image_open(self):
        if (self.opt != ''):
            print('button_image_open')
            # 先创建展示图片用的支持Painter的QLabel
            if self.ui.verticalLayout_5.count() > 0:
                for i in range(self.ui.verticalLayout_5.count()):
                    self.ui.verticalLayout_5.itemAt(i).widget().delete()

            # 这部分都是QT的鼠标绘制区域相关逻辑
            self.draw_label = MyLabel(self)
            # 没有点击“绘制区域”时不能使用画笔
            self.draw_label.setFlag(False)
            self.ui.verticalLayout_5.addWidget(self.draw_label)
            name_list = []


            # 打开加载图片文件
            try:
                img_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "打开图片", "data/images",
                                                                    "*.jpg;;*.png;;All Files(*)")
            except OSError as reason:
                print('文件打开出错啦！核对路径是否正确' + str(reason))
            else:
                # 判断图片是否为空
                if not img_name:
                    QtWidgets.QMessageBox.warning(self, u"警告", u"打开图片失败", buttons=QtWidgets.QMessageBox.Ok,
                                                  defaultButton=QtWidgets.QMessageBox.Ok)
                else:
                    img = cv2.imread(img_name)

                    print("img_name:", img_name)
                    if self.draw_area == 1:
                        area_poly = load_poly_area_data_simple(self.openfile_area)
                        info_show = self.detect(name_list, img, area_poly)
                    else:
                        info_show = self.detect(name_list, img)
                    print(info_show)
                    # 获取当前系统时间，作为img文件名
                    now = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
                    file_extension = img_name.split('.')[-1]
                    new_filename = now + '.' + file_extension  # 获得文件后缀名
                    file_path = self.output_folder + 'img_output/' + new_filename
                    cv2.imwrite(file_path, img)

                    # 检测信息显示在QT界面
                    self.ui.textBrowser.setText(info_show)

                    # 检测结果显示在界面
                    self.result = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
                    origin_size = img.shape

                    # 计算加载图片的原尺寸和resize到640*480的坐标比例，引用全局变量，这个是在QT界面中绘制区域需要用到的缩放比例
                    # 所有传入的视频都要经过分辨率的调整，调整前后画面大小不一样，如果没有这两个参数，鼠标在界面中绘制的多边形区域位置会发生偏移
                    global o_n_y_scale
                    global o_n_x_scale
                    o_n_x_scale = origin_size[1] / 640
                    o_n_y_scale = origin_size[0] / 480

                    self.result = cv2.resize(self.result, (640, 480), interpolation=cv2.INTER_AREA)
                    self.QtImg = QtGui.QImage(self.result.data, self.result.shape[1], self.result.shape[0],
                                              QtGui.QImage.Format_RGB32)
                    self.draw_label.setPixmap(QtGui.QPixmap.fromImage(self.QtImg))
                    self.draw_label.setScaledContents(True)  # 设置图像自适应界面大小

    def set_video_name_and_path(self):
        # 获取当前系统时间，作为img和video的文件名
        now = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
        # if vid_cap:  # video
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # 视频检测结果存储位置
        save_path = self.output_folder + 'video_output/' + now + '.mp4'
        return fps, w, h, save_path

    # 打开视频并检测
    def button_video_open(self):
        # 这部分也是QT的绘制界面
        if (self.opt != ''):
            flag = False
            if (self.ui.verticalLayout_5.count() > 0):
                for i in reversed(range(self.ui.verticalLayout_5.count())):
                    self.ui.verticalLayout_5.removeItem(self.ui.verticalLayout_5.itemAt(i))

            self.draw_label = MyLabel(self)
            self.draw_label.setFlag(flag)
            self.ui.verticalLayout_5.addWidget(self.draw_label)
            video_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "打开视频", "data/", "*.mp4;;*.avi;;All Files(*)")
            flag = self.cap.open(video_name)
            if not flag:
                QtWidgets.QMessageBox.warning(self, u"警告", u"打开视频失败", buttons=QtWidgets.QMessageBox.Ok,
                                              defaultButton=QtWidgets.QMessageBox.Ok)
            else:



                # -------------------------写入视频----------------------------------#
                fps, w, h, save_path = self.set_video_name_and_path()
                self.vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

                self.timer_video.start(30)  # 以30ms为间隔，启动或重启定时器



                # 进行视频识别时，关闭其他按键点击功能，与QT页面的按钮有关，和区域入侵功能无关
                self.ui.pushButton_video.setDisabled(True)
                self.ui.pushButton_img.setDisabled(True)
                self.ui.pushButton_camer.setDisabled(True)

    # 打开摄像头检测
    def button_camera_open(self):
        # 这部分也是QT的绘制界面
        if (self.opt != ''):
            if (self.ui.verticalLayout_5.count() > 0):
                for i in range(self.ui.verticalLayout_5.count()):
                    self.ui.verticalLayout_5.itemAt(i).widget().delete()
            self.draw_label = MyLabel(self)
            # 没有点击“绘制区域”时不能使用画笔
            self.draw_label.setFlag(False)
            self.ui.verticalLayout_5.addWidget(self.draw_label)



            # 设置使用的摄像头序号，系统自带为0
            video_value = self.define_video()
            # camera_num = 'http://hls01open.ys7.com/openlive/e5515428d3fc424d9d8c2286d4d4da82.hd.m3u8'
            camera_num = video_value
            # 打开摄像头
            self.cap = cv2.VideoCapture(camera_num)
            # 判断摄像头是否处于打开状态
            bool_open = self.cap.isOpened()
            if not bool_open:
                QtWidgets.QMessageBox.warning(self, u"警告", u"打开摄像头失败", buttons=QtWidgets.QMessageBox.Ok,
                                              defaultButton=QtWidgets.QMessageBox.Ok)
            else:
                fps, w, h, save_path = self.set_video_name_and_path()
                fps = 25  # 控制摄像头检测下的fps，Note：保存的视频，播放速度有点快，我只是粗暴的调整了FPS
                self.vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                self.timer_video.start(30)
                self.ui.pushButton_video.setDisabled(True)
                self.ui.pushButton_img.setDisabled(True)
                self.ui.pushButton_camer.setDisabled(True)

    # 定义视频帧显示操作
    def show_video_frame(self):
        name_list = []
        flag, img = self.cap.read()
        if img is not None:
            if self.draw_area == 1:
                area_poly = load_poly_area_data_simple(self.openfile_area)
                info_show = self.detect(name_list, img, area_poly)  # 检测结果写入到原始img上
            else:
                info_show = self.detect(name_list, img)
            self.vid_writer.write(img)  # 检测结果写入视频


            # 检测信息显示在QT界面----------------
            self.ui.textBrowser.setText(info_show)
            #----------------------------------

            # 同样是解决QT界面中由于原分辨率大小的图像和调整分辨率后的图像之间，用鼠标绘制多边形的位置偏移
            origin_size = img.shape
            global o_n_y_scale
            global o_n_x_scale
            o_n_x_scale = origin_size[1] / 640
            o_n_y_scale = origin_size[0] / 480


            #-----------QT显示结果部分---------------
            show = cv2.resize(img, (640, 480))  # 直接将原始img上的检测结果进行显示
            self.result = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
            showImage = QtGui.QImage(self.result.data, self.result.shape[1], self.result.shape[0],
                                     QtGui.QImage.Format_RGB888)
            self.draw_label.setPixmap(QtGui.QPixmap.fromImage(showImage))
            self.draw_label.setCursor(Qt.CrossCursor)  # 图片可以绘制
            self.draw_label.setScaledContents(True)  # 设置图像自适应界面大小


        else:
            self.timer_video.stop()
            # 读写结束，释放资源
            self.cap.release()  # 释放video_capture资源
            self.vid_writer.release()  # 释放video_writer资源
            self.draw_label.clear()
            # 视频帧显示期间，禁用其他检测按键功能
            self.ui.pushButton_video.setDisabled(False)
            self.ui.pushButton_img.setDisabled(False)
            self.ui.pushButton_camer.setDisabled(False)

    # 暂停与继续检测
    def button_video_stop(self):
        self.timer_video.blockSignals(False)
        # 暂停检测
        # 若QTimer已经触发，且激活
        if self.timer_video.isActive() == True and self.num_stop % 2 == 1:
            self.ui.pushButton_stop.setText(u'继续检测')  # 当前状态为暂停状态
            self.num_stop = self.num_stop + 1  # 调整标记信号为偶数
            self.timer_video.blockSignals(True)
        # 继续检测
        else:
            self.num_stop = self.num_stop + 1
            self.ui.pushButton_stop.setText(u'暂停检测')

    # 结束视频检测
    def finish_detect(self):

        self.cap.release()  # 释放video_capture资源
        if self.vid_writer is not None:
            self.vid_writer.release()  # 释放video_writer资源

        # 启动其他检测按键功能
        self.ui.pushButton_video.setDisabled(False)
        self.ui.pushButton_img.setDisabled(False)
        self.ui.pushButton_camer.setDisabled(False)
        self.ui.textBrowser.clear()
        if len(self.ui.verticalLayout_5) > 0:
            self.draw_label.Polygon_draw_list.clear()
            self.draw_label.Polygon_origin2json_list.clear()
            self.draw_label.Polygon_origin2canvas_list.clear()

        for i in reversed(range(self.ui.verticalLayout_5.count())):
            self.ui.verticalLayout_5.removeItem(self.ui.verticalLayout_5.itemAt(i))

        self.ui.pushButton.setText("绘制区域")
        self.num_stop = 0

        # 结束检测时，查看暂停功能是否复位，将暂停功能恢复至初始状态
        # Note:点击暂停之后，num_stop为偶数状态
        if self.num_stop % 2 == 0:
            print("Reset stop/begin!")
            self.ui.pushButton_stop.setText(u'暂停/继续')
            self.num_stop = self.num_stop + 1
            self.timer_video.blockSignals(False)

    def DrawPolygon(self):
        """
        用于与‘绘制区域’按钮绑定，通过draw_label的flag变量判断是否允许鼠标绘制区域
        """
        if self.ui.pushButton.text() == '绘制区域':
            self.Draw = "Polygon"
            if self.ui.verticalLayout_5.count() > 0:
                self.draw_label.setFlag(True)
                self.ui.pushButton.setText('停止绘制')
        else:
            self.draw_label.setFlag(False)
            self.ui.pushButton.setText('绘制区域')

# QT部分的绘制区域，这个不涉及区域入侵逻辑
# 在QLabel上实现QPainter，一开始就限制了Painter的范围在QLabel上
class MyLabel(QLabel):
    Polygon_draw_list = []  # 绘制在640 * 480分辨率画面上的多边形坐标
    Polygon_point = []
    Polygon_origin2json_list = []  # 绘制在原始画面大小，且会保存为json的画面坐标
    Polygon_origin2canvas_list = []  # 通过勾选区域入侵直接在画面上识别的坐标
    # 是否点击了‘绘制区域’按钮
    flag = False
    # 多边形点计数
    Point_count = 0
    move_x = 0.0
    move_y = 0.0

    def delete(self):
        self.clear()

    def combinePoint(self):
        if len(self.Polygon_list) > 0:
            point_count = len(self.Polygon_list) / 2
            for i in range(point_count):
                if i % 2 == 0:
                    str = 'x' + i + 1 + ''
                else:
                    str = 'y' + i + 1 + ''
                self.Polygon_point.append(str)

    def setFlag(self, flag):
        self.flag = flag

    def mouseMoveEvent(self, event):
        s = event.pos()
        self.setMouseTracking(True)
        print('此时鼠标移动的坐标 {move_x},{move_y}'.format(move_x=s.x(), move_y=s.y()))

    # 鼠标点击事件
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.Polygon_draw_list.clear()
            self.Polygon_origin2json_list.clear()
            self.Polygon_point.clear()
            self.Polygon_origin2canvas_list.clear()
            self.Point_count = 0
            self.update()
        elif self.flag:
            self.Point_count += 1
            self.mouseMoveEvent(event)
            pt_pos = event.pos()

            scaled_x = o_n_x_scale * pt_pos.x()
            scaled_y = o_n_y_scale * pt_pos.y()

            # 处理json中的坐标转换
            self.Polygon_origin2json_list.append(scaled_x)
            self.Polygon_origin2json_list.append(scaled_y)

            # 处理用于直接在画面上检测的原始尺寸坐标（双层list）
            origin2canvas_list = []
            origin2canvas_list.append(scaled_x)
            origin2canvas_list.append(scaled_y)
            self.Polygon_origin2canvas_list.append(origin2canvas_list)

            # 直接在画面上绘制的多边形坐标
            self.Polygon_draw_list.append(pt_pos.x())
            self.Polygon_draw_list.append(pt_pos.y())
            Point_x = "x" + str(self.Point_count)
            Point_y = "y" + str(self.Point_count)

            self.Polygon_point.append(Point_x)
            self.Polygon_point.append(Point_y)
            # list转dict保存成json
            polygon = zip(self.Polygon_point, self.Polygon_origin2json_list)

            with open('ruqin/ruqin.json', 'w') as ts:
                json.dump(dict(polygon), ts)
            with open('ruqin/ruqin.json', 'r') as sf:
                j = json.load(sf)

            print(j)
            self.update()

    # 绘制事件
    def paintEvent(self, event):
        super().paintEvent(event)
        # 相当于QLabel上绘制
        painter = QPainter(self)
        painter.setPen(QColor(255, 0, 0))
        painter.begin(self)
        polygon = QPolygon()
        if runqin_check_for_draw is not True and len(self.Polygon_draw_list) >= 6:
            polygon.setPoints(self.Polygon_draw_list)
            painter.drawPolygon(polygon)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    current_ui = UI_Logic_Window()
    current_ui.setMouseTracking(True)  #
    current_ui.show()
    sys.exit(app.exec_())
