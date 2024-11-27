from __future__ import annotations
from ..type_definitions import *
import os
from PyQt5.QtWidgets import QMessageBox, QDialog
from scipy.io import loadmat, savemat
import tifffile
import datetime
import numpy as np
from ..gui.table_setup import applyDictROICheckToTable
from ..preprocessing.preprocessing_fall import convertMatToDictFall, convertMatToDictROICheck
from ..preprocessing.preprocessing_image import getBGImageFromFall, convertImageDtypeToINT
from ..preprocessing.preprocessing_table import convertTableDataToDictROICheck, convertDictROICheckToMatROICheck, convertMatROICheckToDictROICheck, convertTableDataToDictROITracking, convertDictROITrackingToMatROITracking
from ..preprocessing.preprocessing_tiff import standardizeTIFFStack
from .file_dialog import openFileDialog, saveFileDialog

# load Fall.mat data
def loadFallMat(
        path_fall       : str, 
        preprocessing   : bool=True
        ) -> Dict[str, Any]:
    Fall = loadmat(path_fall)
    if preprocessing:
        dict_Fall = convertMatToDictFall(Fall)
    else:
        dict_Fall = Fall
    return dict_Fall

def saveTifImage(
        q_widget        : QWidget,
        path_dst        : str,
        im              : np.array[Any, Any, Any]
        ) -> None:
    path_dst, is_overwrite = saveFileDialog(q_widget=q_widget, file_type="tif", title="Save TIF image file", initial_dir=path_dst)
    tifffile.imsave(path_dst, im)

# load tif image data (XYC)
def loadTifImage(
        path_image      : str, 
        preprocessing   : bool=True
        ) -> np.array:
    im = tifffile.imread(path_image)
    if preprocessing:
        im = convertImageDtypeToINT(im)
    return im

# save tiff stack data (TZCYX)
def saveTiffStack(
        q_widget        : QWidget,
        path_dst        : str,
        tiff_stack      : np.array[Any, Any, Any, Any, Any],
        imagej          : bool=True,
        metadata        : Dict[str, Any] = None
        ) -> None:
    # To save as ImageJ format, move axes to the last
    path_dst, is_overwrite = saveFileDialog(q_widget=q_widget, file_type="tif", title="Save TIFF image stack file", initial_dir=path_dst)
    if path_dst:
        if imagej:
            data_ijformat = np.moveaxis(tiff_stack, [0,1,2,3,4], [4,3,2,1,0])
            tifffile.imwrite(path_dst, data_ijformat, imagej=imagej, metadata=metadata)
        else:
            tifffile.imwrite(path_dst, tiff_stack)
    else:
        return

# load tiff stack data (XYCZT)
def loadTiffStack(
        path_tiff       : str, 
        preprocessing   : bool=True, 
        axes_tgt        : str="XYCZT"
        ) -> np.ndarray:
    if path_tiff:
        if preprocessing:
            with tifffile.TiffFile(path_tiff) as tif:
                series = tif.series[0]
                axes_src = series.axes
                im = standardizeTIFFStack(series.asarray(), axes_src, axes_tgt)
                metadata = tif.imagej_metadata
        else:
            im = tifffile.imread(path_tiff)
            metadata = None
        return im, metadata
    else:
        return

# EventFile npyの読み込み, 初期化
def loadEventFileNPY(
        q_window        : QMainWindow, 
        data_manager    : DataManager, 
        control_manager : ControlManager, 
        app_key         : str
        ) -> None | np.array:
    path_eventfile = openFileDialog(q_widget=q_window, file_type="npy", title="Open Eventfile npy File").replace("\\", "/")

    if path_eventfile:
        eventfile = np.load(path_eventfile)
        len_eventfile = len(eventfile)
        len_Fall = data_manager.getLengthOfData(app_key)
        eventfile_name = path_eventfile.split("/")[-1].split(".")[0]
        control_manager.setSharedAttr(app_key, "eventfile_name", eventfile_name)
        if not len_eventfile == len_Fall:
            QMessageBox.warning(q_window, "File load failed", f"Length of data does not match! \nFall: {len_Fall}, eventfile: {len_eventfile}")
            return None
        else:
            data_manager.dict_eventfile[app_key] = eventfile
            return data_manager.dict_eventfile[app_key]
    else:
        return

# 保存用のファイルパス作成, 初期位置も指定
def generateSavePath(
        path_src        : str, 
        prefix          : str="", 
        suffix          : str="", 
        new_extension   : str=None, 
        remove_strings  : str=None
        ) -> str:
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

