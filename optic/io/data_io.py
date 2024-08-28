# データの読み込み用関数
from PyQt5.QtWidgets import QMessageBox
from scipy.io import loadmat
import tifffile
import datetime
from ..preprocessing.preprocessing_fall import convertMatToDictFall, convertMatToDictROICheck
from ..preprocessing.preprocessing_image import convertImageDtypeToINT, resizeImageShape

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




# Tableの内容をROICheckとして保存
def saveROICheck(data_manager):
    options = QFileDialog.Options()
    path_Fall = self.dict_lineedit[f"path_fall_{key}"].text()
    dir_project = os.path.dirname(path_Fall)
    name_Fall = os.path.basename(path_Fall).replace('Fall_', '')
    path_roicheck_init = os.path.join(dir_project, f"ROIcheck_{name_Fall}")
    path_roicheck, _ = QFileDialog.getSaveFileName(self, "Save ROI Check", path_roicheck_init, "mat Files (*.mat);;All Files (*)", options=options)
    if path_roicheck:
        try:
            tableWidget = self.dict_table[key]
            today = datetime.datetime.today().strftime('%y%m%d')

            cell_type_keys = ROICheckMatKeysLocal.cell_type_keys

            data_to_save = {}
            roi_count = tableWidget.rowCount()

            for col_name, col_info in self.dict_tablecol.items():
                if col_info['type'] == 'radio':
                    selected_rows = []
                    for row in range(roi_count):
                        radio_button = tableWidget.cellWidget(row, col_info['order'])
                        if radio_button and radio_button.isChecked():
                            selected_rows.append([row])

                    data_to_save[col_name] = np.array(selected_rows, dtype=np.int32)
                    if col_name in cell_type_keys:
                        data_to_save[cell_type_keys[col_name]] = np.array(selected_rows, dtype=np.int32)
                elif col_info['type'] == 'checkbox':
                    data_to_save[col_name] = np.zeros((roi_count, 1), dtype=np.bool_)
                    for row in range(roi_count):
                        item = tableWidget.item(row, col_info['order'])
                        data_to_save[col_name][row] = item.checkState() == Qt.Checked if item else False
                elif col_info['type'] == 'string':
                    data_to_save[col_name] = np.empty((roi_count, 1), dtype=object)
                    for row in range(roi_count):
                        item = tableWidget.item(row, col_info['order'])
                        data_to_save[col_name][row] = item.text() if item else ''

            threshold_roi = {param: self.dict_lineedit[f"threshold_{param}"].text() for param in ["npix", "radius", "aspect_ratio", "compact", "skew", "std"]}
            
            mat_roicheck = {
                "manualROIcheck": {
                    **data_to_save,
                    "update": today,
                    "threshold_roi": threshold_roi,
                }
            }
            savemat(path_roicheck, mat_roicheck)
            print("ROICheck file saved!")
        except Exception as e:
            print(f"Error saving ROICheck file: {e}")
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