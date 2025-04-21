from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QTableWidgetItem
from ..visualization.info_visual import updateROICountDisplay
from ..visualization.view_visual_roi import shouldSkipROI

class TableHandler:
    """
    Handler class responsible for table event processing
    Separates event handling logic from TableControl
    """
    def __init__(self, table_control: TableControl):
        self.table_control = table_control
        self.app_key = table_control.app_key
        self.key_function_map = table_control.key_function_map
        self.data_manager = table_control.data_manager
        self.config_manager = table_control.config_manager
        self.widget_manager = table_control.widget_manager
        self.control_manager = table_control.control_manager
        
    def handleKeyPress(self, event: QKeyEvent) -> None:
        """
        Handle key press events
        Execute actions based on KEY_FUNCTION_MAP in gui_defaults
        """
        if self.table_control.selected_row is not None and event.key() in self.key_function_map:
            action = self.key_function_map[event.key()]
            self.executeAction(action)
            self.table_control.q_table.setCurrentCell(
                self.table_control.selected_row, 
                self.table_control.selected_column
            )
            self.table_control.q_table.scrollToItem(
                self.table_control.q_table.item(
                    self.table_control.selected_row, 
                    self.table_control.selected_column
                )
            )

    def executeAction(self, action: Tuple) -> None:
        """
        Execute the action corresponding to a key operation
        """
        action_type = action[0]  # radio, checkbox, move, row
        if action_type == 'move':
            move_type = action[1]  # cell_type, skip_roi, selected_type, up/down/left/right
            step = action[2]
            self.moveCell(move_type, step) 
        elif action_type == 'toggle':
            col_order = action[1]
            self.toggleColumn(self.table_control.selected_row, col_order)
        elif action_type == 'roi_match':
            self.setSelectedROIMatch()
        updateROICountDisplay(self.widget_manager, self.config_manager, self.app_key)

    def moveCell(self, move_type: str, step: Literal[-1, 1]) -> None:
        """
        Process table cell movement
        """
        table_control = self.table_control
        if move_type == 'up':
            table_control.selected_row = max(0, table_control.selected_row - step)
        elif move_type == 'down':
            table_control.selected_row = min(table_control.q_table.rowCount() - 1, table_control.selected_row + step)
        elif move_type == 'left':
            table_control.selected_column = max(0, table_control.selected_column - step)
        elif move_type == 'right':
            table_control.selected_column = min(table_control.q_table.columnCount() - 1, table_control.selected_column + step)
        elif move_type == 'cell_type':
            self.moveToSameCellType(table_control.selected_row, step)
        elif move_type == 'skip_roi':
            self.moveSkippingROI(table_control.selected_row, step)
        elif move_type == 'selected_type':
            self.moveToSelectedType(table_control.selected_row, step)

    def toggleColumn(self, row: int, col_order: int) -> None:
        """
        Toggle radio button or checkbox states
        """
        table_control = self.table_control
        for col_name, col_info in table_control.table_columns.getColumns().items():
            if col_info['order'] == col_order:
                if col_info['type'] == 'celltype':
                    button_group = table_control.groups_celltype.get(row)
                    if button_group:
                        for button in button_group.buttons():
                            if table_control.q_table.cellWidget(row, col_order) == button:
                                button.setChecked(True)
                                table_control.changeRadiobuttonOfTable(row)
                                # update data_manager.dict_roi_celltype
                                self.data_manager.dict_roi_celltype[self.app_key][row] = col_name
                                break
                elif col_info['type'] == 'checkbox':
                    check_box_item = table_control.q_table.item(row, col_order)
                    if check_box_item:
                        check_box_item.setCheckState(
                            Qt.Unchecked if check_box_item.checkState() == Qt.Checked else Qt.Checked
                        )
                break

    def moveToSameCellType(self, start_row: int, direction: Literal[-1, 1]) -> None:
        """
        Move to the next/previous cell with the same cell type
        """
        table_control = self.table_control
        current_cell_type = table_control.getCurrentCellTypeOfRow(start_row)
        total_rows = table_control.q_table.rowCount()
        new_row = start_row

        while True:
            new_row = (new_row + direction) % total_rows
            if new_row == start_row:
                break
            if table_control.getCurrentCellTypeOfRow(new_row) == current_cell_type:
                table_control.selected_row = new_row
                return
            
    def moveSkippingROI(self, start_row: int, direction: Literal[-1, 1]) -> None:
        """
        Move to find ROIs that don't match the skip condition
        """
        table_control = self.table_control
        total_rows = table_control.q_table.rowCount()
        new_row = start_row

        while True:
            new_row = (new_row + direction) % total_rows
            if new_row == start_row:
                break

            # Select ROI if it's not skipped
            if not shouldSkipROI(
                roi_id=new_row,
                table_columns=table_control.table_columns,
                q_table=table_control.q_table,
                skip_roi_types=table_control.control_manager.getSharedAttr(self.app_key, "skip_roi_types")
            ):
                table_control.selected_row = new_row
                return
            
    def moveToSelectedType(self, start_row: int, direction: Literal[-1, 1]) -> None:
        """
        Move to the next/previous ROI of the selected type
        """
        table_control = self.table_control
        dict_roi_display = table_control.getSharedAttr_DictROIDisplay()
        total_rows = table_control.q_table.rowCount()
        new_row = start_row

        while True:
            new_row = (new_row + direction) % total_rows
            if new_row == start_row:
                break
            if dict_roi_display[new_row]:
                table_control.selected_row = new_row
                return
            
    def setSelectedROIMatch(self) -> None:
        """
        Set the currently selected ROI in sec view as match for the selected ROI in pri view
        """
        # hardcoded !!!
        table_control_pri = self.control_manager.table_controls["pri"]
        table_control_sec = self.control_manager.table_controls["sec"]

        # get roi_selected_id of "sec" table
        sec_roi_id = self.control_manager.getSharedAttr("sec", "roi_selected_id")
        if sec_roi_id is None:
            return
            
        # get column of "id_match"
        id_match_col_order = None
        for col_name, col_info in table_control_pri.table_columns.getColumns().items():
            if col_info['type'] == 'id_match':
                id_match_col_order = col_info['order']
                break
                
        if id_match_col_order is None:
            return
            
        # get roi_selected_id of "pri" table
        pri_row = table_control_pri.selected_row
        if pri_row is None:
            return
            
        # update "ROI Match ID"
        item = QTableWidgetItem(str(sec_roi_id))
        table_control_pri.q_table.setItem(pri_row, id_match_col_order, item)
        
        # update dict_roi_matching["match"]
        pri_roi_id = table_control_pri.getCellIdFromRow(pri_row)
        if pri_roi_id is not None:
            pri_plane_t = table_control_pri.getPlaneT()
            sec_plane_t = table_control_sec.getPlaneT()
            
            if pri_plane_t in self.data_manager.dict_roi_matching["match"] and \
               sec_plane_t in self.data_manager.dict_roi_matching["match"][pri_plane_t]:
                self.data_manager.dict_roi_matching["match"][pri_plane_t][sec_plane_t][pri_roi_id] = sec_roi_id
        
        # update view
        for app_key in self.control_manager.view_controls:
            self.control_manager.view_controls[app_key].updateView()

    
    # def removeSelectedRow(self) -> None:
    #     """
    #     Remove the selected row (used mainly in MICROGLIA_TRACKING)
    #     """
    #     table_control = self.table_control
    #     current_row = table_control.selected_row
        
    #     if current_row is not None:
    #         # Get ROI ID to be removed
    #         roi_id = table_control.getCellIdFromRow(current_row)
    #         if roi_id is not None:
    #             # Remove ROI from display
    #             roi_display = table_control.getSharedAttr_DictROIDisplay()
    #             if roi_id in roi_display:
    #                 del roi_display[roi_id]
    #                 table_control.setSharedAttr_DictROIDisplay(roi_display)
                
    #             # Remove row from table
    #             table_control.q_table.removeRow(current_row)
    #             table_control.setLenRow(table_control.q_table.rowCount())
                
    #             # Get plane T and remove corresponding data
    #             plane_t = table_control.getPlaneT()
                
    #             # Remove from dict_roi_matching and dict_roi_coords_xyct
    #             data_manager = table_control.data_manager
    #             if roi_id in data_manager.dict_roi_matching["id"][plane_t]:
    #                 data_manager.dict_roi_matching["id"][plane_t].remove(roi_id)
                
    #             if plane_t in data_manager.dict_roi_coords_xyct and roi_id in data_manager.dict_roi_coords_xyct[plane_t]:
    #                 del data_manager.dict_roi_coords_xyct[plane_t][roi_id]
                
    #             # Update selected row
    #             if current_row >= table_control.q_table.rowCount():
    #                 table_control.selected_row = table_control.q_table.rowCount() - 1
    #             else:
    #                 table_control.selected_row = current_row
                
    #             print(f"ROI {roi_id} is removed.")
                
    #             # Update views
    #             control_manager = table_control.control_manager
    #             for app_key in control_manager.view_controls:
    #                 control_manager.view_controls[app_key].updateView()