# save table content as ROIcheck.mat
def saveROICheck(
        q_window        : QMainWindow, 
        q_lineedit      : QLineEdit, 
        q_table         : QTableWidget, 
        gui_defaults    : GuiDefaults,
        table_columns   : TableColumns,
        json_config     : JsonConfig, 
        local_var       : bool=True
        ) -> None:
    path_src = q_lineedit.text()
    path_dst = generateSavePath(path_src, prefix="ROIcheck_", remove_strings="Fall_")
    path_dst, is_overwrite = saveFileDialog(q_widget=q_window, file_type="mat", title="Save ROIcheck mat File", initial_dir=path_dst)
    
    if path_dst:
        try:
            from ..dialog.user_select import UserSelectDialog
            dialog = UserSelectDialog(parent=q_window, gui_defaults=gui_defaults, json_config=json_config)
            if dialog.exec_() == QDialog.Accepted:
                dialog.getUser()
                user = dialog.user
            now = f"save_{datetime.datetime.now().strftime('%y%m%d_%H%M%S')}"
            if is_overwrite:
                mat_roicheck = loadmat(path_dst, simplify_cells=True)
                dict_roicheck = convertTableDataToDictROICheck(q_table, table_columns, local_var)
                mat_roicheck = convertDictROICheckToMatROICheck(
                    dict_roicheck,
                    mat_roicheck=mat_roicheck,
                    date=now,
                    user=user
                    )
            else:
                dict_roicheck = convertTableDataToDictROICheck(q_table, table_columns, local_var)
                mat_roicheck = convertDictROICheckToMatROICheck(
                    dict_roicheck,
                    date=now,
                    user=user,
                    n_roi=q_table.rowCount(),
                    path_fall=path_src,
                    )
            savemat(path_dst, mat_roicheck)
            QMessageBox.information(q_window, "File save", f"ROICheck file saved!\nuser: {user}, date: {now}")
        except Exception as e:
            QMessageBox.warning(q_window, "File save failed", f"Error saving ROICheck file: {e}")

# load ROIcheck.mat
def loadROICheck(
        q_window        : QMainWindow, 
        q_table         : QTableWidget, 
        gui_defaults    : GuiDefaults,
        table_columns   : TableColumns,
        table_control   : TableControl,
        ) -> Union[Dict[str, Any], None]:
    path_roicheck = openFileDialog(q_widget=q_window, file_type="mat", title="Open ROIcheck mat File")
    if path_roicheck:
        try:
            mat_roicheck = loadmat(path_roicheck, simplify_cells=True)
            # check number of ROIs between of Fall file and of ROICheck file
            if table_control.len_row != mat_roicheck["NumberOfROI"]:
                QMessageBox.warning(q_window, "File load failed", f"Length of data does not match! \nTable: {table_control.len_row}, ROICheck: {mat_roicheck['NumberOfROI']}")
                return

            from ..dialog.date_select import DateSelectDialog
            list_date = list(mat_roicheck["manualROIcheck"].keys())
            dialog = DateSelectDialog(parent=q_window, gui_defaults=gui_defaults, list_date=list_date)
            if dialog.exec_() == QDialog.Accepted:
                date = dialog.date
            
            # select saved date
            dict_roicheck = mat_roicheck["manualROIcheck"][date]
            
            applyDictROICheckToTable(q_table, table_columns, dict_roicheck)
            QMessageBox.information(q_window, "File load", "ROICheck file loaded!")
        except Exception as e:
            QMessageBox.warning(q_window, "File load failed", f"Error loading ROICheck file: {e}")

# save table content as ROITracking.mat
def saveROITracking(
        q_window         : QMainWindow, 
        q_lineedit_pri   : QLineEdit, 
        q_lineedit_sec   : QLineEdit,
        q_table_pri      : QTableWidget, 
        q_table_sec      : QTableWidget,
        gui_defaults     : GuiDefaults,
        table_column_pri : TableColumns,
        table_column_sec : TableColumns,
        json_config      : JsonConfig, 
        local_var        : bool=False
        ) -> None:
    path_src_pri = q_lineedit_pri.text()
    path_src_sec = q_lineedit_sec.text()
    path_dst = generateSavePath(path_src_pri, prefix="ROItracking_", remove_strings="Fall_")
    path_dst, is_overwrite = saveFileDialog(q_widget=q_window, file_type="mat", title="Save ROItracking mat File", initial_dir=path_dst)
    
    if path_dst:
        try:
            from ..dialog.user_select import UserSelectDialog
            dialog = UserSelectDialog(parent=q_window, gui_defaults=gui_defaults, json_config=json_config)
            if dialog.exec_() == QDialog.Accepted:
                dialog.getUser()
                user = dialog.user
            now = f"save_{datetime.datetime.now().strftime('%y%m%d_%H%M%S')}"
            if is_overwrite:
                mat_roi_tracking = loadmat(path_dst, simplify_cells=True)
                dict_roi_tracking_pri = convertTableDataToDictROITracking(q_table_pri, table_column_pri, local_var)
                dict_roi_check_sec = convertTableDataToDictROICheck(q_table_sec, table_column_sec)
                mat_roi_tracking = convertDictROITrackingToMatROITracking(
                    dict_roi_tracking_pri,
                    dict_roi_check_sec,
                    mat_roi_tracking=mat_roi_tracking,
                    date=now,
                    user=user
                    )
            else:
                dict_roi_tracking_pri = convertTableDataToDictROITracking(q_table_pri, table_column_pri, local_var)
                print(dict_roi_tracking_pri.keys())
                print(dict_roi_tracking_pri["Cell ID"])
                dict_roi_check_sec = convertTableDataToDictROICheck(q_table_sec, table_column_sec)
                mat_roi_tracking = convertDictROITrackingToMatROITracking(
                    dict_roi_tracking_pri,
                    dict_roi_check_sec,
                    date=now,
                    user=user,
                    n_roi_pri=q_table_pri.rowCount(),
                    n_roi_sec=q_table_sec.rowCount(),
                    path_fall_pri=path_src_pri,
                    path_fall_sec=path_src_sec
                    )
            
            savemat(path_dst, mat_roi_tracking)
            QMessageBox.information(q_window, "File save", f"ROI Tracking file saved!\nuser: {user}, date: {now}")
        except Exception as e:
            raise e
            # QMessageBox.warning(q_window, "File save failed", f"Error saving ROI Tracking file: {e}")

# load ROITracking.mat
def loadROITracking(
        
):
    pass