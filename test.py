
import sys
from PySide2.QtCore import *
# from PySide2.QtWidgets import (QWidget,QPushButton,QComboBox,QSpinBox,QHBoxLayout,QVBoxLayout,QApplication,QLineEdit,
#                                 QLabel,QGridLayout)
from PySide2.QtWidgets import *

from PySide2.QtGui import *
import numpy as np
import cv2
from os.path import exists
from os import mkdir


from time import sleep,time

import xml.etree.ElementTree as ET
from xml.dom import minidom


listColors =    [QColor(25,25,112),
                QColor(255,105,180),
                QColor(60,179,113),
                QColor(255,140,0),
                QColor(131,139,139),
                QColor(30,144,255),
                QColor(255,0,255),
                QColor(107,142,35),
                QColor(138,43,226),
                QColor(184,134,11),
                QColor(0,100,0),
                QColor(71,60,139),
                QColor(160,82,45),
                QColor(106,90,205),
                ]

class MainApp(QWidget):

    def __init__(self,path):
        self._name_database_ = 'vehicles'
        self._div = 2
        if path != '':
            self.videoPath = path
        else:
            self.videoPath = 0
        QWidget.__init__(self)
        self.initsetup()
        self.designer()
        self.logic()

    def initsetup(self):
        #init camera
        self.capture = cv2.VideoCapture(self.videoPath)
        sleep(0.2)
        _,frame = self.capture.read()
        self.video_size = QSize(frame.shape[1],frame.shape[0])
        self.video_resize = QSize(frame.shape[1]/self._div,frame.shape[0]/self._div)

        self.timer = QTimer()
        self.timer.timeout.connect(self.display_video_stream)

        # leemos las clases
        self.ListID = []
        if exists('labels.txt'):
            with open('labels.txt','r') as f:
                txt = f.read()
                for l in txt.strip('\n').split('\n'):
                    self.ListID.append(l)

        print(self.ListID)

    def logic(self):
        self.listObjects = []
        newObject = False
        def mouseMoveEvent(e):
            if e.x()>=0 and e.x()<=self.video_resize.width()-1:
                x = e.x()
            elif e.x()<0:
                x = 0
            elif e.x()>self.video_resize.width()-1:
                x = self.video_resize.width()-1
            if e.y()>=0 and e.y()<=self.video_resize.height()-1:
                y = e.y()
            elif e.y()<0:
                y = 0
            elif e.y()>self.video_resize.height()-1:
                y = self.video_resize.height()-1
            rect = self.listObjects[-1].get('rect')

            xmin = int(rect.x()/self._div)
            ymin = int(rect.y()/self._div)
            rect.setRect(xmin*self._div,ymin*self._div,(x-xmin)*self._div,(y-ymin)*self._div)

            self.updateImage()

        def mousePressEvent(e):
            newObject = True
            rectObj = QRect(e.x()*self._div,e.y()*self._div,0,0)
            obj = {'rect':rectObj,'class':self.cbID.currentText(),'time':time()}
            self.listObjects.append(obj)

        def mouseReleaseEvent(e):
            newObject = False
            obj = self.listObjects[-1]
            if obj.get('rect').width() != 0 and obj.get('rect').height() != 0:
                self.addObjectToTable()
            else:
                del self.listObjects[-1]

        self.videocapture_label.mouseMoveEvent = mouseMoveEvent
        self.videocapture_label.mousePressEvent = mousePressEvent
        self.videocapture_label.mouseReleaseEvent = mouseReleaseEvent

        self.bSaveChange.clicked.connect(self.saveAll)

        self.cbID.addItems(self.ListID)

        self.bPlay.clicked.connect(self.fControl)
        self.bAddId.clicked.connect(self.enterNewId)

    def enterNewId(self):
        txt,ok = QInputDialog.getText(self,'NuevaClase','Nombre')
        if ok:
            with open('labels.txt','a') as f:
                f.write(txt+'\n')

    def designer(self):
        """Initialize widgets.
        """
        self.videocapture_label = QLabel()
        self.videocapture_label.setFixedSize(self.video_resize)

        self.bAddId = QPushButton('ADD')
        self.bPlay = QPushButton("Play")
        self.cbID = QComboBox()

        self.tableChange = QTableWidget()
        self.tableChange.setColumnCount(6)
        self.tableChange.verticalHeader().setVisible(True)
        # self.tableChange.horizontalHeader().setStretchLastSection(True)
        self.tableChange.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableChange.horizontalHeader().setHighlightSections(False)
        self.tableChange.setHorizontalHeaderLabels(['Clase','X','Y','Width','Height','Delete'])
        self._row = -1
        self.tableChange.currentCellChanged.connect(self._setRow )

        self.bCancelChange = QPushButton('Cancel')
        self.bSaveChange = QPushButton('Save')
        self.bDelChange = QPushButton('Del')

        lhButtonsChange = QHBoxLayout()
        lhButtonsChange.addWidget(self.bCancelChange)
        lhButtonsChange.addWidget(self.bSaveChange)
        lhButtonsChange.addWidget(self.bDelChange)

        lvChangePanel = QVBoxLayout()

        lvChangePanel.addWidget(self.tableChange)
        lvChangePanel.addLayout(lhButtonsChange)

        lhControl = QHBoxLayout()
        lhControl.addWidget(self.bAddId)
        lhControl.addWidget(self.bPlay)
        lhControl.addWidget(self.cbID)

        lvCameraPanel = QVBoxLayout()
        lvCameraPanel.addWidget(self.videocapture_label)
        lvCameraPanel.addLayout(lhControl)

        self.main_layout = QGridLayout()
        self.main_layout.addLayout(lvCameraPanel,0,1,1,1)
        self.main_layout.addLayout(lvChangePanel,0,2,1,1)

        self.setLayout(self.main_layout)

    def _setRow(self,row,colum):
        self._row = row
        self.updateImage()

    def addObjectToTable(self):

        rectObj = self.listObjects[-1].get('rect')
        tim = self.listObjects[-1].get('time')

        a = rectObj.x()
        b = rectObj.y()
        c = rectObj.x()+rectObj.width()
        d = rectObj.y()+rectObj.height()

        xmin = min(a,c)
        ymin = min(b,d)
        xmax = max(a,c)-1
        ymax = max(b,d)-1

        rectObj.setCoords(xmin,ymin,xmax,ymax)

        cbIDChange = QComboBox()
        cbIDChange.addItems(self.ListID)
        cbIDChange.setCurrentIndex(self.cbID.currentIndex())
        cbIDChange.currentTextChanged.connect(lambda t: self.changeObject(tim,'ID',t))
        sbXChange = QSpinBox()
        sbXChange.setMinimum(0)
        sbXChange.setMaximum(self.video_size.width())
        sbXChange.setValue(xmin)
        sbXChange.valueChanged.connect(lambda t: self.changeObject(tim,'X',t))
        sbYChange = QSpinBox()
        sbYChange.setMinimum(0)
        sbYChange.setMaximum(self.video_size.height())
        sbYChange.setValue(ymin)
        sbYChange.valueChanged.connect(lambda t: self.changeObject(tim,'Y',t))
        sbWChange = QSpinBox()
        sbWChange.setMinimum(0)
        sbWChange.setMaximum(self.video_size.width())
        sbWChange.setValue(xmax)#-xmin)
        sbWChange.valueChanged.connect(lambda t: self.changeObject(tim,'Width',t))
        sbHChange = QSpinBox()
        sbHChange.setMinimum(0)
        sbHChange.setMaximum(self.video_size.height())
        sbHChange.setValue(ymax)#-ymin)
        sbHChange.valueChanged.connect(lambda t: self.changeObject(tim,'Height',t))
        pbDel = QPushButton('X')
        pbDel.clicked.connect(lambda t: self.delObject(tim))

        row = len(self.listObjects)
        self.tableChange.setRowCount(row)

        self.tableChange.setCellWidget(row-1,0,cbIDChange)
        self.tableChange.setCellWidget(row-1,1,sbXChange)
        self.tableChange.setCellWidget(row-1,2,sbYChange)
        self.tableChange.setCellWidget(row-1,3,sbWChange)
        self.tableChange.setCellWidget(row-1,4,sbHChange)
        self.tableChange.setCellWidget(row-1,5,pbDel)

    def delObject(self,tim):
        row = -1
        for i,obj in enumerate(self.listObjects):
            if tim == obj.get('time'):
                del self.listObjects[i]
                row = i
                break
        self.tableChange.removeRow(row)

    def changeObject(self,tim,key,value):
        row = -1
        for i,obj in enumerate(self.listObjects):
            if tim == obj.get('time'):
                rect = self.listObjects[i].get('rect')
                obj = self.listObjects[i]
                row = i
                break

        if key=='X':
            x1,y1,x2,y2 = rect.getCoords()
            rect.setCoords(value,y1,x2,y2)
            #rect.setX(value)
        elif key =='Y':
            x1,y1,x2,y2 = rect.getCoords()
            rect.setCoords(x1,value,x2,y2)
            #rect.setY(value)
        elif key == 'Width':
            x1,y1,x2,y2 = rect.getCoords()
            rect.setCoords(x1,y1,value,y2)
            # rect.setWidth(value)
        elif key == 'Height':
            x1,y1,x2,y2 = rect.getCoords()
            rect.setCoords(x1,y1,x2,value)
            # rect.setHeight(value)
        elif key == 'ID':
            obj['class']=value

        self.updateImage()

    def fControl(self):
        if self.bPlay.text()=='Play':
            self.bPlay.setText('Pause')
            self.timer.start(30)
        elif self.bPlay.text()=='Pause':
            self.bPlay.setText('Play')
            self.timer.stop()

    def display_video_stream(self):
        """Read frame from camera and repaint QLabel widget.
        """
        self.getFrame()
        self.updateImage()

    def getFrame(self):
        _, self.frameOriginal = self.capture.read()

    def processFrame(self):
        self.frame = cv2.resize(self.frameOriginal,(self.video_resize.width(),self.video_resize.height()))
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

    def drawRectangles(self):
        self.processFrame()
        self.image = QImage(self.frame, self.frame.shape[1], self.frame.shape[0],
                       self.frame.strides[0], QImage.Format_RGB888)

        painter = QPainter(self.image)
        for i,obj in enumerate(self.listObjects):
            rect = obj.get('rect')
            objClass = obj.get('class')
            idxID = self.ListID.index(objClass)
            rectResize = QRect()
            x1,y1,x2,y2 = rect.getCoords()
            rectResize.setCoords(x1/self._div,y1/self._div,x2/self._div,y2/self._div)
            # if i==self._row:
            #     painter.setPen(QColor(255,255,255))
            # else:
            painter.setPen(listColors[idxID%14])
            painter.drawRect(rectResize)

    def updateImage(self):
        self.drawRectangles()
        self.videocapture_label.setPixmap(QPixmap.fromImage(self.image))

    def mouseMoveEvent(self, e):

        self.update()

    def createDirectories(self,root):
        try:
            mkdir(root)
            mkdir(root+'/Annotations/')
            mkdir(root+'/ImageSets/')
            mkdir(root+'/ImageSets/Main/')
            mkdir(root+'/JPEGImages/')
        except:
            pass

    def saveAll(self):
        # create a directorios
        root = self._name_database_
        self.createDirectories(root)

        #guardamos imagen
        from datetime import datetime
        timenow = datetime.now()
        format = "%Y%m%d-%H%M%S"
        name = timenow.strftime(format)
        imgName = name + '.jpg'
        xmlName = name + '.xml'
        self.saveImage(root+'/JPEGImages/'+imgName)

        #creamos anotacion xml
        self.createXML(root+'/Annotations/'+xmlName,imgName,root,self.frameOriginal.shape,self.listObjects)

        #agregamos a la lista de train.txt
        with open(root + '/ImageSets/Main/trainval.txt','a') as f:
            f.write(name+'\n')

        self.clearAll()

    def clearAll(self):
        self.listObjects = []
        self.tableChange.clearContents()
        self.tableChange.setRowCount(0)
        self.updateImage()

    def saveImage(self,path):
        cv2.imwrite(path,self.frameOriginal)

    def createXML(self,namefile,nameimg,folder,size,listObjects):
        xmlAnnot = ET.Element('annotation')
        xmlAnnotFilename = ET.SubElement(xmlAnnot,'filename')
        xmlAnnotFilename.text = nameimg
        xmlAnnotFolder = ET.SubElement(xmlAnnot,'folder')
        xmlAnnotFolder.text = folder
        xmlAnnotSource = ET.SubElement(xmlAnnot,'source')
        xmlAnnotSourceDatabase = ET.SubElement(xmlAnnotSource,'database')
        xmlAnnotSourceDatabase.text = folder
        xmlAnnotSourceAnnotation = ET.SubElement(xmlAnnotSource,'annotation')
        xmlAnnotSourceAnnotation.text = 'custom'
        xmlAnnotSourceImage = ET.SubElement(xmlAnnotSource,'image')
        xmlAnnotSourceImage.text = 'custom'
        xmlAnnotSize = ET.SubElement(xmlAnnot,'size')
        xmlAnnotSizeWidth = ET.SubElement(xmlAnnotSize,'width')
        xmlAnnotSizeWidth.text = str(size[1])
        xmlAnnotSizeHeight = ET.SubElement(xmlAnnotSize,'height')
        xmlAnnotSizeHeight.text = str(size[0])
        xmlAnnotSizeDepth = ET.SubElement(xmlAnnotSize,'depth')
        xmlAnnotSizeDepth.text = str(size[2])
        xmlAnnotSegmented = ET.SubElement(xmlAnnot,'segmented')
        xmlAnnotSegmented.text = '0'

        for obj in listObjects:
            classID = obj.get('class')
            rect = obj.get('rect')
            xmin,ymin,xmax,ymax = rect.getCoords()
            xmlObj = ET.SubElement(xmlAnnot,'object')
            xmlObjName = ET.SubElement(xmlObj,'name')
            xmlObjName.text = classID
            xmlObjPose = ET.SubElement(xmlObj,'pose')
            xmlObjPose.text = 'unspecified'
            xmlObjTruncated = ET.SubElement(xmlObj,'truncated')
            xmlObjTruncated.text = '0'
            xmlObjDifficult = ET.SubElement(xmlObj,'difficult')
            xmlObjDifficult.text = '0'

            xmlObjBndbox = ET.SubElement(xmlObj,'bndbox')
            xmlObjBndboxXmin = ET.SubElement(xmlObjBndbox,'xmin')
            xmlObjBndboxXmin.text = str(xmin)
            xmlObjBndboxYmin = ET.SubElement(xmlObjBndbox,'ymin')
            xmlObjBndboxYmin.text = str(ymin)
            xmlObjBndboxXmax = ET.SubElement(xmlObjBndbox,'xmax')
            xmlObjBndboxXmax.text = str(xmax)
            xmlObjBndboxYmax = ET.SubElement(xmlObjBndbox,'ymax')
            xmlObjBndboxYmax.text = str(ymax)


        dom = minidom.parseString(ET.tostring(xmlAnnot))
        with open(namefile,'w') as f:
            f.write(dom.toprettyxml(indent='\t'))

