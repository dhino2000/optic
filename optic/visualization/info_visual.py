from __future__ import annotations
from ..type_definitions import *
from collections import Counter

# Display Z,T plane number
def updateZPlaneDisplay(widget_manager: WidgetManager, app_key: str, z: int) -> None:
    label_key = f"{app_key}_plane_z"
    if label_key in widget_manager.dict_label:
        widget_manager.dict_label[label_key].setText(f"Z: {z}")
def updateTPlaneDisplay(widget_manager: WidgetManager, app_key: str, t: int) -> None:
    label_key = f"{app_key}_plane_t"
    if label_key in widget_manager.dict_label:
        widget_manager.dict_label[label_key].setText(f"T: {t}")

# Display Selected ROI Property
def updateROIPropertyDisplay(control_manager: ControlManager, data_manager: DataManager, widget_manager: WidgetManager, app_key: str) -> None:
    roi_selected_id = control_manager.getSharedAttr(app_key, 'roi_selected_id')
    if roi_selected_id is None:
        return

    roi_properties = getRoiProperties(data_manager, app_key, roi_selected_id)
    displayRoiProperties(widget_manager, app_key, roi_properties)

def getRoiProperties(data_manager: DataManager, app_key: str, roi_id: int) -> Dict[str, Any]:
    roi_stat = data_manager.getStat(app_key)[roi_id]
    properties = ["med", "npix", "npix_soma", "radius", "aspect_ratio", 
                  "compact", "solidity", "footprint", "skew", "std"]
    
    return {prop: roi_stat.get(prop, "N/A") for prop in properties}

def displayRoiProperties(widget_manager: WidgetManager, app_key: str, properties: Dict[str, Any]) -> None:
    for prop, value in properties.items():
        label_key = f"{app_key}_roi_prop_{prop}"
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
def updateROICountDisplay(widget_manager: WidgetManager, config_manager: ConfigManager, app_key: str) -> None:
    roi_counts = countROIs(config_manager, widget_manager, app_key)
    displayROICounts(widget_manager, app_key, roi_counts)

def countROIs(config_manager: ConfigManager, widget_manager: WidgetManager, app_key: str) -> Dict[str, int]:
    table_columns = config_manager.getTableColumns(app_key).getColumns()
    celltype_columns = [col_name for col_name, col_info in table_columns.items() if col_info['type'] == 'celltype']

    roi_counts = {col_name: 0 for col_name in celltype_columns}
    roi_counts["Unclassified"] = 0
    total_rois = 0

    q_table = widget_manager.dict_table[app_key]
    for row in range(q_table.rowCount()):
        total_rois += 1
        classified = False
        for col_name in celltype_columns:
            col_index = table_columns[col_name]['order']
            radio_button = q_table.cellWidget(row, col_index)
            if radio_button and radio_button.isChecked():
                roi_counts[col_name] += 1
                classified = True
                break
        if not classified:
            roi_counts["Unclassified"] += 1

    roi_counts["All"] = total_rois

    return roi_counts

def displayROICounts(widget_manager: WidgetManager, app_key: str, roi_counts: Dict[str, int]) -> None:
    for celltype, count in roi_counts.items():
        if celltype not in ["Unclassified", "All"]:  # まず celltype のみ表示
            label_key = f"{app_key}_roicount_{celltype}"
            if label_key in widget_manager.dict_label:
                widget_manager.dict_label[label_key].setText(f"{celltype}: {count}")
    
    # "Unclassified" と "All" を最後に表示
    for special_type in ["Unclassified", "All"]:
        if special_type in roi_counts:
            label_key = f"{app_key}_roicount_{special_type}"
            if label_key in widget_manager.dict_label:
                widget_manager.dict_label[label_key].setText(f"{special_type}: {roi_counts[special_type]}")