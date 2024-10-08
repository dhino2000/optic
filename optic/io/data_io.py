from __future__ import annotations
from ..type_definitions import *
import os
from PyQt5.QtWidgets import QMessageBox
from scipy.io import loadmat, savemat
import tifffile
import datetime
import numpy as np
from ..gui.table_setup import applyDictROICheckToTable
from ..preprocessing.preprocessing_fall import convertMatToDictFall, convertMatToDictROICheck
from ..preprocessing.preprocessing_image import getBGImageFromFall, convertImageDtypeToINT
from ..preprocessing.preprocessing_table import convertTableDataToDictROICheck, convertDictROICheckToMatROICheck, convertMatROICheckToDictROICheck
from .file_dialog import openFileDialog, saveFileDialog

# Fallの読み込み, メッセージ付き
def loadFallMATWithGUI(q_window: QMainWindow, data_manager: DataManager, key_app: str, path_fall: str) -> bool:
    success = data_manager.loadFallMAT(key_app, path_fall)
    if success:
        QMessageBox.information(q_window, "File load", "File loaded successfully!")
        return True
    else:
        QMessageBox.warning(q_window, "File Load Error", "Failed to load the file.")
        return False

# load tif image data (XYC)
def loadTifImage(path_image: str, preprocessing: bool=True) -> np.array:
    im = tifffile.imread(path_image)
    im = convertImageDtypeToINT(im)
    return im

# load tiff stack data (XYZCT)
def loadTiffStack(path_tiff: str, preprocessing: bool=True) -> bool:
    im = tifffile.imread(path_tiff)
    return im

# EventFile npyの読み込み, 初期化
def loadEventFileNPY(q_window: QMainWindow, data_manager: DataManager, control_manager: ControlManager, key_app: str) -> None | np.array:
    path_eventfile = openFileDialog(q_widget=q_window, file_type="npy", title="Open Eventfile npy File").replace("\\", "/")

    if path_eventfile:
        eventfile = np.load(path_eventfile)
        len_eventfile = len(eventfile)
        len_Fall = data_manager.getLengthOfData(key_app)
        eventfile_name = path_eventfile.split("/")[-1].split(".")[0]
        control_manager.setSharedAttr(key_app, "eventfile_name", eventfile_name)
        if not len_eventfile == len_Fall:
            QMessageBox.warning(q_window, "File load failed", f"Length of data does not match! \nFall: {len_Fall}, eventfile: {len_eventfile}")
            return None
        else:
            data_manager.dict_eventfile[key_app] = eventfile
            return data_manager.dict_eventfile[key_app]
    else:
        return

# 保存用のファイルパス作成, 初期位置も指定
def generateSavePath(path_src: str, prefix: str="", suffix: str="", new_extension: str=None, remove_strings: str=None) -> str:
    """
    元のファイルパスを基に、新しい保存パスを生成する。

    :param path_src: 元のファイルパス
    :param prefix: 新しいファイル名の接頭辞
    :param suffix: 新しいファイル名の接尾辞
    :param new_extension: 新しい拡張子（指定しない場合は元の拡張子を使用）
    :param remove_strings: 元のファイル名から除去する文字列または文字列のリスト
    :return: 生成された保存パス
    """
    dir_src = os.path.dirname(path_src)
    name_ext_src =  os.path.basename(path_src)
    name_src, ext_src = os.path.splitext(name_ext_src)

    # 指定された文字列を除去
    if remove_strings:
        if isinstance(remove_strings, str):
            remove_strings = [remove_strings]
        for s in remove_strings:
            name_src = name_src.replace(s, '')

    name_dst = f"{prefix}{name_src}{suffix}"

    # 新しい拡張子が指定されている場合は使用、そうでなければ元の拡張子を使用
    ext_dst = new_extension if new_extension else ext_src

    name_ext_dst = f"{name_dst}{ext_dst}"
    path_dst = os.path.join(dir_src, name_ext_dst).replace("\\", "/")
    return path_dst

# Tableの内容をROICheckとして保存
def saveROICheck(q_window: QMainWindow, q_lineedit: QLineEdit, q_table: QTableWidget, table_columns: TableColumns, local_var: bool=True) -> None:
    path_src = q_lineedit.text()
    path_dst = generateSavePath(path_src, prefix="ROIcheck_", remove_strings="Fall_")
    path_dst = saveFileDialog(q_widget=q_window, file_type="mat", title="Save ROIcheck mat File", initial_dir=path_dst)
    if path_dst:
        try:
            dict_roicheck = convertTableDataToDictROICheck(q_table, table_columns, local_var)
            mat_roicheck = convertDictROICheckToMatROICheck(dict_roicheck)
            savemat(path_dst, mat_roicheck)
            QMessageBox.information(q_window, "File save", "ROICheck file saved!")
        except Exception as e:
            QMessageBox.warning(q_window, "File save failed", f"Error saving ROICheck file: {e}")

# ROICheckを読み込んでTableを更新
def loadROICheck(q_window: QMainWindow, q_table: QTableWidget, table_columns: TableColumns, table_control: TableControl) -> None:
    path_roicheck = openFileDialog(q_widget=q_window, file_type="mat", title="Open ROIcheck mat File")
    if path_roicheck:
        try:
            dict_roicheck = convertMatROICheckToDictROICheck(loadmat(path_roicheck))
            # if table_control.len_row != len(dict_roicheck):
            #     QMessageBox.warning(q_window, "File load failed", f"Length of data does not match! \nTable: {table_control.len_row}, ROICheck: {len(dict_roicheck)}")
            #     return
            applyDictROICheckToTable(q_table, table_columns, dict_roicheck)
            QMessageBox.information(q_window, "File load", "ROICheck file loaded!")
        except Exception as e:
            QMessageBox.warning(q_window, "File load failed", f"Error loading ROICheck file: {e}")