from typing import Dict, Any, List
from collections import Counter

# Display Selected ROI Property
def updateROIPropertyDisplay(control_manager, data_manager, widget_manager, key_app: str):
    selected_roi_id = control_manager.getSharedAttr(key_app, 'selected_roi_id')
    if selected_roi_id is None:
        return

    roi_properties = getRoiProperties(data_manager, key_app, selected_roi_id)
    displayRoiProperties(widget_manager, key_app, roi_properties)

def getRoiProperties(data_manager, key_app: str, roi_id: int) -> Dict[str, Any]:
    roi_stat = data_manager.dict_Fall[key_app]["stat"][roi_id]
    properties = ["med", "npix", "npix_soma", "radius", "aspect_ratio", 
                  "compact", "solidity", "footprint", "skew", "std"]
    
    return {prop: roi_stat.get(prop, "N/A") for prop in properties}

def displayRoiProperties(widget_manager, key_app: str, properties: Dict[str, Any]):
    for prop, value in properties.items():
        label_key = f"{key_app}_roi_prop_{prop}"
        if label_key in widget_manager.dict_label:
            if prop == "med":
                value_str = f"({value[0]}, {value[1]})"
            else:
                scalar_value = value.item() if hasattr(value, 'item') else value
                if isinstance(scalar_value, int):
                    value_str = f"{scalar_value}"
                elif isinstance(scalar_value, float):
                    value_str = f"{scalar_value:.2f}"
                else:
                    value_str = str(scalar_value)
            widget_manager.dict_label[label_key].setText(f"{prop}: {value_str}")

# Display Celltype Count
def updateROICountDisplay(widget_manager, config_manager, key_app: str):
    roi_counts = countROIs(config_manager, widget_manager, key_app)
    displayROICounts(widget_manager, key_app, roi_counts)

def countROIs(config_manager, widget_manager, key_app: str) -> Dict[str, int]:
    table_columns = config_manager.getTableColumns(key_app).getColumns()
    celltype_columns = [col_name for col_name, col_info in table_columns.items() if col_info['type'] == 'celltype']

    roi_counts = Counter()
    total_rois = 0

    q_table = widget_manager.dict_table[key_app]
    for row in range(q_table.rowCount()):
        total_rois += 1
        for col_name in celltype_columns:
            col_index = table_columns[col_name]['order']
            radio_button = q_table.cellWidget(row, col_index)
            if radio_button and radio_button.isChecked():
                roi_counts[col_name] += 1
                break
        else:
            roi_counts["Unclassified"] += 1

    roi_counts["All"] = total_rois

    return dict(roi_counts)

def displayROICounts(widget_manager, key_app: str, roi_counts: Dict[str, int]):
    for celltype, count in roi_counts.items():
        label_key = f"{key_app}_roicount_{celltype}"
        if label_key in widget_manager.dict_label:
            widget_manager.dict_label[label_key].setText(f"{celltype}: {count}")