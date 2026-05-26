import os
import sys
from functools import partial
from itertools import combinations

dir_notebook = os.path.dirname(os.path.abspath("__file__"))
dir_parent = os.path.dirname(dir_notebook)
if not dir_parent in sys.path:
    sys.path.append(dir_parent)

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QApplication, QMessageBox, QDialog, QTableWidgetItem
)
from optic.config.constants import BGImageTypeList, Extension, AccessURL
from optic.controls.view_control import ViewControl
from optic.controls.table_control import TableControl
from optic.dialog.table_columns_config import TableColumnConfigDialog
from optic.dialog.elastix_params_config import ElastixParamsConfigDialog
from optic.dialog.load_multi_fall import LoadMultiFallDialog
from optic.gui.app_setup import setupMainWindow
from optic.gui.app_style import applyAppStyle
from optic.gui.slider_layouts import makeLayoutContrastSlider, makeLayoutOpacitySlider
from optic.gui.io_layouts import (
    makeLayoutLoadFileExitHelp, makeLayoutROICurationIO, makeLayoutROITrackingIO
)
from optic.gui.info_layouts import makeLayoutROIProperty
from optic.gui.processing_image_layouts import makeLayoutMultiSessionFallRegistration, makeLayoutManualRegistration
from optic.gui.processing_roi_layouts import makeLayoutROIMatching
from optic.gui.table_layouts import makeLayoutTableROICountLabel
from optic.gui.view_layouts import (
    makeLayoutViewWithZTSlider, makeLayoutWidgetDislplayCelltype,
    makeLayoutWidgetDislplayCheckbox, makeLayoutWidgetBGImageTypeDisplay,
    makeLayoutWidgetROIChooseSkip
)
from optic.manager import WidgetManager, ConfigManager, DataManager, ControlManager, LayoutManager, initManagers
from optic.gui.bind_func import (
    bindFuncExit, bindFuncHelp,
    bindFuncRadiobuttonBGImageTypeChanged, bindFuncComboboxBGImageChannelChanged,
    bindFuncCheckBoxDisplayCelltypeChanged, bindFuncCheckBoxDisplayCheckBoxChanged,
    bindFuncCheckBoxROIChooseSkip,
    bindFuncRadiobuttonOfTableChanged, bindFuncCheckboxOfTableChanged,
    bindFuncTableSelectionChangedWithTracking,
    bindFuncOpacitySlider, bindFuncHighlightOpacitySlider,
    bindFuncBackgroundContrastSlider, bindFuncBackgroundVisibilityCheckbox,
    bindFuncViewEvents, bindFuncROICurationIO,
    bindFuncCheckboxShowMatchedROI, bindFuncCheckboxShowROIPair,
    bindFuncROIPairOpacitySlider,
    bindFuncCheckboxShowRegisteredBGImage, bindFuncCheckboxShowRegisteredROIImage,
    bindFuncButtonRunElastixForMultiSessionFall, bindFuncButtonRunManualRegistration,
    bindFuncRegisteredROIAndBGImageIO,
    bindFuncButtonRunROIMatchingForXYCT, bindFuncButtonClearROIMatching,
    bindFuncMultiSessionTrackingIO,
    bindFuncIDMatchOfTableChanged,
    bindFuncButtonGenerateMasterTrackingTable,
)
from optic.visualization.info_visual import updateROICountDisplay
from optic.utils.layout_utils import clearLayout


