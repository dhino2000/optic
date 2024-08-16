# ROI Tracking GUI
import itk
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
from scipy.io import savemat, loadmat
import tifffile
import cv2
import random
from utils import *
import datetime

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Elastix Config
class ElastixConfigWindow(QDialog):
    def __init__(self, parent, function):
        super().__init__(parent)
        self.parent = parent
        self.function = function
        self.setWindowTitle("Elastix Config")
        self.setGeometry(100, 100, 900, 600)
        self.dict_label = {}
        self.dict_entry = {}
        # Elastix parameter
        self.dict_parameter_map = parent.dict_parameter_map[function]
        
        layout = QGridLayout()
        # 4列になるようlabel, entryを配置
        for i, (key_parameter, tuple_value_parameter) in enumerate(self.dict_parameter_map.items()):
            row = i % 7
            column = i // 7
            self.dict_label[key_parameter] = QLabel(key_parameter)
            layout.addWidget(self.dict_label[key_parameter], row*2, column)
            value_parameter = ' '.join(tuple_value_parameter) # tupleをstrに変換
            self.dict_entry[key_parameter] = QLineEdit(value_parameter)
            layout.addWidget(self.dict_entry[key_parameter], row*2+1, column)
        
        self.setLayout(layout)
    
    def reject(self):
        # Elastix parameter 更新
        for key_parameter in self.dict_parameter_map.keys():
            value = list(self.dict_entry[key_parameter].text().split(" "))
            self.dict_parameter_map[key_parameter] = value
        self.parent.dict_parameter_map[self.function] = self.dict_parameter_map
        super().reject()
        self.close()

