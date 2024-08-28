# データの読み込み用関数
import os
from PyQt5.QtWidgets import QMessageBox
from scipy.io import loadmat
import tifffile
import datetime
from ..preprocessing.preprocessing_fall import convertMatToDictFall, convertMatToDictROICheck
from ..preprocessing.preprocessing_image import convertImageDtypeToINT, resizeImageShape
from ..preprocessing.preprocessing_table import convertTableDataToDictROICheck, convertDictROICheckToMatROICheck
from .file_dialog import openFileDialog, saveFileDialog

# Fallの読み込み, メッセージ付き
def loadFallMAT(q_window, data_manager, key_dict_Fall, path_fall, preprocessing=True):
    try:
        Fall = loadmat(path_fall)
        if preprocessing:
            dict_Fall = convertMatToDictFall(Fall)
            data_manager.dict_Fall[key_dict_Fall] = dict_Fall
        else:
            data_manager.dict_Fall[key_dict_Fall] = Fall
        QMessageBox.information(q_window, "File load", "File loaded!")
        return data_manager.dict_Fall[key_dict_Fall]
    except FileNotFoundError as e:
        QMessageBox.warning(q_window, "File Not Found", str(e))
        return False

# tif imageの読み込み
def loadTIFImage(data_manager, key_dict_im, path_image, preprocessing=True):
    im = tifffile.imread(path_image)
    data_manager.dict_im[key_dict_im] = im
    return data_manager.dict_im[key_dict_im]

# EventFile npyの読み込み, 初期化
def loadEventFileNPY(widget_manager, path_npy):
    pass

def clearEventFileNPY(widget_manager):
    pass


# 保存用のファイルパス作成, 初期位置も指定
def generateSavePath(path_src, prefix="", suffix="", new_extension=None, remove_strings=None):
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
def saveROICheck(q_window, q_table, data_manager, dict_tablecol, path_roicheck, local_var=True):


    options = QFileDialog.Options()
    path_Fall = self.dict_lineedit[f"path_fall_{key}"].text()
    dir_project = os.path.dirname(path_Fall)
    name_Fall = os.path.basename(path_Fall).replace('Fall_', '')
    path_roicheck_init = os.path.join(dir_project, f"ROIcheck_{name_Fall}")
    path_roicheck, _ = QFileDialog.getSaveFileName(self, "Save ROI Check", path_roicheck_init, "mat Files (*.mat);;All Files (*)", options=options)
    if path_roicheck:
        try:
            dict_roicheck = convertTableDataToDictROICheck(q_table, dict_tablecol, local_var)
            mat_roicheck = convertDictROICheckToMatROICheck(dict_roicheck)
            savemat(path_roicheck, mat_roicheck)
            QMessageBox.information(q_window, "File save", "ROICheck file saved!")
        except Exception as e:
            QMessageBox.warning(q_window, "File save failed", f"Error saving ROICheck file: {e}")



# ROICheckを読み込んでTableを更新
def loadROICheck(self, key):
    options = QFileDialog.Options()
    path_Fall = self.dict_lineedit[f"path_fall_{key}"].text()
    dir_project = os.path.dirname(path_Fall)
    path_roicheck = openFileDialog(self, file_type="mat", title="Open Fall.mat File", initial_dir=dir_project)
    if path_roicheck:
        try:
            mat_roicheck = loadmat(path_roicheck)
            mat_roicheck = mat_roicheck["manualROIcheck"]
            dict_roicheck = convertMatToDictROICheck(mat_roicheck)

            tableWidget = self.dict_table[key]
            roi_count = tableWidget.rowCount()

            cell_type_keys = {
                "rows_selected_neuron": "Neuron",
                "rows_selected_astro": "Astrocyte",
                "rows_selected_noise": "Not Cell"
            }

            # ラジオボタンの設定
            for col_name, col_info in self.dict_tablecol.items():
                if col_info['type'] == 'radio':
                    if col_name in dict_roicheck:
                        selected_rows = dict_roicheck[col_name]
                        for row in range(roi_count):
                            radio_button = tableWidget.cellWidget(row, col_info['order'])
                            if radio_button:
                                radio_button.setChecked(any(row == sr[0] for sr in selected_rows))
                    elif col_name in cell_type_keys.values():
                        corresponding_key = [k for k, v in cell_type_keys.items() if v == col_name][0]
                        if corresponding_key in dict_roicheck:
                            selected_rows = dict_roicheck[corresponding_key]
                            for row in range(roi_count):
                                radio_button = tableWidget.cellWidget(row, col_info['order'])
                                if radio_button:
                                    radio_button.setChecked(any(row == sr[0] for sr in selected_rows))

            # チェックボックスと文字列の設定
            for col_name, col_info in self.dict_tablecol.items():
                if col_info['type'] in ['checkbox', 'string']:
                    if col_name in dict_roicheck:
                        data = dict_roicheck[col_name]
                        for row in range(min(roi_count, len(data))):
                            item = tableWidget.item(row, col_info['order'])
                            if item:
                                if col_info['type'] == 'checkbox':
                                    item.setCheckState(Qt.Checked if data[row][0] else Qt.Unchecked)
                                else:  # string
                                    # 空のリストや空の文字列を空白として処理
                                    value = str(data[row][0])
                                    if value == '[]' or value == '':
                                        value = ''
                                    item.setText(value)

            # threshold_roi の設定
            if 'threshold_roi' in dict_roicheck:
                threshold_roi_dict = convertMatToDictFall(dict_roicheck["threshold_roi"])
                for param in ["npix", "radius", "aspect_ratio", "compact", "skew", "std"]:
                    if param in threshold_roi_dict:
                        self.dict_lineedit[f"threshold_{param}"].setText(str(threshold_roi_dict[param][0]))

            self.updateView(key)
            self.displayROINumber(key)
            print("ROICheck file loaded!")
        except Exception as e:
            print(f"Error loading ROICheck file: {e}")
            raise  # This will re-raise the exception for debugging purposes