class OpticROITrackingMultiGUI(QMainWindow):
    def __init__(self):
        APP_NAME = "OPTIC_ROI_TRACKING_MULTI"
        QMainWindow.__init__(self)
        self.widget_manager, self.config_manager, self.data_manager, self.control_manager = initManagers(
            WidgetManager(), ConfigManager(), DataManager(), ControlManager()
        )
        self.config_manager.setCurrentApp(APP_NAME)
        self.app_keys = self.config_manager.gui_defaults["APP_KEYS"]
        self.n_sessions = 0
        self.list_path_fall = []
        # Per-session ROI curation snapshot: {app_key: {plane_t: dict_curation}}.
        # Lets celltype / checkbox / memo edits (and loaded ROICuration) survive session switches.
        self._curation_cache = {}
        # The (t_pri, t_sec) pair currently rendered in the pri table's Cell_ID_Match column.
        # Used to defensively sync manual id_match edits back into dict_roi_matching before any rebuild.
        self._displayed_pair = None

        self.setupUI_done = False
        setupMainWindow(self, self.config_manager.gui_defaults)
        self.initUI()

    """
    setup UI Functions
    """
    def initUI(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout_main = QGridLayout(self.central_widget)

        self.layout_file_load = QHBoxLayout()
        self.setupFileLoadUI()
        self.layout_main.addLayout(self.layout_file_load, 1, 0, 1, 1)

        self.layout_main_ui = QGridLayout()
        self.layout_main.addLayout(self.layout_main_ui, 0, 0, 1, 2)

        self.layout_extra_ui = QHBoxLayout()
        self.layout_main.addLayout(self.layout_extra_ui, 1, 1, 1, 1)

    def setupFileLoadUI(self):
        file_load_widget = QWidget()
        layout = QVBoxLayout(file_load_widget)
        layout.addLayout(self.makeLayoutSectionBottom())
        self.bindFuncFileLoadUI()
        self.layout_file_load.addWidget(file_load_widget)

    def loadFilePathsAndInitialize(self):
        """Show LoadMultiFallDialog, load sessions, build main UI."""
        dialog = LoadMultiFallDialog(self.config_manager.gui_defaults, parent=self)
        if not dialog.exec_():
            return
        self.n_sessions = dialog.plane_t
        self.list_path_fall = [
            dialog.widget_manager.dict_lineedit[f"path_fall_t{t}"].text()
            for t in range(self.n_sessions)
        ]

        # Re-init managers so a second load starts fresh
        self.control_manager, self.data_manager = initManagers(self.control_manager, self.data_manager)

        success = self.loadData()
        if success:
            QMessageBox.information(self, "File load", f"Loaded {self.n_sessions} sessions successfully!")
            self.setupMainUI()
        else:
            QMessageBox.warning(self, "File Load Error", "Failed to load one or more Fall.mat files.")

    def setupMainUI(self):
        if self.setupUI_done:
            clearLayout(self.layout_main_ui)
            clearLayout(self.layout_extra_ui)

        self.setupMainUILayouts()
        self.setupControls()
        self.initializeDataControlForMultiSession()
        self.bindFuncAllWidget()
        self.updateInitialView()
        self.setupUI_done = True

    def loadData(self):
        """Load each Fall.mat into XYCT dicts and redirect pri/sec app_key slots."""
        success = True
        for t, path_fall in enumerate(self.list_path_fall):
            ok, e = self.data_manager.loadFallMatMultiSession(plane_t=t, path_fall=path_fall)
            if not ok:
                print(f"[loadData] session {t} failed: {e}")
                success = False
        return success

    def setupMainUILayouts(self):
        self.layout_main_ui.addLayout(self.makeLayoutSectionLeftUpper(), 0, 0, 1, 1)
        self.layout_main_ui.addLayout(self.makeLayoutSectionRightUpper(), 0, 1, 1, 1)
        self.layout_extra_ui.addLayout(self.makeLayoutSectionBottomExtra())

    def setupControls(self):
        """Create TableControl (ROI table) and ViewControl for each app_key."""
        for app_key in self.app_keys:
            self.control_manager.table_controls[app_key] = TableControl(
                app_key=app_key,
                q_table=self.widget_manager.dict_table[app_key],
                data_manager=self.data_manager,
                widget_manager=self.widget_manager,
                config_manager=self.config_manager,
                control_manager=self.control_manager,
            )
            self.control_manager.table_controls[app_key].setupWidgetROITable(app_key)

            self.control_manager.view_controls[app_key] = ViewControl(
                app_key=app_key,
                q_view=self.widget_manager.dict_view[app_key],
                q_scene=self.widget_manager.dict_scene[app_key],
                data_manager=self.data_manager,
                widget_manager=self.widget_manager,
                config_manager=self.config_manager,
                control_manager=self.control_manager,
                app_key_sec=self.app_keys[1] if app_key == self.app_keys[0] else None,
            )
            self.control_manager.view_controls[app_key].setViewSize()
            self.control_manager.initializeSkipROITypes(app_key, self.control_manager.table_controls[app_key].table_columns)

        # Path lineedits for per-session ROICuration IO (hidden; auto-updated on T change)
        for t, app_key in enumerate(self.app_keys):
            self.widget_manager.makeWidgetLineEdit(key=f"path_fall_{app_key}", text_set=self.list_path_fall[t] if t < self.n_sessions else "")

        # Set sec panel to session 1 initially
        self.widget_manager.dict_slider[f"{self.app_keys[1]}_plane_t"].setValue(1)
        self.control_manager.view_controls[self.app_keys[1]].setPlaneT(1)
        # Switch sec's underlying data to session 1
        self.data_manager.switchSessionForAppKey(self.app_keys[1], 1)
        # Sync roi_colors for sec session 1
        vc_sec = self.control_manager.view_controls[self.app_keys[1]]
        vc_sec.roi_colors = dict(vc_sec.roi_colors_xyct.get(1, {}))
        # Reload sec table with session-1 data
        self.control_manager.table_controls[self.app_keys[1]].setupWidgetROITable(self.app_keys[1])
        self.control_manager.initializeSkipROITypes(self.app_keys[1], self.control_manager.table_controls[self.app_keys[1]].table_columns)
        # Update sec path lineedit
        if self.n_sessions > 1:
            self.widget_manager.dict_lineedit[f"path_fall_{self.app_keys[1]}"].setText(self.list_path_fall[1])

    def initializeDataControlForMultiSession(self):
        """
        Initialize dict_roi_matching and roi_colors_xyct for all sessions.
          dict_roi_matching["id"][t]          = [roi_id, ...]
          dict_roi_matching["match"][t0][t1]  = {roi_id: None, ...}  (pre-filled, unmatched)
          roi_colors_xyct[t][roi_id]          = random color
        """
        for plane_t in range(self.n_sessions):
            roi_coords_t = self.data_manager.dict_roi_coords_xyct.get(plane_t, {})
            roi_ids = list(roi_coords_t.keys())
            self.data_manager.dict_roi_matching["id"][plane_t] = roi_ids
            for app_key in self.app_keys:
                self.control_manager.view_controls[app_key].initializeROIColorsXYCT(plane_t)

        for plane_pri, plane_sec in combinations(range(self.n_sessions), 2):
            if plane_pri not in self.data_manager.dict_roi_matching["match"]:
                self.data_manager.dict_roi_matching["match"][plane_pri] = {}
            roi_ids_pri = self.data_manager.dict_roi_matching["id"].get(plane_pri, [])
            self.data_manager.dict_roi_matching["match"][plane_pri][plane_sec] = {
                roi_id: None for roi_id in roi_ids_pri
            }

    def switchSession(self, app_key: str, plane_t: int) -> None:
        """Switch app_key to session plane_t: redirect data, reload table, rebind, update view."""
        # 0a. Sync pri table's Cell_ID_Match column into dict_roi_matching for whatever pair
        #     the table is currently displaying (tracked via self._displayed_pair). Defensive
        #     against missed itemChanged signals — preserves manual match edits.
        self._syncIdMatchToDict()
        # 0. Snapshot the current table's curation before we leave this session, so it can be
        #    restored when the user navigates back (otherwise setupWidgetROITable resets it to iscell).
        old_plane_t = self.control_manager.view_controls[app_key].getPlaneT()
        if old_plane_t != plane_t:
            self._captureCuration(app_key, old_plane_t)
        # 1. Redirect data_manager's per-app_key dicts to new session
        self.data_manager.switchSessionForAppKey(app_key, plane_t)
        # 2. Ensure ROI colors are initialized for this session
        self.control_manager.view_controls[app_key].initializeROIColorsXYCT(plane_t)
        # Sync roi_colors with current session for updateLayerROI_OpticROITracking
        vc = self.control_manager.view_controls[app_key]
        vc.roi_colors = dict(vc.roi_colors_xyct.get(plane_t, {}))
        # 3. Update view_control's T
        self.control_manager.view_controls[app_key].setPlaneT(plane_t)
        self.control_manager.view_controls[app_key].setSharedAttr_ROISelected(None)
        # 4. Reset skip ROI types
        self.control_manager.initializeSkipROITypes(
            app_key, self.control_manager.table_controls[app_key].table_columns
        )
        # 5. Update path lineedit so ROICuration IO works on the right file
        if plane_t < len(self.list_path_fall):
            self.widget_manager.dict_lineedit[f"path_fall_{app_key}"].setText(self.list_path_fall[plane_t])
        # 6. Rebuild table with new session's ROI data (defaults celltype from iscell)
        self.control_manager.table_controls[app_key].setupWidgetROITable(app_key)
        # 6b. Re-apply any curation snapshot saved for this session (overrides iscell defaults).
        self._restoreCuration(app_key, plane_t)
        # 6c. Re-apply the 'Display Cells' side-panel filter so only selected celltypes/checkboxes show.
        self._reapplyDisplayFilters(app_key)
        # 7. Update Cell_ID_Match column (only meaningful for pri)
        if app_key == self.app_keys[0]:
            t_sec = self.control_manager.view_controls[self.app_keys[1]].getPlaneT()
            self._updateMatchColumn(plane_t, t_sec)
        # 8. Re-bind table radiobutton/checkbox callbacks (widgets were recreated)
        bindFuncRadiobuttonOfTableChanged(
            table_control=self.control_manager.table_controls[app_key],
            view_control=self.control_manager.view_controls[app_key],
        )
        bindFuncCheckboxOfTableChanged(
            table_control=self.control_manager.table_controls[app_key],
            view_control=self.control_manager.view_controls[app_key],
        )
        # id_match column edit handler (pri only)
        if app_key == self.app_keys[0]:
            bindFuncIDMatchOfTableChanged(
                table_control=self.control_manager.table_controls[app_key],
                view_control=self.control_manager.view_controls[app_key],
                control_manager=self.control_manager,
                data_manager=self.data_manager,
            )
        # 9. Update ROI count label
        updateROICountDisplay(self.widget_manager, self.config_manager, app_key)
        # 10. Render
        self.control_manager.view_controls[app_key].updateView()

    def _reapplyDisplayFilters(self, app_key: str) -> None:
        """Re-apply the side-panel 'Display Cells' checkbox state to dict_roi_display.
        setupWidgetROITable resets dict_roi_display to all-True, but the side-panel
        checkbox widgets keep their previous state — we need to push that state back
        into dict_roi_display so the view only renders the ROIs the user selected."""
        tc = self.control_manager.table_controls[app_key]
        columns = self.config_manager.table_columns[app_key].getColumns()
        celltype_names = {c for c, info in columns.items() if info['type'] == 'celltype'}
        checkbox_names = {c for c, info in columns.items() if info['type'] == 'checkbox'}
        dict_celltype_visibility = {}
        dict_checkbox_visibility = {}
        for key, qcb in self.widget_manager.dict_checkbox.items():
            if app_key not in key:
                continue
            if 'celltype_roi_display_' in key:
                name = key.split('celltype_roi_display_')[-1]
                if name in celltype_names:
                    dict_celltype_visibility[name] = qcb.isChecked()
            elif 'checkbox_roi_display_' in key:
                name = key.split('checkbox_roi_display_')[-1]
                if name in checkbox_names:
                    dict_checkbox_visibility[name] = qcb.isChecked()
        if dict_celltype_visibility:
            tc.updateROIDisplayWithCelltype(dict_celltype_visibility)
        if dict_checkbox_visibility:
            tc.updateROIDisplayWithCheckbox(dict_checkbox_visibility)

    def _syncIdMatchToDict(self) -> None:
        """Push the pri table's current Cell_ID_Match column values into dict_roi_matching
        for the pair the table currently displays (tracked via self._displayed_pair).
        Defensive sync against any uncommitted edit / missed itemChanged signal."""
        if self._displayed_pair is None:
            return
        t_pri, t_sec = self._displayed_pair
        pri_key = self.app_keys[0]
        table_columns = self.config_manager.table_columns[pri_key]
        q_table = self.widget_manager.dict_table[pri_key]
        if q_table.rowCount() == 0:
            return
        match_col_idx = None
        id_col_idx = None
        for col_name, col_info in table_columns.getColumns().items():
            if col_info['type'] == 'id_match':
                match_col_idx = col_info['order']
            elif col_info['type'] == 'id':
                id_col_idx = col_info['order']
        if match_col_idx is None or id_col_idx is None:
            return
        match_dict = self.data_manager.dict_roi_matching.setdefault('match', {}).setdefault(t_pri, {}).setdefault(t_sec, {})
        for row in range(q_table.rowCount()):
            id_item = q_table.item(row, id_col_idx)
            if id_item is None:
                continue
            try:
                roi_id_pri = int(id_item.text())
            except ValueError:
                continue
            match_item = q_table.item(row, match_col_idx)
            text = match_item.text().strip() if match_item is not None else ''
            if text == '':
                match_dict[roi_id_pri] = None
            else:
                try:
                    match_dict[roi_id_pri] = int(text)
                except ValueError:
                    pass  # keep prior value on parse error

    def _captureCuration(self, app_key: str, plane_t: int) -> None:
        """Snapshot the current table's celltype / checkbox / string columns for a session."""
        from optic.preprocessing.preprocessing_table import convertTableDataToDictROICuration
        tc = self.control_manager.table_controls[app_key]
        q_table = self.widget_manager.dict_table[app_key]
        if q_table.rowCount() == 0:
            return
        self._curation_cache.setdefault(app_key, {})[plane_t] = (
            convertTableDataToDictROICuration(q_table, tc.table_columns)
        )

    def _restoreCuration(self, app_key: str, plane_t: int) -> None:
        """Re-apply a previously snapshotted curation for a session, if one exists."""
        dict_curation = self._curation_cache.get(app_key, {}).get(plane_t)
        if dict_curation is None:
            return
        from optic.gui.table_setup import applyDictROICurationToTable
        tc = self.control_manager.table_controls[app_key]
        q_table = self.widget_manager.dict_table[app_key]
        applyDictROICurationToTable(q_table, tc.table_columns, dict_curation)

    def _updateMatchColumn(self, t_pri: int, t_sec: int) -> None:
        """Fill Cell_ID_Match column of pri table from dict_roi_matching["match"][t_pri][t_sec].
        Also records (t_pri, t_sec) as self._displayed_pair so future _syncIdMatchToDict()
        writes back to the correct dict entry."""
        self._displayed_pair = (t_pri, t_sec)
        app_key = self.app_keys[0]
        table_columns = self.config_manager.table_columns[app_key]
        q_table = self.widget_manager.dict_table[app_key]

        match_col_idx = None
        for col_name, col_info in table_columns.getColumns().items():
            if col_info['type'] == 'id_match':
                match_col_idx = col_info['order']
                break
        if match_col_idx is None:
            return

        match_data = self.data_manager.dict_roi_matching.get("match", {}).get(t_pri, {}).get(t_sec, {})
        q_table.blockSignals(True)
        for row in range(q_table.rowCount()):
            id_item = q_table.item(row, 0)
            if id_item is None:
                continue
            try:
                roi_id = int(id_item.text())
            except ValueError:
                continue
            matched_id = match_data.get(roi_id)
            match_item = QTableWidgetItem()
            if matched_id is not None:
                match_item.setText(str(matched_id))
            q_table.setItem(row, match_col_idx, match_item)
        q_table.blockSignals(False)

    def updateInitialView(self):
        """Render both panels and update ROI count labels after initial load."""
        for app_key in self.app_keys:
            updateROICountDisplay(self.widget_manager, self.config_manager, app_key)
            self.control_manager.view_controls[app_key].updateView()
        t_pri = self.control_manager.view_controls[self.app_keys[0]].getPlaneT()
        t_sec = self.control_manager.view_controls[self.app_keys[1]].getPlaneT()
        self._updateMatchColumn(t_pri, t_sec)

    """
    makeLayout Functions: Component
    """
    "Left / Right Upper"
    def makeLayoutComponentROIView(self, app_key):
        layout = makeLayoutViewWithZTSlider(
            self.widget_manager,
            app_key,
            slider_z=False,
            slider_t=True,
            key_label_t=f"{app_key}_plane_t",
            key_slider_t=f"{app_key}_plane_t",
            stack_size_t=self.n_sessions,
        )
        return layout

    def makeLayoutComponentROIPropertyDisplay_Threshold(self, app_key):
        layout = QVBoxLayout()
        layout.addLayout(makeLayoutROIProperty(
            self.widget_manager,
            key_label=f"{app_key}_roi_prop",
            load_caiman=False,
        ))
        return layout

    def makeLayoutComponentROIDisplay_BGImageDisplay_ROISkip(self, app_key):
        layout = QHBoxLayout()
        layout.addWidget(makeLayoutWidgetDislplayCelltype(
            self.widget_manager,
            key_label=f"{app_key}_display_celltype",
            key_checkbox=f"{app_key}_display_celltype",
            key_scrollarea=f"{app_key}_display_celltype",
            table_columns=self.config_manager.table_columns[app_key],
            gui_defaults=self.config_manager.gui_defaults,
        ))
        layout.addWidget(makeLayoutWidgetDislplayCheckbox(
            self.widget_manager,
            key_label=f"{app_key}_display_checkbox",
            key_checkbox=f"{app_key}_display_checkbox",
            key_scrollarea=f"{app_key}_display_checkbox",
            table_columns=self.config_manager.table_columns[app_key],
            gui_defaults=self.config_manager.gui_defaults,
        ))
        layout.addWidget(makeLayoutWidgetBGImageTypeDisplay(
            self,
            self.widget_manager,
            key_label=f"{app_key}_im_bg_type",
            key_buttongroup=f"{app_key}_im_bg_type",
            key_scrollarea=f"{app_key}_im_bg_type",
            gui_defaults=self.config_manager.gui_defaults,
            bg_types=BGImageTypeList.FALL,
            key_combobox=f"{app_key}_im_bg_type_channel",
            key_combobox_label=f"{app_key}_im_bg_type_channel",
            list_combobox_channel=[str(i) for i in range(self.data_manager.getNChannels(app_key))],
        ))
        layout.addWidget(makeLayoutWidgetROIChooseSkip(
            self.widget_manager,
            key_label=f"{app_key}_skip_celltype",
            key_checkbox=f"{app_key}_skip_celltype",
            key_scrollarea=f"{app_key}_skip_celltype",
            table_columns=self.config_manager.table_columns[app_key],
            gui_defaults=self.config_manager.gui_defaults,
        ))
        return layout

    def makeLayoutComponentContrastOpacitySlider(self, app_key):
        layout = QVBoxLayout()
        channels = self.config_manager.gui_defaults["CHANNELS"]
        layout_channel = QHBoxLayout()
        for channel in channels:
            layout_channel.addLayout(makeLayoutContrastSlider(
                self.widget_manager,
                key_label=f"{app_key}_{channel}",
                key_checkbox=f"{app_key}_{channel}",
                key_slider=f"{app_key}_{channel}",
                label_checkbox=f"Show {channel} channel",
                label_label=f"{channel} Value",
                checked=True,
            ))
        layout.addLayout(layout_channel)
        layout.addLayout(makeLayoutOpacitySlider(
            self.widget_manager,
            key_label=app_key,
            key_slider=app_key,
            label=app_key,
        ))
        return layout

    def makeLayoutComponentTable_ROICountLabel_ROISetSameCelltype_ROICurationIO(self, app_key):
        layout = QVBoxLayout()
        layout.addLayout(makeLayoutTableROICountLabel(
            self.widget_manager,
            key_label=app_key,
            key_table=app_key,
            table_columns=self.config_manager.table_columns[app_key],
        ))
        layout.addWidget(self.widget_manager.makeWidgetButton(key=f"{app_key}_config_table", label="Table Columns Config"))
        layout.addLayout(makeLayoutROICurationIO(
            self.widget_manager,
            key_button_save=f"roicuration_save_{app_key}",
            key_button_load=f"roicuration_load_{app_key}",
        ))
        return layout

    def makeLayoutComponent_View_Label_Radiobutton_Slider(self, app_key):
        layout = QVBoxLayout()
        layout.addLayout(self.makeLayoutComponentROIView(app_key))
        layout.addLayout(self.makeLayoutComponentROIPropertyDisplay_Threshold(app_key))
        layout.addLayout(self.makeLayoutComponentROIDisplay_BGImageDisplay_ROISkip(app_key))
        layout.addLayout(self.makeLayoutComponentContrastOpacitySlider(app_key))
        return layout

    def makeLayoutComponent_Table_Button(self, app_key):
        layout = QVBoxLayout()
        layout.addLayout(self.makeLayoutComponentTable_ROICountLabel_ROISetSameCelltype_ROICurationIO(app_key))
        return layout

    "Bottom"
    def makeLayoutComponentFileLoadUI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.widget_manager.makeWidgetLabel(
            key="load_fall", label="File Load",
            font_size=12, bold=True, italic=True, use_global_style=False
        ))
        layout.addLayout(makeLayoutLoadFileExitHelp(self.widget_manager))
        return layout

    "Bottom Extra"
    def makeLayoutComponenImageRegistration(self):
        layout = makeLayoutMultiSessionFallRegistration(
            self.widget_manager,
            n_sessions=self.n_sessions,
            key_label_elastix_method="elastix_label_method",
            key_combobox_elastix_method="elastix_method",
            key_label_ref_s="elastix_label_ref_s",
            key_combobox_ref_s="elastix_ref_s",
            key_button_config="elastix_config",
            key_button_run="elastix_run",
            key_checkbox_show_roi_match="show_roi_match",
            key_checkbox_show_roi_pair="show_roi_pair",
            key_checkbox_show_reg_im_bg="show_reg_im_bg",
            key_checkbox_show_reg_im_roi="show_reg_im_roi",
            key_label_opacity_pair="label_opacity_roi_pair",
            key_slider_opacity_pair="opacity_roi_pair",
        )
        layout.addLayout(makeLayoutManualRegistration(
            self.widget_manager,
            "manual_registration_center",
            "manual_registration_shift_x",
            "manual_registration_shift_y",
            "manual_registration_radian",
            "manual_registration_run",
        ))
        layout.addWidget(self.widget_manager.makeWidgetButton(key="save_reg_roi_bg", label="Save registered ROI and images"))
        layout.addWidget(self.widget_manager.makeWidgetButton(key="load_reg_roi_bg", label="Load registered ROI and images"))
        return layout

    def makeLayoutComponentROIMatching(self):
        layout = QVBoxLayout()
        layout.addLayout(makeLayoutROIMatching(
            self.widget_manager,
            "roi_matching",
            "ot_method",
            "ot_partial_mass",
            "ot_partial_reg",
            "ot_dist_exp",
            "ot_threshold_transport",
            "ot_threshold_cost",
            "ot_partial_mass",
            "ot_partial_reg",
            "ot_dist_exp",
            "ot_threshold_transport",
            "ot_threshold_cost",
            "ot_method",
            "ot_run",
            "ot_clear",
        ))
        layout.addWidget(self.widget_manager.makeWidgetButton(
            "ot_run_all_tplanes", "Run OT for all session pairs"
        ))
        layout.addLayout(makeLayoutROITrackingIO(
            self.widget_manager,
            "roi_matching_save",
            "roi_matching_load",
        ))
        layout.addWidget(self.widget_manager.makeWidgetButton(
            "master_tracking_run", "Generate master tracking table"
        ))
        return layout

    "Section-level layout assembly"
    def makeLayoutSectionLeftUpper(self):
        layout = QHBoxLayout()
        layout.addLayout(self.makeLayoutComponent_View_Label_Radiobutton_Slider(self.app_keys[0]))
        layout.addLayout(self.makeLayoutComponent_Table_Button(self.app_keys[0]))
        return layout

    def makeLayoutSectionRightUpper(self):
        layout = QHBoxLayout()
        layout.addLayout(self.makeLayoutComponent_View_Label_Radiobutton_Slider(self.app_keys[1]))
        layout.addLayout(self.makeLayoutComponent_Table_Button(self.app_keys[1]))
        return layout

    def makeLayoutSectionBottom(self):
        return self.makeLayoutComponentFileLoadUI()

    def makeLayoutSectionBottomExtra(self):
        layout = QHBoxLayout()
        layout.addLayout(self.makeLayoutComponenImageRegistration())
        layout.addLayout(self.makeLayoutComponentROIMatching())
        return layout

    """
    Sub-window dialogs
    """
    def showSubWindowTableColumnConfig(self, app_key):
        config_window = TableColumnConfigDialog(
            self,
            self.control_manager.table_controls[app_key].table_columns,
            self.config_manager.gui_defaults,
        )
        if not config_window.exec_():
            return
        # 1) Mirror the edited columns onto the other panel (sec inherits everything
        #    except the pri-only Cell_ID_Match column).
        self._syncTableColumnsAcrossSessions(source_app_key=app_key)
        # Column structure changed -> previous curation snapshots are stale; drop them.
        self._curation_cache = {}
        # 2) Snapshot user state that the full reload would otherwise destroy:
        #      - dict_roi_matching['match']  (initializeDataControlForMultiSession resets it to all-None)
        #      - current plane_t for both panels (setupControls resets sec to plane_t=1)
        import copy
        saved_matching = copy.deepcopy(self.data_manager.dict_roi_matching)
        saved_t_pri = self.control_manager.view_controls[self.app_keys[0]].getPlaneT()
        saved_t_sec = self.control_manager.view_controls[self.app_keys[1]].getPlaneT()
        # 3) Full UI rebuild: tables + side panels (ROI Display Celltypes / Skip / contrast / etc.)
        #    + control_manager re-creates fresh TableControl / ViewControl with new TableColumns.
        self.setupMainUI()
        # 4) Restore matching and plane_t after the reload.
        self.data_manager.dict_roi_matching['id']    = saved_matching['id']
        self.data_manager.dict_roi_matching['match'] = saved_matching['match']
        for slider_key, value in (
            (f'{self.app_keys[0]}_plane_t', saved_t_pri),
            (f'{self.app_keys[1]}_plane_t', saved_t_sec),
        ):
            slider = self.widget_manager.dict_slider[slider_key]
            slider.blockSignals(True)
            slider.setValue(value)
            slider.blockSignals(False)
        self.switchSession(self.app_keys[0], saved_t_pri)
        self.switchSession(self.app_keys[1], saved_t_sec)

    def _syncTableColumnsAcrossSessions(self, source_app_key: str) -> None:
        """Make the *other* panel's TableColumns match the one the user just edited.
        Pri keeps Cell_ID_Match (id_match column); sec never has it. All other columns
        (names, types, widths, ordering, defaults) are copied from the source side."""
        pri_key, sec_key = self.app_keys[0], self.app_keys[1]
        target_app_key = sec_key if source_app_key == pri_key else pri_key
        source_cols = self.control_manager.table_controls[source_app_key].table_columns.getColumns()
        target_tc   = self.control_manager.table_controls[target_app_key].table_columns
        target_cols_old = target_tc.getColumns()

        if target_app_key == sec_key:
            # sec inherits source minus the pri-only id_match column.
            new_target = {n: dict(i) for n, i in source_cols.items() if i.get('type') != 'id_match'}
        else:
            # pri inherits source (sec) and re-inserts Cell_ID_Match after the id column.
            existing_match = None
            for n, i in target_cols_old.items():
                if i.get('type') == 'id_match':
                    existing_match = (n, dict(i))
                    break
            new_target = {}
            inserted = False
            for n, i in source_cols.items():
                new_target[n] = dict(i)
                if not inserted and i.get('type') == 'id' and existing_match is not None:
                    cm_name, cm_info = existing_match
                    new_target[cm_name] = cm_info
                    inserted = True

        # Renumber 'order' contiguously to match the new insertion order.
        for idx, name in enumerate(new_target):
            new_target[name]['order'] = idx
        target_tc.setColumns(new_target)


    def showSubWindowElastixParamsConfig(self):
        config_window = ElastixParamsConfigDialog(
            self,
            self.config_manager.json_config.get("elastix_params"),
            self.config_manager.gui_defaults,
        )
        if config_window.exec_() == QDialog.Accepted:
            self.config_manager.json_config.set("elastix_params", config_window.elastix_params)

    """
    bindFunc Functions
    """
    def bindFuncFileLoadUI(self):
        self.widget_manager.dict_button["load_file"].clicked.connect(
            lambda: self.loadFilePathsAndInitialize()
        )
        bindFuncExit(q_window=self, q_button=self.widget_manager.dict_button["exit"])
        bindFuncHelp(
            q_button=self.widget_manager.dict_button["help"],
            url=AccessURL.HELP.get(self.config_manager.current_app, ""),
        )

    def bindFuncAllWidget(self):
        for app_key in self.app_keys:
            # ROICuration save / load
            bindFuncROICurationIO(
                q_window=self,
                q_lineedit=self.widget_manager.dict_lineedit[f"path_fall_{app_key}"],
                q_button_save=self.widget_manager.dict_button[f"roicuration_save_{app_key}"],
                q_button_load=self.widget_manager.dict_button[f"roicuration_load_{app_key}"],
                q_table=self.widget_manager.dict_table[app_key],
                widget_manager=self.widget_manager,
                config_manager=self.config_manager,
                control_manager=self.control_manager,
                app_key=app_key,
                local_var=False,
            )
            # Table Columns Config
            self.widget_manager.dict_button[f"{app_key}_config_table"].clicked.connect(
                partial(self.showSubWindowTableColumnConfig, app_key)
            )
            # Background image type radio
            bindFuncRadiobuttonBGImageTypeChanged(
                q_buttongroup=self.widget_manager.dict_buttongroup[f"{app_key}_im_bg_type"],
                view_control=self.control_manager.view_controls[app_key],
            )
            # Background image channel combobox
            bindFuncComboboxBGImageChannelChanged(
                q_combobox=self.widget_manager.dict_combobox[f"{app_key}_im_bg_type_channel"],
                view_control=self.control_manager.view_controls[app_key],
            )
            # Celltype display checkboxes
            bindFuncCheckBoxDisplayCelltypeChanged(
                dict_q_checkbox_celltype={
                    key.split("celltype_roi_display_")[-1]: self.widget_manager.dict_checkbox[key]
                    for key in self.widget_manager.dict_checkbox.keys()
                    if ("celltype_roi_display_" in key) and (app_key in key)
                    and (key.split("celltype_roi_display_")[-1] in set(self.config_manager.table_columns[app_key].getColumns().keys()))
                },
                dict_q_checkbox_checkbox={
                    key.split("checkbox_roi_display_")[-1]: self.widget_manager.dict_checkbox[key]
                    for key in self.widget_manager.dict_checkbox.keys()
                    if ("checkbox_roi_display_" in key) and (app_key in key)
                    and (key.split("checkbox_roi_display_")[-1] in set(self.config_manager.table_columns[app_key].getColumns().keys()))
                },
                view_control=self.control_manager.view_controls[app_key],
                table_control=self.control_manager.table_controls[app_key],
            )
            # Checkbox display checkboxes
            bindFuncCheckBoxDisplayCheckBoxChanged(
                dict_q_checkbox_celltype={
                    key.split("celltype_roi_display_")[-1]: self.widget_manager.dict_checkbox[key]
                    for key in self.widget_manager.dict_checkbox.keys()
                    if ("celltype_roi_display_" in key) and (app_key in key)
                    and (key.split("celltype_roi_display_")[-1] in set(self.config_manager.table_columns[app_key].getColumns().keys()))
                },
                dict_q_checkbox_checkbox={
                    key.split("checkbox_roi_display_")[-1]: self.widget_manager.dict_checkbox[key]
                    for key in self.widget_manager.dict_checkbox.keys()
                    if ("checkbox_roi_display_" in key) and (app_key in key)
                    and (key.split("checkbox_roi_display_")[-1] in set(self.config_manager.table_columns[app_key].getColumns().keys()))
                },
                view_control=self.control_manager.view_controls[app_key],
                table_control=self.control_manager.table_controls[app_key],
            )
            # ROI skip type checkboxes
            bindFuncCheckBoxROIChooseSkip(
                dict_q_checkbox={
                    key.split("celltype_skip_choose_")[-1]: self.widget_manager.dict_checkbox[key]
                    for key in self.widget_manager.dict_checkbox.keys()
                    if ("celltype_skip_choose_" in key) and (app_key in key)
                    and (key.split("celltype_skip_choose_")[-1] in set(self.config_manager.table_columns[app_key].getColumns().keys()))
                },
                control_manager=self.control_manager,
                app_key=app_key,
            )
            # Table radiobutton / checkbox callbacks
            bindFuncRadiobuttonOfTableChanged(
                table_control=self.control_manager.table_controls[app_key],
                view_control=self.control_manager.view_controls[app_key],
            )
            bindFuncCheckboxOfTableChanged(
                table_control=self.control_manager.table_controls[app_key],
                view_control=self.control_manager.view_controls[app_key],
            )
            # Opacity sliders
            bindFuncOpacitySlider(
                q_slider=self.widget_manager.dict_slider[f"{app_key}_opacity_roi_all"],
                view_control=self.control_manager.view_controls[app_key],
            )
            bindFuncHighlightOpacitySlider(
                q_slider=self.widget_manager.dict_slider[f"{app_key}_opacity_roi_selected"],
                view_control=self.control_manager.view_controls[app_key],
            )
            # Channel contrast / visibility
            for channel in self.config_manager.gui_defaults["CHANNELS"]:
                bindFuncBackgroundContrastSlider(
                    q_slider_min=self.widget_manager.dict_slider[f"{app_key}_{channel}_contrast_min"],
                    q_slider_max=self.widget_manager.dict_slider[f"{app_key}_{channel}_contrast_max"],
                    view_control=self.control_manager.view_controls[app_key],
                    channel=channel,
                )
                bindFuncBackgroundVisibilityCheckbox(
                    q_checkbox=self.widget_manager.dict_checkbox[f"{app_key}_{channel}_show"],
                    view_control=self.control_manager.view_controls[app_key],
                    channel=channel,
                )
            # View events (key, mouse, wheel)
            bindFuncViewEvents(
                q_view=self.widget_manager.dict_view[app_key],
                view_control=self.control_manager.view_controls[app_key],
            )

        # ROI table selection sync
        bindFuncTableSelectionChangedWithTracking(
            q_table_pri=self.widget_manager.dict_table[self.app_keys[0]],
            q_table_sec=self.widget_manager.dict_table[self.app_keys[1]],
            table_control_pri=self.control_manager.table_controls[self.app_keys[0]],
            table_control_sec=self.control_manager.table_controls[self.app_keys[1]],
            view_control_pri=self.control_manager.view_controls[self.app_keys[0]],
            view_control_sec=self.control_manager.view_controls[self.app_keys[1]],
            canvas_control_pri=None,
            canvas_control_sec=None,
        )

        # T-slider: switching sessions for each panel independently
        def _onPriTChanged(value):
            slider_pri = self.widget_manager.dict_slider[f"{self.app_keys[0]}_plane_t"]
            slider_sec = self.widget_manager.dict_slider[f"{self.app_keys[1]}_plane_t"]
            if value >= slider_sec.value():
                new_sec = value + 1
                if new_sec > slider_sec.maximum():
                    slider_pri.blockSignals(True)
                    slider_pri.setValue(slider_sec.value() - 1)
                    slider_pri.blockSignals(False)
                    return
                slider_sec.blockSignals(True)
                slider_sec.setValue(new_sec)
                slider_sec.blockSignals(False)
                self.switchSession(self.app_keys[1], new_sec)
            self.switchSession(self.app_keys[0], value)
            self._updateMatchColumn(value, self.control_manager.view_controls[self.app_keys[1]].getPlaneT())

        def _onSecTChanged(value):
            slider_pri = self.widget_manager.dict_slider[f"{self.app_keys[0]}_plane_t"]
            slider_sec = self.widget_manager.dict_slider[f"{self.app_keys[1]}_plane_t"]
            if value <= slider_pri.value():
                new_pri = value - 1
                if new_pri < slider_pri.minimum():
                    slider_sec.blockSignals(True)
                    slider_sec.setValue(slider_pri.value() + 1)
                    slider_sec.blockSignals(False)
                    return
                slider_pri.blockSignals(True)
                slider_pri.setValue(new_pri)
                slider_pri.blockSignals(False)
                self.switchSession(self.app_keys[0], new_pri)
            self.switchSession(self.app_keys[1], value)
            self._updateMatchColumn(self.control_manager.view_controls[self.app_keys[0]].getPlaneT(), value)
            self.control_manager.view_controls[self.app_keys[0]].updateView()

        self.widget_manager.dict_slider[f"{self.app_keys[0]}_plane_t"].valueChanged.connect(_onPriTChanged)
        self.widget_manager.dict_slider[f"{self.app_keys[1]}_plane_t"].valueChanged.connect(_onSecTChanged)

        # Visibility checkboxes
        bindFuncCheckboxShowMatchedROI(
            q_checkbox=self.widget_manager.dict_checkbox["show_roi_match"],
            view_controls=self.control_manager.view_controls,
        )
        bindFuncCheckboxShowROIPair(
            q_checkbox=self.widget_manager.dict_checkbox["show_roi_pair"],
            view_controls=self.control_manager.view_controls,
        )
        bindFuncROIPairOpacitySlider(
            q_slider=self.widget_manager.dict_slider["opacity_roi_pair"],
            view_control=self.control_manager.view_controls[self.app_keys[0]],
        )
        bindFuncCheckboxShowRegisteredBGImage(
            q_checkbox=self.widget_manager.dict_checkbox["show_reg_im_bg"],
            view_controls=self.control_manager.view_controls,
        )
        bindFuncCheckboxShowRegisteredROIImage(
            q_checkbox=self.widget_manager.dict_checkbox["show_reg_im_roi"],
            view_controls=self.control_manager.view_controls,
        )

        # Elastix registration (all sessions vs. reference session)
        bindFuncButtonRunElastixForMultiSessionFall(
            q_widget=self,
            q_button=self.widget_manager.dict_button["elastix_run"],
            data_manager=self.data_manager,
            config_manager=self.config_manager,
            control_manager=self.control_manager,
            combobox_elastix_method=self.widget_manager.dict_combobox["elastix_method"],
            combobox_idx_ref=self.widget_manager.dict_combobox["elastix_ref_s"],
        )
        # Manual registration (sec vs. pri at current T)
        bindFuncButtonRunManualRegistration(
            self,
            q_button=self.widget_manager.dict_button["manual_registration_run"],
            data_manager=self.data_manager,
            config_manager=self.config_manager,
            control_manager=self.control_manager,
            app_key=self.app_keys[0],
            app_key_sec=self.app_keys[1],
            q_lineedit_center=self.widget_manager.dict_lineedit["manual_registration_center"],
            q_lineedit_shift_x=self.widget_manager.dict_lineedit["manual_registration_shift_x"],
            q_lineedit_shift_y=self.widget_manager.dict_lineedit["manual_registration_shift_y"],
            q_lineedit_radian=self.widget_manager.dict_lineedit["manual_registration_radian"],
            path_points_txt="points_tmp.txt",
            output_directory="./elastix",
        )
        # Elastix config dialog
        self.widget_manager.dict_button["elastix_config"].clicked.connect(
            lambda: self.showSubWindowElastixParamsConfig()
        )
        # Save / Load registered ROI and bg images (sec)
        bindFuncRegisteredROIAndBGImageIO(
            q_button_save=self.widget_manager.dict_button["save_reg_roi_bg"],
            q_button_load=self.widget_manager.dict_button["load_reg_roi_bg"],
            q_window=self,
            q_lineedit=self.widget_manager.dict_lineedit[f"path_fall_{self.app_keys[1]}"],
            data_manager=self.data_manager,
            app_key=self.app_keys[1],
        )
        # Multi-session tracking IO (save / load roi_matching)
        bindFuncMultiSessionTrackingIO(
            q_button_save=self.widget_manager.dict_button["roi_matching_save"],
            q_button_load=self.widget_manager.dict_button["roi_matching_load"],
            q_window=self,
            q_lineedit=None,
            config_manager=self.config_manager,
            data_manager=self.data_manager,
            control_manager=self.control_manager,
        )
        # OT ROI matching (current session pair + all session pairs)
        bindFuncButtonRunROIMatchingForXYCT(
            q_widget=self,
            q_button_run=self.widget_manager.dict_button["ot_run"],
            q_button_run_all_tplanes=self.widget_manager.dict_button["ot_run_all_tplanes"],
            widget_manager=self.widget_manager,
            data_manager=self.data_manager,
            control_manager=self.control_manager,
            app_key_pri=self.app_keys[0],
            app_key_sec=self.app_keys[1],
            use_dynamic_table=False,
        )
        # Clear ROI matching result
        bindFuncButtonClearROIMatching(
            q_button=self.widget_manager.dict_button["ot_clear"],
            data_manager=self.data_manager,
            control_manager=self.control_manager,
            app_key_pri=self.app_keys[0],
            app_key_sec=self.app_keys[1],
        )
        # Cell_ID_Match column edit �� update dict_roi_matching and view
        bindFuncIDMatchOfTableChanged(
            table_control=self.control_manager.table_controls[self.app_keys[0]],
            view_control=self.control_manager.view_controls[self.app_keys[0]],
            control_manager=self.control_manager,
            data_manager=self.data_manager,
        )
        # Generate master tracking table (graph-based multi-session alignment)
        def _getSuite2pSessionLabels():
            return list(self.list_path_fall)
        def _getSuite2pDefaultFilename():
            if not self.list_path_fall:
                return "master_tracking.csv"
            first = self.list_path_fall[0]
            base = os.path.splitext(os.path.basename(first))[0]
            return os.path.join(os.path.dirname(first), f"master_tracking_{base}.csv")
        bindFuncButtonGenerateMasterTrackingTable(
            q_button=self.widget_manager.dict_button["master_tracking_run"],
            q_window=self,
            data_manager=self.data_manager,
            get_session_labels_callback=_getSuite2pSessionLabels,
            default_filename_callback=_getSuite2pDefaultFilename,
        )