class Suite2pROITrackingGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Suite2pROITrackingGUI")
        self.setGeometry(100, 100, 1200, 200)
        self.setupUI_done = False

        self.dict_label       = {} # labelの保管
        self.dict_entry       = {} # entryの保管
        self.dict_button      = {} # buttonの保管
        self.dict_ax          = {} # axの保管
        self.dict_checkbox    = {} # checkboxの保管
        self.dict_slider      = {} # sliderの保管
        self.dict_combobox    = {} # pulldownの保管
        self.dict_list        = {} # ListWidgetの保管
        self.dict_buttongroup = {}
        self.dict_scene       = {}
        self.dict_view        = {}
        self.dict_table       = {}
        self.dict_figure      = {}
        self.dict_canvas      = {}
        self.dict_opacity     = {}
        self.dict_roiPixmapItem = {}
        self.dict_roiPixmapItemHighlight = {}
        self.dict_table_selectedRow = {}
    
        self.setupFileLoadUI()
        
        self.dict_Fall          = {}
        self.dict_im            = {}
        self.dict_im_original   = {}
        self.dict_im_ref        = {}
        self.dict_grid          = {}
        self.dict_grid_original = {}
        self.ROIOpacity_init = 50 # ROI透明度の初期値
        # Tableの列名と列番号のdict
        self.dict_celltypes = {"Astrocyte": 2, "Neuron": 3, "Not Cell": 4, "Check": 5, "Tracking": 6, "Memo": 7}
        # Elastix parameter
        self.dict_parameter_map = {}
        for function in ["affine", "bspline"]:
            parameter_object = itk.ParameterObject.New()
            self.dict_parameter_map[function] = dict(parameter_object.GetDefaultParameterMap(function, 4).items())
        
    # Widget, LayoutなどUI設定用の関数
    """
    UI setup Function
    """    
    # File load用のUIセットアップ
    def setupFileLoadUI(self):
        self.mainLayout = QGridLayout()
        
        # checkroi_fix, setup, checkroi_movのLayoutを配置するためのLayout
        self.Layout_setupcheckroi = QHBoxLayout()
        
        Layout_setup = QVBoxLayout()
        # ファイルパスとbrowseボタン
        layout_path_fall_fix = self.makeLoadFileWidgetLayout(label="Fall mat file path (Fixed Image)", key="path_fall_fix", fileFilter="mat Files (*.mat);;All Files (*)")
        layout_path_tif_fix = self.makeLoadFileWidgetLayout(label="Tiff image file path (Fixed Image) (optional)", key="path_tif_fix", fileFilter="tiff Files (*.tif *.tiff);;All Files (*)")
        layout_path_fall_mov = self.makeLoadFileWidgetLayout(label="Fall mat file path (Moving Image)", key="path_fall_mov", fileFilter="mat Files (*.mat);;All Files (*)")
        layout_path_tif_mov = self.makeLoadFileWidgetLayout(label="Tiff image file path (Moving Image) (optional)", key="path_tif_mov", fileFilter="tiff Files (*.tif *.tiff);;All Files (*)")
        
        self.Layout_setup_button = QHBoxLayout()
        # Load
        self.dict_button["loadFile"] = QPushButton("Load files")
        self.dict_button["loadFile"].clicked.connect(self.loadFilePathsandInitialize)
        self.Layout_setup_button.addWidget(self.dict_button["loadFile"])
        # Exitボタンの設定
        self.dict_button["exit"] = QPushButton("Exit")
        self.dict_button["exit"].clicked.connect(self.exitApp)
        self.Layout_setup_button.addWidget(self.dict_button["exit"])
        
        Layout_setup.addLayout(layout_path_fall_fix)
        Layout_setup.addLayout(layout_path_tif_fix)
        Layout_setup.addLayout(layout_path_fall_mov)
        Layout_setup.addLayout(layout_path_tif_mov)
        Layout_setup.addLayout(self.Layout_setup_button)
        Layout_setup.setSpacing(0)  # レイアウト間のスペーシングを設定
        
        self.Layout_setupcheckroi.addLayout(Layout_setup)
        
        self.mainLayout.addLayout(self.Layout_setupcheckroi, 2, 0, 1, 2)
        
        widget = QWidget()
        widget.setLayout(self.mainLayout)
        self.setCentralWidget(widget)
        
    # 読み込むファイルを選択するためのウィジェット
    def makeLoadFileWidgetLayout(self, label="", key="", fileFilter=""):
        hboxlayout = QHBoxLayout() # entry, button
        vboxlayout = QVBoxLayout() # label, entry. button
        
        self.dict_label[key] = QLabel(label)
        self.dict_entry[key] = QLineEdit()
        self.dict_entry[key].setMinimumWidth(800)
        self.dict_button[f"browse_{key}"] = QPushButton("Browse")
        self.dict_button[f"browse_{key}"].clicked.connect(lambda: self.openFileDialog(fileFilter, self.dict_entry[key]))
        hboxlayout.addWidget(self.dict_entry[key])
        hboxlayout.addWidget(self.dict_button[f"browse_{key}"])
        vboxlayout.addWidget(self.dict_label[key])
        vboxlayout.addLayout(hboxlayout)
        return vboxlayout
    
    # GUI, データの初期化
    def initializeGUI(self):
        for key in ["fix", "mov"]:
            Fall = loadmat(self.dict_entry[f"path_fall_{key}"].text())
            self.dict_Fall[key] = self.convertDictStatFromFall(Fall, key)
            im = self.dict_Fall[key]["ops"]["meanImg"]
            self.dict_im[key] = self.convertImageToINT(im, dtype="uint16")
            self.dict_im_original[key] = self.convertImageToINT(im, dtype="uint16")
            self.dict_grid[key] = self.makeGridCoords()
            self.dict_grid_original[key] = self.makeGridCoords()
            # Optional tif画像
            if self.dict_entry[f"path_tif_{key}"].text():
                self.dict_im_ref[key] = self.convertImageToINT(tifffile.imread(self.dict_entry[f"path_tif_{key}"].text()))
            else:
                self.dict_im_ref[key] = np.zeros(im.shape)
        # Elastixの変形結果画像
        self.dict_im["res"] = np.zeros(self.dict_im["fix"].shape)
        self.dict_im["res"] = self.dict_im["mov"]
        
    # File load後のUIセットアップ
    def setupUI(self):
        self.setGeometry(100, 100, 1800, 1000)
        
        # Control Layout
        Layout_control = QHBoxLayout()
        Layout_control.addLayout(self.makeROICheckbuttonSliderLayout("fix"))
        Layout_control.addLayout(self.makeROIMatchingControlLayout())
        Layout_control.addLayout(self.makeROICheckbuttonSliderLayout("mov"))
        
        # ROI, Table, Plot Layout
        Layout_fixmov = QHBoxLayout()
        Layout_fix = self.makeLayoutViewTablePlot("fix")
        Layout_mov = self.makeLayoutViewTablePlot("mov")
        Layout_fixmov.addLayout(Layout_fix)
        Layout_fixmov.addLayout(Layout_mov)
        
        # ROIcheck Layout, Layout_setupcheckroiに追加
        Layout_roicheck_fix = self.makeROICheckLayout("fix")
        Layout_roicheck_mov = self.makeROICheckLayout("mov")
        
        # Widget, Layoutの配置
        self.mainLayout.addLayout(Layout_fixmov, 0, 0, 1, 2)
        self.mainLayout.addLayout(Layout_control, 1, 0, 1, 2)
        self.Layout_setupcheckroi.insertLayout(0, Layout_roicheck_fix)
        self.Layout_setupcheckroi.addLayout(Layout_roicheck_mov)

        self.setLayout(self.mainLayout)
        self.setupUI_done = True
        
    # Fixed, Moving imageのtable, view, plot WidgetをまとめたLayout
    def makeLayoutViewTablePlot(self, key): # key: fix, mov
        # Fixed Image Layout
        Layout = QVBoxLayout()
        
        Layout_TableScene = QHBoxLayout()
        # Table widget
        self.dict_table_selectedRow[key] = 0
        self.dict_table[key] = QTableWidget()
        self.dict_table[key] = self.setupTableWidget(self.dict_table[key], key)
        
        # ROI表示画像
        self.dict_scene[key] = QGraphicsScene()
        self.dict_view[key] = QGraphicsView(self.dict_scene[key])
        self.dict_view[key].setMinimumHeight(530)
        self.dict_view[key].setMinimumWidth(530)
        self.dict_view[key].setStyleSheet("background-color: black;")  # 背景色を黒に設定
        # クリック時のイベント
        self.dict_view[key].mousePressEvent = lambda event: self.viewMousePressEvent(event, key)
        # ROI, tif imageの設定
        self.dict_roiPixmapItem[key], self.dict_roiPixmapItemHighlight[key] = None, None
        self.makeROIPixmap(key)
        self.updateImageDisplay(key)
        
        Layout_TableScene.addWidget(self.dict_table[key])
        Layout_TableScene.addWidget(self.dict_view[key])
        
        Layout_Plot = QHBoxLayout()
        # trace plot widget
        Layout_Plot_Figure = QVBoxLayout()
        self.dict_figure[key] = Figure()
        self.dict_canvas[key] = FigureCanvas(self.dict_figure[key])
        Layout_Plot_Figure.addWidget(self.dict_canvas[key])
        self.dict_ax[key] = self.dict_figure[key].add_subplot(1, 1, 1)
        
        Layout_Plot_LabelButton = QVBoxLayout()
        # ROI property
        Layout_Plot_Label = QVBoxLayout()
        for prop in ["med", "npix", "npix_soma", "compact", "solidity", "radius", "aspect_ratio", "skew", "std"]:
            self.dict_label[f"{prop}_{key}"] = QLabel(f"{prop}:")
            Layout_Plot_Label.addWidget(self.dict_label[f"{prop}_{key}"])
        Layout_Plot_LabelButton.addLayout(Layout_Plot_Label)        
        Layout_Plot.addLayout(Layout_Plot_Figure)
        Layout_Plot.addLayout(Layout_Plot_LabelButton)
        
        Layout.addLayout(Layout_TableScene)
        Layout.addLayout(Layout_Plot)
        return Layout
    
    # ROIの表示調整用Layout
    def makeROICheckbuttonSliderLayout(self, key):
        Layout_ROIshow = QVBoxLayout()
        
        # チェックボックスの設定
        Layout_ROIshow_checkbox = QHBoxLayout()
        for channel, func_ in zip(["ref", "grid"], [lambda state, key=key: self.toggleImageVisibility(key, state, "ref"), lambda state, key=key: self.toggleImageVisibility(key, state, "grid")]):
            self.dict_checkbox[f"show_{key}_{channel}"] = QCheckBox(f"Show {key} {channel} Image")
            self.dict_checkbox[f"show_{key}_{channel}"].setChecked(True)
            self.dict_checkbox[f"show_{key}_{channel}"].stateChanged.connect(func_)
            Layout_ROIshow_checkbox.addWidget(self.dict_checkbox[f"show_{key}_{channel}"])
            
        # fixの時だけElastix用の変形後の画像用チェックボックスを追加
        if key == "fix":
            self.dict_checkbox[f"show_{key}_res"] = QCheckBox(f"Show Elastix Result Image")
            self.dict_checkbox[f"show_{key}_res"].setChecked(True)
            self.dict_checkbox[f"show_{key}_res"].stateChanged.connect(lambda state, key=key: self.toggleImageVisibility(key, state, "res"))
            Layout_ROIshow_checkbox.addWidget(self.dict_checkbox[f"show_{key}_res"])
            
        Layout_ROIshow.addLayout(Layout_ROIshow_checkbox)
        
        # Min, Max, Opacity Valueスライダーの設定
        Layout_ROIshow_sliderminmax = QHBoxLayout()
        Layout_ROIshow_slideropacity = QVBoxLayout()
        list_key_slider = [key]
        if key == "fix":
            list_key_slider.append("res")

        # Min, Maxスライダー, fixの場合はresも追加して2列に
        for key_slider in list_key_slider:
            Layout_ROIshow_sliderminmax_keyslider = QVBoxLayout()
            for m, default_value in zip(["min", "max"], [0, 255]):
                self.dict_slider[f"{m}Value_{key_slider}"] = QSlider(Qt.Horizontal)
                self.dict_slider[f"{m}Value_{key_slider}"].setMinimum(0)
                self.dict_slider[f"{m}Value_{key_slider}"].setMaximum(255)
                self.dict_slider[f"{m}Value_{key_slider}"].setMaximumHeight(5)
                self.dict_slider[f"{m}Value_{key_slider}"].setValue(default_value)
                self.dict_slider[f"{m}Value_{key_slider}"].valueChanged.connect(lambda value, key=key: self.adjustContrast(key)) # resの時もfixを参照
                self.dict_label[f"{m}Value_{key_slider}"] = QLabel(f"{m} Value ({key_slider})")
                Layout_ROIshow_sliderminmax_keyslider.addWidget(self.dict_label[f"{m}Value_{key_slider}"])
                Layout_ROIshow_sliderminmax_keyslider.addWidget(self.dict_slider[f"{m}Value_{key_slider}"])
            Layout_ROIshow_sliderminmax.addLayout(Layout_ROIshow_sliderminmax_keyslider)
            
        self.dict_slider[f"opacityValue_{key}"] = QSlider(Qt.Horizontal)
        self.dict_slider[f"opacityValue_{key}"].setMinimum(0)
        self.dict_slider[f"opacityValue_{key}"].setMaximum(255)
        self.dict_slider[f"opacityValue_{key}"].setMaximumHeight(5)
        self.dict_slider[f"opacityValue_{key}"].setValue(50)
        self.dict_slider[f"opacityValue_{key}"].valueChanged.connect(lambda value, key=key: self.changeROIOpacity(key, value))
        self.dict_label[f"opacityValue_{key}"] = QLabel(f"opacity Value ({key})")
        Layout_ROIshow_slideropacity.addWidget(self.dict_label[f"opacityValue_{key}"])
        Layout_ROIshow_slideropacity.addWidget(self.dict_slider[f"opacityValue_{key}"])
        
        Layout_ROIshow.addLayout(Layout_ROIshow_sliderminmax)
        Layout_ROIshow.addLayout(Layout_ROIshow_slideropacity)
        
        return Layout_ROIshow
    
    # ROI Matching用のLayout
    def makeROIMatchingControlLayout(self):
        Layout_roimatch = QHBoxLayout()
        
        Layout_roimatch_method = QVBoxLayout()
        # Matching用のMethod
        self.dict_label["roimatch_method"] = QLabel("ROI Matching Method")
        self.dict_combobox["roimatch_method"] = QComboBox()
        self.dict_combobox["roimatch_method"].addItems(['None','multiquadric','inverse','gaussian','linear','cubic','quintic','thin_plate','affine','bspline'])
        self.dict_button["roimatch_method"] = QPushButton("ROI Match")
        self.dict_button["roimatch_method"].clicked.connect(lambda: self.ROIMatching())
        Layout_roimatch_method.addWidget(self.dict_label["roimatch_method"])
        Layout_roimatch_method.addWidget(self.dict_combobox["roimatch_method"])
        Layout_roimatch_method.addWidget(self.dict_button["roimatch_method"])
        
        Layout_roimatch_config = QVBoxLayout()
        # Elastixのconfig
        self.dict_button["config_elastix"] = QPushButton("Elastix config")
        self.dict_button["config_elastix"].clicked.connect(lambda: self.openElastixConfigWindow())
        # Matchingの結果を使ってmovのROICheckを更新
        self.dict_button["roimatch_roicheck"] = QPushButton("ROICheck Match")
        self.dict_button["roimatch_roicheck"].clicked.connect(lambda: self.ROICheckMatching())
        # ROI matching 出力
        self.dict_button["roimatch_export"] = QPushButton("Export result")
        self.dict_button["roimatch_export"].clicked.connect(lambda: self.exportROIMatchingCSV())
        Layout_roimatch_config.addWidget(self.dict_button["config_elastix"])
        Layout_roimatch_config.addWidget(self.dict_button["roimatch_roicheck"])
        Layout_roimatch_config.addWidget(self.dict_button["roimatch_export"])
        
        # rbf matchingで使用するROIのペア
        Layout_roimatch_ROIpair = QHBoxLayout()
        Layout_roimatch_ROIpair_list = QVBoxLayout()
        Layout_roimatch_ROIpair_button = QVBoxLayout()
        self.dict_label["roimatch_roipair"] = QLabel("ROI Pairs")
        self.dict_list["roimatch_roipair"] = QListWidget()
        Layout_roimatch_ROIpair_list.addWidget(self.dict_label["roimatch_roipair"])
        Layout_roimatch_ROIpair_list.addWidget(self.dict_list["roimatch_roipair"])
        for prefix, func_ in zip(["add", "remove", "clear"], [self.addROIPair, self.removeROIPair, self.clearROIPair]):
            self.dict_button[f"roimatch_roipair_{prefix}"] = QPushButton(f"{prefix} ROI pair")
            self.dict_button[f"roimatch_roipair_{prefix}"].clicked.connect(func_)
            Layout_roimatch_ROIpair_button.addWidget(self.dict_button[f"roimatch_roipair_{prefix}"])
        Layout_roimatch_ROIpair.addLayout(Layout_roimatch_ROIpair_list)
        Layout_roimatch_ROIpair.addLayout(Layout_roimatch_ROIpair_button)
        # Matching時の閾値設定
        Layout_roimatch_threshold = QVBoxLayout()
        Layout_roimatch_threshold.addWidget(QLabel("ROI Matching Threshold"))
        for key_label, value_entry in zip(["r", "error_rate"], ["5", "20%"]):
            self.dict_label[f"roimatch_thoreshold_{key_label}"] = QLabel(key_label)
            self.dict_entry[f"roimatch_thoreshold_{key_label}"] = QLineEdit(key_label)
            self.dict_entry[f"roimatch_thoreshold_{key_label}"].setText(value_entry)
            Layout_roimatch_threshold.addWidget(self.dict_label[f"roimatch_thoreshold_{key_label}"])
            Layout_roimatch_threshold.addWidget(self.dict_entry[f"roimatch_thoreshold_{key_label}"])
        
        Layout_roimatch.addLayout(Layout_roimatch_method)
        Layout_roimatch.addLayout(Layout_roimatch_config)
        Layout_roimatch.addLayout(Layout_roimatch_ROIpair)
        Layout_roimatch.addLayout(Layout_roimatch_threshold)
        return Layout_roimatch
    
    # ROI check用のLayout
    def makeROICheckLayout(self, key): # key: fix, mov
        Layout_roicheck = QVBoxLayout()
        
        # ROIの表示切り替え radiobutton
        Layout_roicheck_radiobutton = QHBoxLayout()
        self.dict_buttongroup[f"{key}_roicheck"] = QButtonGroup(self)
        self.dict_buttongroup[f"{key}_roicheck"].setExclusive(True)  # 同一グループ内で1つだけ選択可能にする
        for i, label in enumerate(["All ROI", "None", "Astrocyte", "Neuron", "Not Cell"]):
            radioButton = QRadioButton(label)
            if i == 0:
                radioButton.setChecked(True)
            Layout_roicheck_radiobutton.addWidget(radioButton)
            self.dict_buttongroup[f"{key}_roicheck"].addButton(radioButton, i)
            # ボタンが選択されたときのイベントハンドラを設定
            radioButton.toggled.connect(lambda checked, key=key, row=i, choice=label: self.onRadioButtonshowROIToggled(checked, key, row, choice))
        
        # 背景画像の切り替え meanImg, meanImgE, max_proj, Vcorr, RefImg
        Layout_roicheck_radiobutton_refimg = QHBoxLayout()
        self.dict_buttongroup[f"{key}_refimg"] = QButtonGroup(self)
        self.dict_buttongroup[f"{key}_refimg"].setExclusive(True)  # 同一グループ内で1つだけ選択可能にする
        for i, label in enumerate(["meanImg", "meanImgE", "max_proj", "Vcorr", "RefImg"]):
            radioButton = QRadioButton(label)
            if i == 0:
                radioButton.setChecked(True)
            Layout_roicheck_radiobutton_refimg.addWidget(radioButton)
            self.dict_buttongroup[f"{key}_refimg"].addButton(radioButton, i)
            # ボタンが選択されたときのイベントハンドラを設定
            radioButton.toggled.connect(lambda checked, key=key, row=i, choice=label: self.onRadioButtonshowImageToggled(checked, key, row, choice))
        
        # CheckされていないROIのcelltypeをそろえる button
        Layout_roicheck_button_setcelltype = QHBoxLayout()
        for i, (key_button, label) in enumerate(zip([f"{key}_setAstrocyte", f"{key}_setNeuron", f"{key}_setNotCell"],
                                                     ["Astrocyte", "Neuron", "Not Cell"])):
            self.dict_button[key_button] = QPushButton(label)
            self.dict_button[key_button].clicked.connect(lambda _, key=key, celltype=label: self.setAllROICelltype(key, celltype))
            Layout_roicheck_button_setcelltype.addWidget(self.dict_button[key_button])
            
        # filter用の閾値 entry, button
        Layout_roicheck_filter_threshold = QHBoxLayout()
        for param, threshold in zip(["npix", "radius", "aspect_ratio", "compact", "skew", "std"], 
                                     ["(50, 200)", "(3, 12)", "(0, 1.5)", "(0, 1.5)", "(1, 100)", "(0, 100)"]):
            Layout_roicheck_filter_threshold_entry = QVBoxLayout()
            self.dict_label[f"{key}_threshold_{param}"] = QLabel(param)
            self.dict_entry[f"{key}_threshold_{param}"] = QLineEdit(threshold)
            Layout_roicheck_filter_threshold_entry.addWidget(self.dict_label[f"{key}_threshold_{param}"])
            Layout_roicheck_filter_threshold_entry.addWidget(self.dict_entry[f"{key}_threshold_{param}"])
            Layout_roicheck_filter_threshold.addLayout(Layout_roicheck_filter_threshold_entry)
            
        # ROIのフィルタリング, ROICheckのsave, load
        Layout_roicheck_button = QHBoxLayout()
        for key_button, label, func_ in zip([f"{key}_filterROI", f"{key}_saveROICheck", f"{key}_loadROICheck"],
                                             ["Filter ROI", "Save ROICheck", "Load ROICheck"],
                                             [lambda: self.filterROICheck(key),
                                              lambda: self.saveROICheck(key),
                                              lambda: self.loadROICheck(key)]):
            self.dict_button[key_button] = QPushButton(label)
            self.dict_button[key_button].clicked.connect(func_)
            Layout_roicheck_button.addWidget(self.dict_button[key_button])
        
        Layout_roicheck.addLayout(Layout_roicheck_radiobutton)
        Layout_roicheck.addLayout(Layout_roicheck_radiobutton_refimg)
        Layout_roicheck.addLayout(Layout_roicheck_button_setcelltype)
        Layout_roicheck.addLayout(Layout_roicheck_filter_threshold)
        Layout_roicheck.addLayout(Layout_roicheck_button)
        return Layout_roicheck
    # ROIの表示のradiobutton関数  
    def onRadioButtonshowROIToggled(self, checked, key, row, choice):
        if checked: # ボタンが選択された場合
            showROI_id = row
            self.makeROIPixmap(key, showROI_id)
            self.updateImageDisplay(key)
    # reference画像表示のradiobutton関数  
    def onRadioButtonshowImageToggled(self, checked, key, row, choice):
        if checked: # ボタンが選択された場合
            key_img = self.dict_buttongroup[f"{key}_refimg"].checkedButton().text()
            if key_img == "RefImg": # optionalで指定したReference Image
                self.dict_im[key] = self.dict_im_ref[key]
            else:
                ops = self.dict_Fall[key]["ops"]
                # max_proj, Vcorrはxyサイズが異なるので注意
                if key_img in ["max_proj", "Vcorr"]:
                    im = np.zeros(self.dict_im[key].shape).astype(ops[key_img].dtype)
                    im[ops["yrange"][0][0]:ops["yrange"][0][1], ops["xrange"][0][0]:ops["xrange"][0][1]] = ops[key_img]
                else:
                    im = ops[key_img]
                im = self.convertImageToINT(im, dtype="uint16") # intに変換
                self.dict_im[key] = im
            self.updateImageDisplay(key)
            
    """
    Table Widget Function
    """
    # TableWidgetのsetup
    def setupTableWidget(self, tableWidget, key): # key: fix, mov
        tableWidget.clearSelection() # テーブルの選択初期化
        tableWidget.clear()  # テーブルの内容をクリア
        tableWidget.setRowCount(0)  # 行数を0にリセット
        list_cellid = list(self.dict_Fall[key]["stat"].keys())
        tableWidget.setRowCount(len(list_cellid))
        tableWidget.setColumnCount(8)
        cols_table = ["Cell ID", "Match\nCell ID"] + list(self.dict_celltypes.keys())

        tableWidget.setHorizontalHeaderLabels(cols_table)
        self.currently_selected_row = None  # 追加: 現在選択されている行を追跡
        for cellid in list_cellid:
            cellItem = QTableWidgetItem(f"{cellid}")
            cellItem.setFlags(cellItem.flags() & ~Qt.ItemIsEditable)  # 編集不可フラグを設定
            tableWidget.setItem(cellid, 0, cellItem)
            buttonGroup = QButtonGroup(tableWidget)
            buttonGroup.setExclusive(True)
            for label, j in self.dict_celltypes.items():
                # Astrocyte, Neuron. Not Cell
                if label not in ["Check", "Tracking", "Memo"]:
                    radioButton = QRadioButton()
                    if label == "Neuron":
                        radioButton.setChecked(True) # Neuron列はデフォルトでチェック
                    buttonGroup.addButton(radioButton, j)
                    tableWidget.setCellWidget(cellid, j, radioButton)
                # Check. Tracking
                elif label in ["Check", "Tracking"]:
                    checkBox = QTableWidgetItem()
                    checkBox.setCheckState(Qt.Unchecked)
                    tableWidget.setItem(cellid, self.dict_celltypes[label], checkBox)
                # Memo
                elif label == "Memo":
                    memoItem = QTableWidgetItem()
                    tableWidget.setItem(cellid, self.dict_celltypes["Memo"], memoItem)
        # セルの横幅指定
        for i in range(tableWidget.columnCount()):
            tableWidget.setColumnWidth(i, 60)
        # イベント設定
        tableWidget.selectionModel().selectionChanged.connect(lambda selected, deselected: self.onSelectionChanged(key, selected, deselected))
        # キーイベントハンドラを設定
        tableWidget.keyPressEvent = lambda event: self.tableWidgetKeyPressEvent(event, key)
        return tableWidget
    
    # 指定した行のcelltypeと列番号を取得する
    def getCellType(self, key, row):
        for celltype, col_table in self.dict_celltypes.items():
            cellWidget = self.dict_table[key].cellWidget(row, col_table)
            if isinstance(cellWidget, QRadioButton) and cellWidget.isChecked():
                return celltype, col_table
    
    # キーイベントのカスタム
    """
    keyPressEvent
    """
    def tableWidgetKeyPressEvent(self, event, key):
        # ROIを選択しているとき
        if not self.dict_table_selectedRow[key] is None:
            currentRow = self.dict_table_selectedRow[key] # 現在選択している行番号
            currentRows = self.dict_table[key].selectionModel().selectedRows()# 現在選択している行番号(複数)
            currentColumn = self.dict_table[key].currentColumn() # 現在選択している列番号
            # 現在の行で選択しているcelltype
            celltype, col_table = self.getCellType(key, currentRow)
            self.currentCelltype = celltype        
                
            # Astrocyte, Neuron, Not Cell, Check, Trackingのチェック
            if event.key() == Qt.Key_Z:
                self.checkROIRadioButton(key, currentRow, self.dict_celltypes["Astrocyte"])
            elif event.key() == Qt.Key_X:
                self.checkROIRadioButton(key, currentRow, self.dict_celltypes["Neuron"])
            elif event.key() == Qt.Key_C:
                self.checkROIRadioButton(key, currentRow, self.dict_celltypes["Not Cell"])
            elif event.key() == Qt.Key_V:
                self.toggleROICheckBox(key, currentRow, self.dict_celltypes["Check"])
            elif event.key() == Qt.Key_B:
                self.toggleROICheckBox(key, currentRow, self.dict_celltypes["Tracking"])
            # 行移動, U,I,O:上に移動 J,K,L:下に移動, (I,K:"Check"ありはスキップ, O,L:"Check"なしはスキップ, U,J:同じcelltypeのみ) 
            elif event.key() == Qt.Key_Down:
                self.moveSelection(key, currentRow, 1, None)
            elif event.key() == Qt.Key_Up:
                self.moveSelection(key, currentRow, -1, None)
            elif event.key() == Qt.Key_J:
                self.moveSelection(key, currentRow, 1, "same_celltype")
            elif event.key() == Qt.Key_U:
                self.moveSelection(key, currentRow, -1, "same_celltype")
            elif event.key() == Qt.Key_K:
                self.moveSelection(key, currentRow, 1, "unchecked")
            elif event.key() == Qt.Key_I:
                self.moveSelection(key, currentRow, -1, "unchecked")
            elif event.key() == Qt.Key_L:
                self.moveSelection(key, currentRow, 1, "checked")
            elif event.key() == Qt.Key_O:
                self.moveSelection(key, currentRow, -1, "checked")

        # ROIpixmapの更新 
        self.makeROIPixmap(key, self.dict_buttongroup[f"{key}_roicheck"].checkedId())
        
    # Astrocyte, Neuron, Not Cellの選択
    def checkROIRadioButton(self, key, currentRow, col_table):
        radiobutton = self.dict_table[key].cellWidget(currentRow, col_table)
        radiobutton.setChecked(True)
    # Check, TrackingのチェックON/OFF
    def toggleROICheckBox(self, key, currentRow, col_table):
        checkBoxItem = self.dict_table[key].item(currentRow, col_table)
        if checkBoxItem.checkState() == Qt.Checked:
            checkBoxItem.setCheckState(Qt.Unchecked)
        else:
            checkBoxItem.setCheckState(Qt.Checked)
    # 行移動の処理
    def moveSelection(self, key, currentRow, direction, condition):
        while True:
            currentRow += direction
            if currentRow < 0 or currentRow >= self.dict_table[key].rowCount():
                break  # テーブルの範囲外に到達したら停止
            if condition == "same_celltype":
                if self.dict_table[key].cellWidget(currentRow, self.dict_celltypes[self.currentCelltype]).isChecked():
                    self.dict_table[key].setCurrentCell(currentRow, self.dict_table[key].currentColumn())
                    return  # 同じcelltypeの行が見つかったら選択して終了
            elif condition == "unchecked":
                if self.dict_table[key].item(currentRow, self.dict_celltypes["Check"]).checkState() != Qt.Checked:
                    self.dict_table[key].setCurrentCell(currentRow, self.dict_table[key].currentColumn())
                    return  # "Check"のチェックが外れている行が見つかったら選択して終了
            elif condition == "checked":
                if self.dict_table[key].item(currentRow, self.dict_celltypes["Check"]).checkState() == Qt.Checked:
                    self.dict_table[key].setCurrentCell(currentRow, self.dict_table[key].currentColumn())
                    return  # "Check"のチェックが入っている行が見つかったら選択して終了
            else:
                self.dict_table[key].setCurrentCell(currentRow, self.dict_table[key].currentColumn())
                return
            
    # UI上のクリック、スライダーの操作等に紐づける関数
    """
    UI-Event Function
    """
    # viewのクリック時の関数
    def viewMousePressEvent(self, event, key):
        # クリックされた座標をシーンの座標系に変換
        scenePos = self.dict_view[key].mapToScene(event.pos())
        # 画像の座標系に合わせる
        imgX, imgY = int(scenePos.x()), int(scenePos.y())

        # 最も近いROIを見つける
        closestROI, minDist = None, float('inf')
        for cellid, stat_cell in self.dict_Fall[key]["stat"].items():
            centerX, centerY = stat_cell['med']
            dist = (centerX - imgX) ** 2 + (centerY - imgY) ** 2
            if dist < minDist:
                closestROI, minDist = cellid, dist

        if closestROI is not None:
            # クリックされたTableWidgetで対応するROIを選択
            self.dict_table[key].selectRow(closestROI)
            self.highlightROI(closestROI, key)

            # クリックされたTableWidgetの2列目を確認
            match_cell_id = self.dict_table[key].item(closestROI, 1)
            if match_cell_id and match_cell_id.text():
                other_key = "fix" if key == "mov" else "mov"
                match_cell_id = int(match_cell_id.text())
                if match_cell_id < 0:
                    pass
                else:
                    self.dict_table[other_key].selectRow(match_cell_id)
                    self.highlightROI(match_cell_id, other_key)
            
    # クリックしたROIをハイライトして表示
    def highlightROI(self, selected_row, key):
        # 他のROIの透明度をdict_opacityの値に戻す
        for cellid in self.dict_Fall[key]["stat"].keys():
            try:
                if cellid != selected_row:
                    self.dict_roiColors[key][cellid].setAlpha(self.dict_opacity[key])
            except:
                pass
            
        if self.dict_roiPixmapItemHighlight[key]:
            self.dict_scene[key].removeItem(self.dict_roiPixmapItemHighlight[key])
            self.dict_roiPixmapItemHighlight[key] = None

        if selected_row is not None:
            # 選択されたROIの色を取得、alpha値を255に設定して不透明にする
            color = self.dict_roiColors[key][selected_row]
            color.setAlpha(255)  # ハイライト時は不透明に

            # 選択されたROIのピクセルマップを作成
            pixmap = QPixmap(self.dict_im[key].shape[1], self.dict_im[key].shape[0])
            pixmap.fill(Qt.transparent)  # 透明で初期化
            painter = QPainter(pixmap)
            pen = QPen(color, 1)  # 保存された色でハイライト
            painter.setPen(pen)
            stat_cell_selected = self.dict_Fall[key]["stat"][selected_row]
            for x, y in zip(stat_cell_selected['xpix'], stat_cell_selected['ypix']):
                painter.drawPoint(x, y)
            painter.end()

            # ハイライトされたROIをシーンに追加
            self.dict_roiPixmapItemHighlight[key] = QGraphicsPixmapItem(pixmap)
            self.dict_scene[key].addItem(self.dict_roiPixmapItemHighlight[key])

    # TableWidgetで別のrowを選択した時の関数
    def onSelectionChanged(self, key, selected, deselected):
        indexes = selected.indexes()
        if indexes:
            selected_row = indexes[0].row()  # 選択された行番号を取得
            self.dict_table_selectedRow[key] = selected_row
            self.highlightROI(selected_row, key)
            self.makeROIPixmap(key, self.dict_buttongroup[f"{key}_roicheck"].checkedId())
            self.updateImageDisplay(key)
            self.updateSelectedCellPlot(selected_row, key)
            self.displayROIProperty(selected_row, key)

            # 選択されたTableWidgetの2列目を確認
            match_cell_id = self.dict_table[key].item(selected_row, 1)
            if match_cell_id and match_cell_id.text():
                other_key = "fix" if key == "mov" else "mov"
                match_cell_id = int(match_cell_id.text())
                if match_cell_id < 0:
                    pass
                else:
                    self.dict_table[other_key].selectRow(match_cell_id)
                    self.highlightROI(match_cell_id, other_key)
                    self.updateSelectedCellPlot(match_cell_id, other_key)
                    self.displayROIProperty(match_cell_id, other_key)

    # 選択したROIのtraceをplot
    def plotTraceOnAxis(self, selected_row, key):
        self.dict_ax[key].clear()
        trace_plot = self.dict_Fall[key]["F"][selected_row]
