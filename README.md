# Real-time Area Intrusion Detection Method and System based on YOLOv5
![GitHub stars](https://img.shields.io/github/stars/JakeVander/YOLOv5-Intrusion-Detection-System)

[中文文档](./README_zh.md)

**Update 2023.04.28**

Added mouse-drawing polygon function:
- Now supports drawing polygons with mouse or directly reading json type coordinates information.
---
## Project Introduction
Using PyQt5 to add a visual detection interface for YOLOv5, and implementing simple interface switching and area intrusion detection, as follows:
**Features:**
* UI interface and logical code are separated
* Supports user-selected models
* Outputs detection results and corresponding information
* Supports image, video, and camera detection
Supports video pause and continue detection
Supports area intrusion, custom area, and counting.
## Quick Start
**Environment and Related File Configuration:**
 - Set up the environment according to the `requirements` in `ult-yolov5`.
 - Install PyQt5 and make sure to install and configure it in an `env` environment.
 - Download or train a model and put the `.pt` file into the `weights` folder. You can choose your own weight file, and the program will open the `weights` folder by default.
    -  The YOLOv5 release version used is v5.0:  [Releases · ultralytics/yolov5 (github.com)](https://github.com/ultralytics/yolov5/releases)
 - Set the `opt` parameter in `init` to be consistent with the setting in `detect.py`.
 - Need to configure the external tools Qtdesigner and PYUIC in PyCharm.

**How to Use:**

 - Run `detect_logicwd.py` directly to enter the detection interface.
    ```shell script
   python detect_logicwd.py
   ```
## Project Structure
```
.
├── README.md
├── README_EN.md
├── models/                    # configuration files for yolov5
├── output/                    # target detection results of yolov5 for images
├── ruqin/                     # JSON files for drawing polygonal areas
├── ui/                        # generated UI files and PY files of PyQT5, the currently used interface file is detect_ui_new_v2.py
├── weights/                   # storage folder for weights files of yolov5 and other training models
├── line_draw.py               # includes the detection algorithm of area intrusion, control of displaying invading objects in detection area, drawing polygonal areas, etc.
└── detect_logicwd.py          # software main body and entry point of the project. It includes importing corresponding PY files of UI, logical implementation of various buttons, outputting information (detection frame, object information, coordinates, confidence level, video screen, etc.).
```
## Usage
1. After launching `detect_logicwd.py`, the software interface will be displayed as shown below:
![image-20230428171100706](README.assets/image-20230428171100706.png)
The system interface is divided into the left function selection, the right object detection object information, and the middle detection result screen.
2. First, select an available yolov5 weight file in the **功能选择** section, and then click the **初始化模型** button to load the target detection model. The selection of weight models supports self-trained models, as long as they are placed in the corresponding weights folder and the corresponding comboBox text is added through PyQT.
![image-20230428171318628](README.assets/image-20230428171318628.png)
3. Subsequently, select **图片检测** or **视频检测** and perform object detection by uploading a local image or local video. Click the **结束检测** button to terminate the current target detection.
   1. Image detection:
      ![image-20230428172326462](README.assets/image-20230428172326462.png)
   2. Video detection:
   ![image-20230428172428674](README.assets/image-20230428172428674.png)
4. In **视频检测**, you can draw a polygonal area. When an object enters the polygonal area, the category of the object will be detected (the judgment criterion for object entry is the relative position relationship between the center position of the detected box recognized by the target detection and the polygon).
   1. Drawing operation: Check **区域入侵**, click **绘制区域**, click the left mouse button in the **检测结果** area to create the coordinates of the polygon. When the number of created points is greater than or equal to 2, the invasion detection algorithm will automatically start, and only the objects that enter the drawn area will be detected and related detection information will be output, while the objects not outside the area or recognized will not have any output.
      ![image-20230428173400623](README.assets/image-20230428173400623.png)
   3. Upload the json format coordinate file: Prepare the file in advance, the content is organized as follows, (xn, yn) represents the coordinate information of a point of the polygon, and the coordinate system takes the upper left corner area of **检测结果** in the software interface as the origin.
      ![image-20230428173707347](README.assets/image-20230428173707347.png)
      Check **区域入侵**, select the uploaded json file, and the invasion detection algorithm will be enabled.
      ![image-20230428173847547](README.assets/image-20230428173847547.png)
   4. In addition to local videos, real-time video streaming detection is also supported by providing the corresponding video streaming information. Both mouse drawing and uploading area methods are supported for invasion detection, which are not demonstrated due to limitations in computer performance.
---
If you find this repository useful, please consider giving it a star ⭐️! It helps to support the project and show appreciation for the work put into it.