class videoPath(QWidget):
    signalStart = Signal()
    def __init__(self):
        QWidget.__init__(self)
        self.designer()
        self.logic()

    def designer(self):
        self.qle_videoPath = QLineEdit()
        self.qle_videoPath.returnPressed.connect(self.start)
        try:
            with open('path.txt','r') as f:
                txt = f.read()
                self.qle_videoPath.setText(txt)
        except:
            pass
        self.b_ok = QPushButton('OK')
        self.b_cancel = QPushButton('Cancel')
        hg = QHBoxLayout()
        hg.addWidget(self.b_cancel)
        hg.addWidget(self.b_ok)
        vg = QVBoxLayout()
        vg.addWidget(self.qle_videoPath)
        vg.addLayout(hg)

        self.setLayout(vg)

    def logic(self):
        self.b_cancel.clicked.connect(self.close)
        self.b_ok.clicked.connect(self.start)
        self.b_ok.setDefault(True)

    def start(self):
        # save path
        with open('path.txt','w') as f:
            f.write(self.qle_videoPath.text())

        self.signalStart.emit()
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    def start():
        win2 = MainApp(win.qle_videoPath.text())
        win2.show()
    win = videoPath()
    win.signalStart.connect(start)
    win.show()
    sys.exit(app.exec_())