#         self.plot_x = np.arange(len(trace_plot)) / self.dict_Fall_ops["fs"][0][0]
        self.dict_ax[key].plot(trace_plot, color="cyan", label="raw fluor", linewidth=0.5)
    
    # trace全体の更新
    def updateSelectedCellPlot(self, selected_row, key):
        # 選択された細胞のデータをプロット
        if selected_row is not None:
            # 選択された細胞のデータを取得
            self.plotTraceOnAxis(selected_row, key)
                
        self.dict_figure[key].tight_layout()
        self.dict_canvas[key].draw()
        
#         if self.xlim:
#             self.dict_ax["top"].set_xlim(self.xlim)  # 保存された表示範囲を適用
#             self.drawPlotRangeRectangle()
            
        self.dict_canvas[key].draw_idle()
        
    # 選択したROIのpropertyを表示
    def displayROIProperty(self, selected_row, key):
        for prop in ["med", "npix", "npix_soma", "compact", "solidity", "radius", "aspect_ratio", "skew", "std"]:
            text = f"{prop}: {self.dict_Fall[key]['stat'][selected_row][prop]}"
            self.dict_label[f"{prop}_{key}"].setText(text)
            
    """
    Slider Function
    """
    def adjustContrast(self, key):
        # 画像表示を更新
        self.updateImageDisplay(key)
    def changeROIOpacity(self, key, value):
        self.dict_opacity[key] = value # 透明度の保存
        for cellid in self.dict_roiColors[key]:
            self.dict_roiColors[key][cellid].setAlpha(value)
        self.makeROIPixmap(key, self.dict_buttongroup[f"{key}_roicheck"].checkedId())
        self.updateImageDisplay(key)
        
    def clearImageItems(self, key):
        for item in self.dict_scene[key].items():
            if isinstance(item, QGraphicsPixmapItem) and item.zValue() == 0 and item is not self.dict_roiPixmapItem[key]:
                self.dict_scene[key].removeItem(item)
    """
    Scene Function
    """
    def updateImageDisplay(self, key): # key; fix, mov
        scene = self.dict_scene[key]

        # 画像をマージするための空の配列を作成
        merged_image = np.zeros((self.dict_im[key].shape[1], self.dict_im[key].shape[0], 3), dtype=np.uint8)

        # 緑チャンネルにref画像を追加
        if self.dict_checkbox[f"show_{key}_ref"].isChecked():
            green_image = self.adjustImageForDisplay(self.dict_im[key], key)
            merged_image[:, :, 1] = green_image
        else:
            self.clearImageItems(key)

        # 赤チャンネルにgrid画像を追加
        if self.dict_checkbox[f"show_{key}_grid"].isChecked():
            grid_image = self.convertGridCoordsToImage(self.dict_grid[key])
            merged_image[:, :, 0] = grid_image
            
        # fixのみ 青チャンネルにmovingのElastix変形画像を追加
        if key == "fix":
            if self.dict_checkbox[f"show_{key}_res"].isChecked():
                blue_image = self.adjustImageForDisplay(self.dict_im["res"], "res")
                merged_image[:, :, 2] = blue_image

        # QImageオブジェクトを作成して表示
        qimage = QImage(merged_image.data, merged_image.shape[1], merged_image.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.clearImageItems(key)  # 以前の画像アイテムをクリア
        pixmap_item = scene.addPixmap(pixmap)

        # ROIの画像を重ねて表示
        if self.dict_roiPixmapItem[key]:
            self.dict_scene[key].addItem(self.dict_roiPixmapItem[key])
            self.dict_roiPixmapItem[key].setZValue(1)  # ROIアイテムを前面に

        # ハイライトされたROIを再描画（現在選択されているROIがある場合）
        if self.dict_table_selectedRow[key] is not None:
            self.highlightROI(self.dict_table_selectedRow[key], key)

    def adjustImageForDisplay(self, image, key):
        # 画像のコントラストを調整し、適切な形式で返す
        min_val = self.dict_slider[f'minValue_{key}'].value()
        max_val = self.dict_slider[f'maxValue_{key}'].value()
        adjusted_image = np.clip(image, min_val, max_val)
        adjusted_image = np.interp(adjusted_image, (min_val, max_val), (0, 255))
        return adjusted_image.astype(np.uint8)
        
    def toggleImageVisibility(self, key, state, channel):
        self.updateImageDisplay(key)
        
    # ROIの色の初期設定
    def initializeROIColors(self):
        self.dict_roiColors = {"fix":{}, "mov":{}}
        for key in ["fix", "mov"]:
            for cellid in self.dict_Fall[key]["stat"].keys():
                color = QColor(np.random.randint(100, 255), np.random.randint(100, 255), np.random.randint(100, 255), self.ROIOpacity_init)
                self.dict_roiColors[key][cellid] = color
            self.dict_opacity[key] = self.ROIOpacity_init
    
    # ROI maskで作成したpixmap
    def makeROIPixmap(self, key, showROI_id=0): # key: fix, mov
        scene = self.dict_scene[key]

        # 既存のROIピクセルマップアイテムがあれば削除
        if self.dict_roiPixmapItem[key]:
            scene.removeItem(self.dict_roiPixmapItem[key])
            self.dict_roiPixmapItem[key] = None
        # ROIを描画するためのピクセルマップを作成
        pixmap = QPixmap(self.dict_im[key].shape[1], self.dict_im[key].shape[0])
        pixmap.fill(Qt.transparent)  # 透明で初期化
        painter = QPainter(pixmap)
        # 1つずつROIを描画
        for cellid, stat_cell in self.dict_Fall[key]["stat"].items():
            xpix = stat_cell["xpix"]
            ypix = stat_cell["ypix"]
            color = self.dict_roiColors[key][cellid]
            pen = QPen(color, 1)
            painter.setPen(pen)
            
            # tableWidgetでどのcelltypeを選んでいるか Astrocyte, Neuron, Not Cell
            celltype, col_table = self.getCellType(key, cellid)
            if (showROI_id == 0) or (col_table == showROI_id): # すべてのROIを表示, あるいは選択したcelltypeのみ表示
                for x, y in zip(xpix, ypix):
                    painter.drawPoint(x, y)
            elif showROI_id == 1: # すべて表示しない
                pass
        painter.end()
        self.dict_roiPixmapItem[key] = QGraphicsPixmapItem(pixmap)
        self.dict_scene[key].addItem(self.dict_roiPixmapItem[key])
        
    # Transformationをチェックする格子画像の座標を作る
    def makeGridCoords(self, width=512, height=512, square=32):
        grid_x, grid_y = [], []
        x_, y_ = np.arange(0, width), np.arange(0, height)

        for i in range(len(x_)):
            for j in range(len(y_)):
                if i % square == 0:
                    grid_x += [x_[i]]
                    grid_y += [y_[j]]
                else:
                    if j % square == 0:
                        grid_x += [x_[i]]
                        grid_y += [y_[j]]
        grid = np.array([grid_x, grid_y]).T
        return grid
    # 格子の座標を画像に変換
    def convertGridCoordsToImage(self, grid):
        im_mono = np.zeros((512, 512)).astype("int8")
        for y, x in grid:
            # 枠外の座標はスキップ
            try:
                im_mono[x, y] = 255
            except IndexError:
                pass
        return im_mono
    
    # button widgetに紐づける関数
    """
    Button-binding Function
    """
    # ダイアログを開いて選択したファイルパスをentryに入力
    def openFileDialog(self, fileFilter, entry):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Open File", "", fileFilter, options=options)
        if filePath:
            entry.setText(filePath)
    
    # 指定したファイルパスを読み込みして初期化
    def loadFilePathsandInitialize(self):
        self.initialize_gui = False
        print("Files Loading...")
        # data読み込み
        self.initializeGUI()
        self.initializeROIColors()
        # UI初期化
        if not self.setupUI_done:
            self.setupUI()
            
        # sceneとtableの更新
        for key in ["fix", "mov"]:
            self.dict_table[key] = self.setupTableWidget(self.dict_table[key], key)
            self.makeROIPixmap(key)
            self.updateImageDisplay(key)
        
        print("GUI Initializing...")
        self.initialize_gui = True
        
    # 画像をint型に変換 型は指定可能
    def convertImageToINT(self, im, dtype="uint8"):
        im = im.astype("float")
        im -= np.min(im)
        im /= np.max(im)
        im *= 255
        im = im.astype(dtype)
        return im

    # Fallをdict_Fallに変換
    def convertDictStatFromFall(self, Fall, key):
        Fall_stat = Fall["stat"]
        Fall_iscell = Fall["iscell"][:,0]
        
        dict_Fall_stat = {}

        list_ROI = []
    
        for cellid in range(len(Fall_iscell)):
            dict_Fall_stat_cell = {key:value for key, value in zip(Fall_stat[0][cellid][0].dtype.fields, Fall_stat[0][cellid][0][0])}
            # flatten
            for key, value in dict_Fall_stat_cell.items():
                dict_Fall_stat_cell[key] = value.flatten()
            xpix = dict_Fall_stat_cell["xpix"]
            ypix = dict_Fall_stat_cell["ypix"]
            center = (int(xpix.mean()), int(ypix.mean())) # ROIの中心
            dict_Fall_stat_cell["center"] = center
            dict_Fall_stat_cell["med"] = dict_Fall_stat_cell["med"][::-1] # yx -> xy
            dict_Fall_stat[cellid] = dict_Fall_stat_cell
            
        # opsの変換
        Fall_ops = Fall["ops"]
        dict_Fall_ops = {key: value for key, value in zip(Fall_ops[0].dtype.fields, Fall_ops[0][0])}

        return {"stat": dict_Fall_stat, "F": Fall["F"], "Fneu": Fall["Fneu"], "spks": Fall["spks"], "ops": dict_Fall_ops}
    
    # fix. movで選択しているROIのpairを追加, 削除, 初期化
    def addROIPair(self):
        cellid_fix, cellid_mov = self.dict_table_selectedRow["fix"], self.dict_table_selectedRow["mov"]
        pair_text = f"{cellid_fix}-{cellid_mov}"
        # Check if the pair already exists in the listbox
        if self.dict_list["roimatch_roipair"].findItems(pair_text, Qt.MatchExactly):
            return  # If the pair already exists, do not add it again
        self.dict_list["roimatch_roipair"].addItem(pair_text)
    def removeROIPair(self):
        current_item = self.dict_list["roimatch_roipair"].currentItem()
        if current_item:
            current_row = self.dict_list["roimatch_roipair"].row(current_item)
            self.dict_list["roimatch_roipair"].takeItem(current_row)
    def clearROIPair(self):
        self.dict_list["roimatch_roipair"].clear()

    # MatchingさせたROI listをcsvとして出力
    def exportROIMatchingCSV(self):
        df_roimatch = self.convertTableToDataFrame(self.dict_table["fix"])
        # 列名にFallのパスを使用
        df_roimatch.columns = [self.dict_entry[f"path_fall_{key}"].text() for key in ["fix", "mov"]]
        # fixのFall pathをもとに保存する
        path_csv = self.dict_entry[f"path_fall_fix"].text().replace("Fall_", "ROIMatch_").replace(".mat", ".csv")
        options = QFileDialog.Options()
        path_csv, _ = QFileDialog.getSaveFileName(self, "Open File", path_csv, "csv Files (*.csv);;All Files (*)", options=options)
        df_roimatch.to_csv(path_csv, index=None, encoding="shift-jis")
        if self.dict_list["roimatch_roipair"].count():
            df_roipair = self.convertListboxToDataFrame(self.dict_list["roimatch_roipair"])
            path_csv, _ = QFileDialog.getSaveFileName(self, "Open File", path_csv.replace("ROIMatch_", "ROIPair_"), "csv Files (*.csv);;All Files (*)", options=options)
            df_roipair.to_csv(path_csv, index=None, encoding="shift-jis")
    # Tableの内容をDataFrameに変換
    def convertTableToDataFrame(self, table):
        data = []
        for row in range(table.rowCount()):
            row_data = []
            for col in range(2): # Cell ID, Match Cell ID
                item = table.item(row, col)
                row_data.append(item.text())
            data.append(row_data)
        return pd.DataFrame(data)
    # ROI pairをcsvとして出力
    def convertListboxToDataFrame(self, listbox):
        data = []
        for i in range(listbox.count()):
            item_text = listbox.item(i).text()
            cellid_fix, cellid_mov = item_text.split("-")
            data.append([int(cellid_fix), int(cellid_mov)])
        return pd.DataFrame(data, columns=["fix", "mov"])
        
    # fix, mov間のROI Matching
    def ROIMatching(self):
        # ROI Matchingを同じcelltypeでのみ行うか
        reply = QMessageBox.question(self, 'ROI Matching', f'Match only ROIs with the same celltype?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        match_samecelltype = (reply == QMessageBox.Yes)
        
        listbox = self.dict_list["roimatch_roipair"]
        function = self.dict_combobox["roimatch_method"].currentText()
        # elastixでtransform: 'affine', 'bspline'
        if (function == "affine") or (function == "bspline"):
            img_fix, img_mov = self.readImageWithITK()
            img_res, result_transform_parameters = self.elastixRegistrationMethod(img_fix, img_mov, function)
            self.dict_im["res"] = img_res # Elastix変形後の画像更新
            list_ROI_center_fix_transform = self.ROITransformElastix(img_mov, result_transform_parameters, min_=0, max_=511)
            cellids_match_mov = self.ROIMatchingAlgorithmElastix(list_ROI_center_fix_transform, match_samecelltype)
            self.ROIMatchingUpdateTable(cellids_match_mov)
            
        # Transformせずそのまま
        elif function == "None":
            list_ROI_center_mov_transform = np.array([stat["med"] for cellid, stat in self.dict_Fall["mov"]["stat"].items()])
            self.dict_grid["fix"] = self.dict_grid_original["fix"]
            cellids_match_mov = self.ROIMatchingAlgorithmRBF(list_ROI_center_mov_transform, match_samecelltype)
            self.ROIMatchingUpdateTable(cellids_match_mov)
            self.dict_im["res"] = self.dict_im["mov"]
        # rbfでtransform: 'multiquadric','inverse','gaussian','linear','cubic','quintic','thin_plate'
        else:
            list_cellid_match = []
            for i in range(listbox.count()):
                cellid_fix, cellid_mov = int(listbox.item(i).text().split("-")[0]), int(listbox.item(i).text().split("-")[1])
                list_cellid_match.append([cellid_fix, cellid_mov])
            #  ROI pairが無い場合
            if len(list_cellid_match) == 0:
                return
            else:
                list_ROI_center_mov_transform = self.ROITransformRBF(list_cellid_match, function)
                cellids_match_mov = self.ROIMatchingAlgorithmRBF(list_ROI_center_mov_transform, match_samecelltype)
                self.ROIMatchingUpdateTable(cellids_match_mov)
                self.dict_im["res"] = self.dict_im["mov"]
                
        self.updateImageDisplay("fix")
        
    # fixのMatch Cell IDに相当するmovのROIのプロパティを更新する
    def ROICheckMatching(self):
        reply = QMessageBox.question(self, 'ROICheck Matching', f'Match ROICheck Properties?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for cellid_fix in range(self.dict_table["fix"].rowCount()):
                try:
                    cellid_mov = int(self.dict_table["fix"].item(cellid_fix, 1).text())
                    if cellid_mov == -1:
                        pass
                    else:
                        # celltype, check, trackingの状態を取得
                        for celltype, col_table in self.dict_celltypes.items():
                            cellWidget = self.dict_table["fix"].cellWidget(cellid_fix, col_table)
                            cellItem = self.dict_table["fix"].item(cellid_fix, col_table)
                            # Neuron, Astrocyte, Not Cellのチェック radiobuttonであるか
                            if isinstance(cellWidget, QRadioButton):
                                if cellWidget.isChecked():
                                    self.dict_table["mov"].cellWidget(cellid_mov, col_table).setChecked(True)
                            # Check, Trackingのチェック QTableWidgetItemであるか
                            elif celltype in ["Check", "Tracking"]:
                                self.dict_table["mov"].item(cellid_mov, col_table).setCheckState(cellItem.checkState())
                            # Memo
                            elif celltype == "Memo":
                                self.dict_table["mov"].item(cellid_mov, col_table).setText(cellItem.text())
                except:
                    pass
        
    # Elastix Config
    def openElastixConfigWindow(self):
        function = self.dict_combobox["roimatch_method"].currentText()
        # affine, bsplineを選んでない場合はエラー
        if function == "affine" or function == "bspline":
            self.elastix_config_window = ElastixConfigWindow(self, function)
            self.elastix_config_window.exec_()
        else:
            QMessageBox.information(self, "Elastix Config", "Select 'affine' or 'bspline'!")
            
    """
    Button-binding Function, ROI Check
    """
    # CheckされたROI以外のすべてのROIのcell typeをそろえる Astro, Neuron, Not Cell
    def setAllROICelltype(self, key, celltype):
        reply = QMessageBox.question(self, 'Set All Cells', f'Set all ROIs as {celltype}?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for row in range(self.dict_table[key].rowCount()):
                checkBox = self.dict_table[key].item(row, self.dict_celltypes["Check"]) # CheckされたROIはスキップ
                isChecked = checkBox.checkState() == Qt.Checked
                if not isChecked:
                    radioButton = self.dict_table[key].cellWidget(row, self.dict_celltypes[celltype])
                    radioButton.setChecked(True)
                                  
    # 全てのthresholdsのmin~maxに収まるROI以外をNot cellとする
    def filterROICheck(self, key):
        reply = QMessageBox.question(self, 'Filter Cells', 'Filter ROIs?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        tableWidget = self.dict_table[key]
        if reply == QMessageBox.Yes:
            # noiseとフィルタリングした行にチェックをつけるか
            reply = QMessageBox.question(self, 'Check Cells', 'Check cells determined "Not cell"?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                check = True
            else:
                check = False
            # threshold
            lists_roifilter = []
            for i, param in enumerate(["npix", "radius", "aspect_ratio", "compact", "skew", "std"]):
                threshold_range = self.dict_entry[f"{key}_threshold_{param}"].text().replace("(", "").replace(")", "").replace(" ","")
                try:
                    threshold_min, threshold_max = float(threshold_range.split(",")[0]), float(threshold_range.split(",")[1])
                    list_roi_param = [self.dict_Fall[key]["stat"][row][param] for row in self.dict_Fall[key]["stat"].keys()]
                    list_roifilter = [(roi_param >= threshold_min) and (roi_param <= threshold_max) for roi_param in list_roi_param]
                    lists_roifilter.append(list_roifilter)
                except ValueError:
                    pass

            # Cellと判定されたROI
            list_roi_cell = [all(values) for values in zip(*lists_roifilter)]
            
            for cellid, roi_cell in enumerate(list_roi_cell):
                radioButton = tableWidget.cellWidget(cellid, self.dict_celltypes["Not Cell"]) # Not Cell QRadioButtonを取得
                checkBox = tableWidget.item(cellid, self.dict_celltypes["Check"])
                if not roi_cell:
                    radioButton.setChecked(True)  # 選択状態を更新
                    if check: # チェックつけるか
                        checkBox.setCheckState(Qt.Checked)
    # Tableの内容をROICheckとして保存
    def saveROICheck(self, key):
        options = QFileDialog.Options()
        path_Fall = self.dict_entry[f"path_fall_{key}"].text()
        dir_project = path_Fall.rsplit("/", 1)[0]
        name_Fall = path_Fall.split("/")[-1].replace('Fall_', '')
        path_roicheck_init = f"{dir_project}/ROIcheck_{name_Fall}"
        path_roicheck, _ = QFileDialog.getSaveFileName(self, "Open File", path_roicheck_init, "mat Files (*.mat);;All Files (*)", options=options)
        tableWidget = self.dict_table[key]
        if path_roicheck:
            today = datetime.datetime.today().strftime('%Y-%m-%d')
            today = today.split("-")[0][2:] + today.split("-")[1] + today.split("-")[2]

            rows_selected_neuron = []
            rows_selected_astro = []
            rows_selected_noise = []
            checkStates = []
            trackingStates = []
            memoContents = []

            for row in range(tableWidget.rowCount()):
                for celltype, col_table in self.dict_celltypes.items():
                    cellWidget = tableWidget.cellWidget(row, col_table)
                    # Neuron, Astrocyte, Not Cellのチェック radiobuttonであるか
                    if isinstance(cellWidget, QRadioButton):
                        if cellWidget.isChecked():
                            if celltype.startswith("Neuron"):
                                rows_selected_neuron.append([row])
                            elif celltype.startswith("Astro"):
                                rows_selected_astro.append([row])
                            elif celltype == "Not Cell":
                                rows_selected_noise.append([row])
                checkItem = tableWidget.item(row, self.dict_celltypes["Check"])
                checkStates.append([checkItem.checkState() == Qt.Checked])
                trackingItem = tableWidget.item(row, self.dict_celltypes["Tracking"])
                trackingStates.append([trackingItem.checkState() == Qt.Checked])
                memoItem = tableWidget.item(row, self.dict_celltypes["Memo"])
                memoText = memoItem.text() if memoItem else ""
                memoContents.append([memoText])

            dict_threshold_roi = {param: self.dict_entry[f"{key}_threshold_{param}"].text() for param in ["npix", "radius", "aspect_ratio", "compact", "skew", "std"]}

            mat_roicheck = {
                "manualROIcheck": {
                    "rows_selected_neuron": np.array(rows_selected_neuron),
                    "rows_selected_astro" : np.array(rows_selected_astro),
                    "rows_selected_noise" : np.array(rows_selected_noise),
                    "update"              : today,
                    "Check"               : np.array(checkStates),
                    "Tracking"            : np.array(trackingStates),
                    "Memo"                : np.array(memoContents).astype("object"),
                    "threshold_roi"       : dict_threshold_roi,
                }
            }

            savemat(path_roicheck, mat_roicheck)
            print("ROICheck file saved!")
    # ROICheckを読み込んでTableを更新
    def loadROICheck(self, key):
        options = QFileDialog.Options()
        path_roicheck, _ = QFileDialog.getOpenFileName(self, "Open File", "", "mat Files (*.mat);;All Files (*)", options=options)
        tableWidget = self.dict_table[key]
        if path_roicheck:
            mat_roicheck = loadmat(path_roicheck)
            mat_roicheck_dtype = list(mat_roicheck["manualROIcheck"][0].dtype.fields)
            dict_roicheck = dict(zip(mat_roicheck_dtype, list(mat_roicheck["manualROIcheck"][0][0])))

            for celltype, rows in dict_roicheck.items():
                if celltype in ["rows_selected_neuron", "rows_selected_astro", "rows_selected_noise"]:
                    for row in rows:
                        if celltype == "rows_selected_neuron":
                            radioButton = tableWidget.cellWidget(row[0], self.dict_celltypes["Neuron"])
                        elif celltype == "rows_selected_astro":
                            radioButton = tableWidget.cellWidget(row[0], self.dict_celltypes["Astrocyte"])
                        elif celltype == "rows_selected_noise":
                            radioButton = tableWidget.cellWidget(row[0], self.dict_celltypes["Not Cell"])
                        radioButton.setChecked(True)
                elif celltype in ["Check", "Tracking"]:
                    for row, state in enumerate(rows):
                        checkBox = tableWidget.item(row, self.dict_celltypes[celltype])
                        checkBox.setCheckState(Qt.Checked if state[0] else Qt.Unchecked)
                elif celltype == "Memo":
                    for row, memo in enumerate(rows):
                        memoItem = tableWidget.item(row, self.dict_celltypes["Memo"])
                        try:
                            memoItem.setText(memo[0][0])
                        except IndexError:
                            pass

            print("ROICheck file loaded!")
        
    """
    rbf kernel
    """
    # ROIのtransform
    def ROITransformRBF(self, list_cellid_match, function):
        # 全ROIのcenterを投射する
        # 当てはめ元 mov
        src_coords = np.array([list(self.dict_Fall["mov"]["stat"][cellid_match[1]]["med"]) for cellid_match in list_cellid_match])
        # 当てはめ先 fix
        tgt_coords = np.array([list(self.dict_Fall["fix"]["stat"][cellid_match[0]]["med"]) for cellid_match in list_cellid_match])

        rbf_x = Rbf(src_coords[:, 0], src_coords[:, 1], tgt_coords[:, 0], function=function)
        rbf_y = Rbf(src_coords[:, 0], src_coords[:, 1], tgt_coords[:, 1], function=function)
        self.gridTransformRBF(rbf_x, rbf_y)

        list_ROI_center_fix = np.array([Fall_stat_fix["med"] for Fall_stat_fix in self.dict_Fall["fix"]["stat"].values()])
        list_ROI_center_mov = np.array([Fall_stat_mov["med"] for Fall_stat_mov in self.dict_Fall["mov"]["stat"].values()])

        list_ROI_center_mov_transform = np.column_stack((rbf_x(list_ROI_center_mov[:, 0], list_ROI_center_mov[:, 1]),
                                                         rbf_y(list_ROI_center_mov[:, 0], list_ROI_center_mov[:, 1]),))
        for cellid in self.dict_Fall["mov"]["stat"].keys():
            self.dict_Fall["mov"]["stat"][cellid]["med_transform"] = list_ROI_center_mov_transform[cellid]
        return list_ROI_center_mov_transform
    # gridのtransform
    def gridTransformRBF(self, rbf_x, rbf_y):
        # mov->fixにtransformしたgridを計算するが、表示はfix側なので注意！
        grid = self.dict_grid_original["mov"]
        grid_transform_x = rbf_x(grid[:,0], grid[:,1])
        grid_transform_y = rbf_y(grid[:,0], grid[:,1])
        self.dict_grid["fix"] = np.column_stack((grid_transform_x, grid_transform_y)).astype("int")
    # cell matching algorithm
    def ROIMatchingAlgorithmRBF(self, list_ROI_center_mov_transform, match_samecelltype=False):
        """
        1. fix ROI listから1つ取り出す(fix ROI)
        2. fix ROIのmedに半径rの円を描く
        3. 2の円内に存在するmov_transfrom ROIのmedを抽出する
        4. 3のうち、npix, npix_soma, compact, solidity, mrs, mrs0, radius, aspect_ratioの誤差率が最も小さいものとmatchさせる
        5. 4の誤差率がすべてthreshold以下出ない場合はmatchなしとする
        6. 1~5をすべてのfix ROI listに対して行う
        7. 手動で補正する機能をつけておく(重要！)
        """

        r = int(self.dict_entry["roimatch_thoreshold_r"].text())
#         keys = ["npix", "npix_soma", "compact", "solidity", "mrs", "mrs0", "radius", "aspect_ratio"]
        keys = ["npix"]
        threshold = float(self.dict_entry["roimatch_thoreshold_error_rate"].text().replace("%","")) / 100
        cellids_match_fix = list(self.dict_Fall["fix"]["stat"].keys())
        cellids_match_mov = []

        # 6
        for cellid_fix in cellids_match_fix:
            # 1
            ROI_med_fix = self.dict_Fall["fix"]["stat"][cellid_fix]["med"]
            # 2
            cellids_mov_transform_choice = []
            for cellid_mov_transform, ROI_med_mov_transform in enumerate(list_ROI_center_mov_transform):
                d = np.sqrt(np.sum(np.square(ROI_med_mov_transform - ROI_med_fix)))
                # 3
                if d < r:
                    cellids_mov_transform_choice.append(cellid_mov_transform)
            # 4 
            list_sum_diff_percent = []
            for cellid_mov_transform_choice in cellids_mov_transform_choice:
                diff_percent = [(self.dict_Fall["fix"]["stat"][cellid_fix][key] - self.dict_Fall["mov"]["stat"][cellid_mov_transform_choice][key]) / self.dict_Fall["fix"]["stat"][cellid_fix][key] for key in keys]
                sum_diff_percent = np.sum(np.abs(diff_percent))
                list_sum_diff_percent.append(sum_diff_percent)
            # 5
            if len(list_sum_diff_percent) == 0: # r内にmatchするROIがない
                cellids_match_mov.append(-1)
            else:
                cellid_match_mov = cellids_mov_transform_choice[np.argmin(list_sum_diff_percent)]
                # 同じcelltypeのROIのみMatching
                if match_samecelltype:
                    celltype_fix = self.getCellType("fix", cellid_fix)
                    celltype_mov = self.getCellType("mov", cellid_match_mov)
                    if celltype_fix == self.dict_celltypes["Not Cell"] or celltype_mov == self.dict_celltypes["Not Cell"] or celltype_fix != celltype_mov:
                        cellids_match_mov.append(-1)
                    else:
                        cellids_match_mov.append(cellid_match_mov)
                else:
                    cellids_match_mov.append(cellid_match_mov)
                
        return cellids_match_mov
        
    """
    Elastix
    """
    # itk-elastixで画像読み込み
    def readImageWithITK(self):
#         path_img_fix = self.dict_entry[f"path_tif_fix"].text()
#         path_img_mov = self.dict_entry[f"path_tif_mov"].text()
        
#         img_fix = itk.imread(path_img_fix, itk.UC)
#         img_mov = itk.imread(path_img_mov, itk.UC)
        
        img_fix = itk.image_view_from_array(self.dict_im["fix"])
        img_mov = itk.image_view_from_array(self.dict_im["mov"])
        return img_fix, img_mov
    # 画像登録の実行
    def elastixRegistrationMethod(self, img_fix, img_mov, function):
        # ElastixImageFilterの設定
        parameter_object = itk.ParameterObject.New()
        parameter_map = parameter_object.GetDefaultParameterMap(function, 4)
        # Elastix parameter上書き
        dict_parameter_map = self.dict_parameter_map[function]
        for key_parameter, value_parameter in dict_parameter_map.items():
            parameter_map[key_parameter] = value_parameter
        parameter_object.AddParameterMap(parameter_map)

        # エラーの場合はダイアログ表示
        try:
            # 画像登録の実行
            img_res, result_transform_parameters = itk.elastix_registration_method(
                img_fix, img_mov,
                parameter_object=parameter_object)
        except RuntimeError:
            QMessageBox.information(self, "Error", "Runtime Error ! Check Elastix Config !")
        return img_res, result_transform_parameters
    # 点群の投射
    def ROITransformElastix(self, img_mov, result_transform_parameters, min_=0, max_=511):
        list_ROI_center_fix = np.array([Fall_stat_fix["med"] for Fall_stat_fix in gui.dict_Fall["fix"]["stat"].values()])
        # Elastix実行用に書き込むtxtファイル
        path_txt = "./elastix/tmp_elastix_coords.txt"
        txt_content = "point\n"
        txt_content += f"{len(list_ROI_center_fix)}\n"
        for ROI_center_fix in list_ROI_center_fix:
            txt_content += f"{ROI_center_fix[0]} {ROI_center_fix[1]}\n"
        with open(path_txt, "w") as file:
            file.write(txt_content)

        list_ROI_center_fix_transform = itk.transformix_pointset(
            img_mov, result_transform_parameters,
            fixed_point_set_file_name=path_txt)[:, 27:29].astype("float").astype("int")
        # はみでたものを補正
        list_ROI_center_fix_transform[list_ROI_center_fix_transform < min_] = min_
        list_ROI_center_fix_transform[list_ROI_center_fix_transform > max_] = max_
        # 一時ファイル消去
        os.remove(path_txt)
        return list_ROI_center_fix_transform

    # gridのtransform
    def gridTransformElastix(self):
        pass

    # cell matching algorithm
    def ROIMatchingAlgorithmElastix(self, list_ROI_center_fix_transform, match_samecelltype=False):
        """
        1. fix_transform ROI listから1つ取り出す(fix_transform ROI)
        2. fix_transform ROIのmedに半径rの円を描く
        3. 2の円内に存在するmov ROIのmedを抽出する
        4. 3のうち、npix, npix_soma, compact, solidity, mrs, mrs0, radius, aspect_ratioの誤差率が最も小さいものとmatchさせる
        5. 4の誤差率がすべてthreshold以下出ない場合はmatchなしとする
        6. 1~5をすべてのfix ROI listに対して行う
        7. 手動で補正する機能をつけておく(重要！)
        """

        r = int(self.dict_entry["roimatch_thoreshold_r"].text())
#         keys = ["npix", "npix_soma", "compact", "solidity", "mrs", "mrs0", "radius", "aspect_ratio"]
        keys = ["npix"]
        threshold = float(self.dict_entry["roimatch_thoreshold_error_rate"].text().replace("%","")) / 100
        cellids_match_fix = list(self.dict_Fall["fix"]["stat"].keys())
        cellids_match_mov = []
        
        list_ROI_center_mov = np.array([stat["med"] for cellid, stat in self.dict_Fall["mov"]["stat"].items()])

        # 6
        for cellid_fix in cellids_match_fix:
            # 1
            ROI_med_fix_transform = list_ROI_center_fix_transform[cellid_fix]
            # 2
            cellids_mov_choice = []
            for cellid_mov, ROI_med_mov in enumerate(list_ROI_center_mov):
                d = np.sqrt(np.sum(np.square(ROI_med_mov - ROI_med_fix_transform)))
                # 3
                if d < r:
                    cellids_mov_choice.append(cellid_mov)
            # 4 
            list_sum_diff_percent = []
            for cellid_mov_choice in cellids_mov_choice:
                diff_percent = [(self.dict_Fall["fix"]["stat"][cellid_fix][key] - self.dict_Fall["mov"]["stat"][cellid_mov_choice][key]) / self.dict_Fall["fix"]["stat"][cellid_fix][key] for key in keys]
                sum_diff_percent = np.sum(np.abs(diff_percent))
                list_sum_diff_percent.append(sum_diff_percent)
            # 5
            if len(list_sum_diff_percent) == 0: # r内にmatchするROIがない
                cellids_match_mov.append(-1)
            else:
                if np.min(list_sum_diff_percent) > threshold: # 誤差率が閾値以上
                    cellids_match_mov.append(-1)
                else:
                    cellid_mov_match = cellids_mov_choice[np.argmin(list_sum_diff_percent)]
                    if match_samecelltype:
                        celltype_fix = self.getCellType("fix", cellid_fix)
                        celltype_mov = self.getCellType("mov", cellid_mov_match)
                        if celltype_fix == self.dict_celltypes["Not Cell"] or celltype_mov == self.dict_celltypes["Not Cell"] or celltype_fix != celltype_mov:
                            cellids_match_mov.append(-1)
                        else:
                            cellids_match_mov.append(cellid_mov_match)
                    else:
                        cellids_match_mov.append(cellid_mov_match)
                
        return cellids_match_mov

    # Matching後のcellidでfixのTableを更新
    def ROIMatchingUpdateTable(self, cellids_match_mov):
        for cellid in range(self.dict_table["fix"].rowCount()):
            item = QTableWidgetItem(str(cellids_match_mov[cellid]))
            self.dict_table["fix"].setItem(cellid, 1, item)
        
    def exitApp(self):
        self.close()
        
if __name__ == "__main__":
    # フォント揃え
    restored_font = QFont()
    restored_font.fromString("MS UI Gothic,9,-1,5,50,0,0,0,0,0")
    app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()
    QApplication.setFont(restored_font)
    gui = Suite2pROITrackingGUI()
    gui.show()
    sys.exit(app.exec_())