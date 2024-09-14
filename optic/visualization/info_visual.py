from typing import Dict, Any

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