from ..config.constants_local import ROICheckMatKeysLocal
import datetime
import numpy as np
from PyQt5.QtCore import Qt

# Tableの内容をdict_roicheckに保管
def convertTableDataToDictROICheck(q_table, table_columns, local_var=True):
    if local_var:
        cell_type_keys = ROICheckMatKeysLocal.cell_type_keys # ローカル変数
    
    dict_roicheck = {}
    row_count = q_table.rowCount()
    # 列ごとに処理
    for col_name, col_info in table_columns.items():
        if col_info['type'] == 'radio':
            selected_rows = []
            for row in range(row_count):
                radio_button = q_table.cellWidget(row, col_info['order'])
                if radio_button and radio_button.isChecked():
                    selected_rows.append([row])

            dict_roicheck[col_name] = np.array(selected_rows, dtype=np.int32)

            if local_var:
                if col_name in cell_type_keys:
                    dict_roicheck[cell_type_keys[col_name]] = np.array(selected_rows, dtype=np.int32)
        
        elif col_info['type'] == 'checkbox':
            dict_roicheck[col_name] = np.zeros((row_count, 1), dtype=np.bool_)
            for row in range(row_count):
                item = q_table.item(row, col_info['order'])
                dict_roicheck[col_name][row] = item.checkState() == Qt.Checked if item else False
        
        elif col_info['type'] == 'string':
            dict_roicheck[col_name] = np.empty((row_count, 1), dtype=object)
            for row in range(row_count):
                item = q_table.item(row, col_info['order'])
                dict_roicheck[col_name][row] = item.text() if item else ''

    # 更新日付
    today = datetime.datetime.today().strftime('%y%m%d')
    dict_roicheck["update"] = today
    return dict_roicheck

# dict_roicheck -> mat_roicheck
def convertDictROICheckToMatROICheck(dict_roicheck):
    mat_roicheck = {
    "manualROIcheck": {
        **dict_roicheck,
    }
}
    return mat_roicheck

# mat_roicheck -> dict_roicheck
def convertMatROICheckToDictROICheck(mat_roicheck):
    mat_roicheck = mat_roicheck["manualROIcheck"]
    mat_dtype = list(mat_roicheck[0].dtype.fields)
    dict_roicheck = {}
    for key_, value_ in zip(mat_dtype, list(mat_roicheck[0][0])):
        if value_.dtype=="object":
            value_ = np.array([[x[0].item() if x[0].size > 0 else ""] for x in value_])
        dict_roicheck[key_] = value_
    return dict_roicheck