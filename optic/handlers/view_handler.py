from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QKeyEvent, QMouseEvent, QWheelEvent
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QTableWidgetItem
from ..visualization.view_visual import zoomView, resetZoomView
from ..visualization.view_visual_rectangle import initializeDragRectangle, updateDragRectangle, clipRectangleRange
from ..visualization.roi_edit import editROIdraw, editROIerase, updateROIEditLayer
from ..preprocessing.preprocessing_image import getDictROIImageXYCTFromDictROICoords
from ..utils.view_utils import generateRandomColor
from ..config.constants import AppKeys, PenColors, PenWidth
import numpy as np


class ViewHandler:
    def __init__(
            self,
            view_control: ViewControl,
            app_key: AppKeys,
        ):
        self.view_control = view_control
        self.app_key = app_key
        self.current_app = view_control.config_manager.current_app
        self.handler = self._initializeHandler(self.current_app)

    def _initializeHandler(self, current_app):
        if current_app == "SUITE2P_ROI_CURATION":
            return self.Suite2pROICurationHandler(self.view_control, self.view_control.control_manager.table_controls[self.app_key])
        elif current_app == "SUITE2P_ROI_TRACKING":
            return self.Suite2pROITrackingHandler(self.view_control)
        elif current_app == "MICROGLIA_TRACKING":
            return self.MicrogliaTrackingHandler(self.view_control)
        elif current_app == "TIFSTACK_EXPLORER":
            return self.TifStackExplorerHandler(self.view_control)
        else:
            return self.DefaultHandler(self.view_control)

    def handleKeyPress(self, event: QKeyEvent):
        self.handler.keyPressEvent(event)

    def handleKeyRelease(self, event: QKeyEvent):
        self.handler.keyReleaseEvent(event)

    def handleMousePress(self, event: QMouseEvent):
        self.handler.mousePressEvent(event)

    def handleMouseMove(self, event: QMouseEvent):
        self.handler.mouseMoveEvent(event)

    def handleMouseRelease(self, event: QMouseEvent):
        self.handler.mouseReleaseEvent(event)

    def handleWheelEvent(self, event: QWheelEvent):
        self.handler.wheelEvent(event)

    """
    Suite2pROICuration Handler
    left click : select roi
    middle click + drag : pan
    ctrl + scroll : zoom in/out
    R : reset zoom
    """
    class Suite2pROICurationHandler:
        def __init__(self, view_control: ViewControl, table_control: TableControl):
            self.view_control = view_control
            self.table_control = table_control

        def keyPressEvent(self, event: QKeyEvent):
            if event.key() in self.view_control.dict_key_pushed:
                self.view_control.dict_key_pushed[event.key()] = True
            if event.key() == Qt.Key_R:
                resetZoomView(self.view_control.q_view, self.view_control.q_scene.sceneRect())
                self.view_control.updateView()

        def keyReleaseEvent(self, event: QKeyEvent) -> None:
            if event.key() in self.view_control.dict_key_pushed:
                self.view_control.dict_key_pushed[event.key()] = False

        def mousePressEvent(self, event: QMouseEvent):
            if event.button() == Qt.LeftButton:
                scene_pos = self.view_control.q_view.mapToScene(event.pos())
                self.view_control.getROIwithClick(int(scene_pos.x()), int(scene_pos.y()))
                roi_selected_id = self.view_control.control_manager.getSharedAttr(self.view_control.app_key, 'roi_selected_id')
                self.table_control.updateSelectedROI(roi_selected_id)
                self.table_control.q_table.setFocus()
            elif event.button() == Qt.MiddleButton:
                self.view_control.is_dragging = True
                self.view_control.drag_start_pos = self.view_control.q_view.mapToScene(event.pos())

        def mouseMoveEvent(self, event: QMouseEvent):
            if self.view_control.is_dragging:
                current_pos = self.view_control.q_view.mapToScene(event.pos())
                delta = current_pos - self.view_control.drag_start_pos
                self.view_control.q_view.setTransformationAnchor(QGraphicsView.NoAnchor)
                self.view_control.q_view.translate(delta.x(), delta.y())
                self.view_control.drag_start_pos = current_pos

        def mouseReleaseEvent(self, event: QMouseEvent):
            if self.view_control.is_dragging:
                self.view_control.is_dragging = False
                self.view_control.drag_start_pos = None

        def wheelEvent(self, event: QWheelEvent):
            if self.view_control.dict_key_pushed[Qt.Key_Control]:
                zoomView(self.view_control.q_view, event.angleDelta().y(), event.pos())
                self.view_control.updateView()

    """
    Suite2pROITracking Handler
    --- pri view ---
    left click : select roi
    right click : select roi in sec view
    middle click + drag : pan
    ctrl + scroll : zoom in/out
    R : reset zoom
    --- sec view ---
    left click : select roi
    middle click + drag : pan
    ctrl + scroll : zoom in/out
    R : reset zoom
    """
    class Suite2pROITrackingHandler:
        def __init__(self, view_control: ViewControl):
            self.view_control = view_control
            self.app_key = view_control.app_key

            self.control_manager: ControlManager = view_control.control_manager
            self.table_control: TableControl = self.control_manager.table_controls[self.app_key]

        def keyPressEvent(self, event: QKeyEvent):
            pass

        def keyReleaseEvent(self, event: QKeyEvent):
            pass

        def mousePressEvent(self, event: QMouseEvent):
            scene_pos = self.view_control.q_view.mapToScene(event.pos())
            x, y = int(scene_pos.x()), int(scene_pos.y())
            if event.button() == Qt.LeftButton: # for "pri", "sec" views
                reg = self.view_control.getShowRegImROI() # registered ROI
                self.view_control.getROIwithClick(x, y , reg)
                roi_selected_id = self.view_control.control_manager.getSharedAttr(self.view_control.app_key, 'roi_selected_id')
                self.table_control.updateSelectedROI(roi_selected_id)
                self.table_control.q_table.setFocus()
            elif event.button() == Qt.RightButton: # for "pri" view
                if self.app_key == AppKeys.PRI:
                    self.view_control_sec: ViewControl = self.control_manager.view_controls[AppKeys.SEC]
                    self.table_control_sec: TableControl = self.control_manager.table_controls[AppKeys.SEC]
                    
                    reg = self.view_control.getShowRegImROI() # registered ROI
                    self.view_control_sec.getROIwithClick(x, y , reg)
                    roi_selected_id = self.view_control_sec.control_manager.getSharedAttr(self.view_control_sec.app_key, 'roi_selected_id')
                    self.table_control_sec.updateSelectedROI(roi_selected_id)
                    self.table_control_sec.q_table.setFocus()
                    self.view_control.updateView()

        def mouseMoveEvent(self, event: QMouseEvent):
            pass

        def mouseReleaseEvent(self, event: QMouseEvent):
            pass

        def wheelEvent(self, event: QWheelEvent):
            pass

    """
    MicrogliaTracking Handler
    --- default mode ---
    click : select roi
    middle click + drag : pan
    ctrl + scroll : zoom in/out
    R : reset zoom
    --- roi edit mode ---
    space : quit roi edit mode

    """
    class MicrogliaTrackingHandler:
        def __init__(self, view_control: ViewControl):
            self.view_control:               ViewControl = view_control
            self.table_control:             TableControl = view_control.control_manager.table_controls[view_control.app_key]
            self.control_manager:         ControlManager = view_control.control_manager
            self.data_manager:               DataManager = view_control.data_manager
            self.is_dragging:                       bool = False
            self.is_dragging_edit:                  bool = False
            self.drag_start_pos:         Tuple[int, int] = None
            self.roi_points_edit:   Set[Tuple[int, int]] = set()
            self.roi_id_edit:                        int = None
            self.plane_t:                            int = None
            self.plane_t_pri:                        int = None
            self.plane_t_sec:                        int = None
            self.plane_t_max:                        int = self.data_manager.getSizeOfT(view_control.app_key) - 1
            self.roi_add_mode:                      bool = False
            self.roi_reg:                           bool = False

        def updateROIEditLayer(self):
            updateROIEditLayer(
                self.view_control,
                self.view_control.layer_roi_edit, 
                self.roi_points_edit, 
                color=(255, 255, 255), 
                opacity=self.view_control.roi_edit_opacity
            )

        def keyPressEvent(self, event: QKeyEvent):
            if event.key() in self.view_control.dict_key_pushed:
                self.view_control.dict_key_pushed[event.key()] = True
            # Reset zoom
            if event.key() == Qt.Key_R:
                resetZoomView(self.view_control.q_view, self.view_control.q_scene.sceneRect())
                self.view_control.updateView()
            # Quit ROI edit mode
            if event.key() == Qt.Key_Space:
                self.view_control.roi_edit_mode = False
                print("Quit ROI edit mode")

                try:
                    xpix = np.array(list(self.roi_points_edit)).astype("uint16")[:, 0]
                    ypix = np.array(list(self.roi_points_edit)).astype("uint16")[:, 1]
                    med = (np.median(xpix).astype("uint16"), np.median(ypix).astype("uint16"))
                    dict_roi_coords_xyct_edit = {"xpix": xpix, "ypix": ypix, "med": med}

                    # ROI update
                    self.data_manager.dict_im_roi_xyct = getDictROIImageXYCTFromDictROICoords(self.data_manager.dict_roi_coords_xyct, self.data_manager.getImageSize("pri"))
                    # With "Add ROI" mode
                    if self.roi_add_mode:
                        print(f"add ROI {self.roi_id_edit}")
                        # WARNING: With adding ROI, the coordinates of ROI and that of Registred ROI are the same.
                        self.data_manager.dict_roi_coords_xyct[self.plane_t][self.roi_id_edit] = dict_roi_coords_xyct_edit 
                        self.data_manager.dict_roi_coords_xyct_reg[self.plane_t][self.roi_id_edit] = dict_roi_coords_xyct_edit
                        self.data_manager.dict_roi_matching["id"][self.plane_t] += [self.roi_id_edit]
                        if self.plane_t < self.plane_t_max: # last plane_t does not have cell_id_match
                            for plane_t_sec in self.data_manager.dict_roi_matching["match"][self.plane_t].keys(): # for all sec planes
                                self.data_manager.dict_roi_matching["match"][self.plane_t][plane_t_sec][self.roi_id_edit] = None
                        # hardcoded !!!
                        self.control_manager.view_controls["pri"].roi_colors_xyct[self.plane_t][self.roi_id_edit] = generateRandomColor()
                        self.control_manager.view_controls["sec"].roi_colors_xyct[self.plane_t][self.roi_id_edit] = self.control_manager.view_controls["pri"].roi_colors_xyct[self.plane_t][self.roi_id_edit]
                    # With "Edit ROI" mode
                    else:
                        print(f"edit ROI {self.roi_id_edit}")
                        if self.view_control.show_reg_im_roi:
                            self.data_manager.dict_roi_coords_xyct_reg[self.plane_t][self.roi_id_edit] = dict_roi_coords_xyct_edit
                        else:
                            self.data_manager.dict_roi_coords_xyct[self.plane_t][self.roi_id_edit] = dict_roi_coords_xyct_edit

                except IndexError as e: # no roi_points_edit
                    pass

                self.roi_points_edit = set()
                self.updateROIEditLayer()

                # hardcoded !!!
                for app_key in [AppKeys.PRI, AppKeys.SEC]:
                    self.control_manager.table_controls[app_key].updateWidgetDynamicTableWithT(
                    self.data_manager.dict_roi_matching, self.plane_t_pri, self.plane_t_sec, True if app_key == "pri" else False)
                    self.control_manager.view_controls[app_key].updateView()

        def keyReleaseEvent(self, event: QKeyEvent):
            if event.key() in self.view_control.dict_key_pushed:
                self.view_control.dict_key_pushed[event.key()] = False

        def mousePressEvent(self, event: QMouseEvent):
            scene_pos = self.view_control.q_view.mapToScene(event.pos())
            x, y = int(scene_pos.x()), int(scene_pos.y())
            if self.view_control.roi_edit_mode:
                # Edit ROI
                if event.button() == Qt.LeftButton: 
                    self.is_dragging_edit = True
                    xmin, xmax, ymin, ymax = 0, self.view_control.image_sizes[0], 0, self.view_control.image_sizes[1]
                    editROIdraw(self.roi_points_edit, x, y, radius=self.view_control.roi_edit_radius, x_min=xmin, x_max=xmax, y_min=ymin, y_max=ymax)
                elif event.button() == Qt.RightButton:
                    self.is_dragging_edit = True
                    editROIerase(self.roi_points_edit, x, y, radius=self.view_control.roi_edit_radius) 
            else:
                # Select ROI
                reg = self.view_control.getShowRegImROI() # registered ROI
                if event.button() == Qt.LeftButton: # for "pri", "sec" views
                    self.view_control.getROIwithClick(x, y, reg, xyct=True, roi_skip=False)
                    roi_selected_id = self.view_control.control_manager.getSharedAttr(self.view_control.app_key, 'roi_selected_id')
                    print(f"ROI selected: {roi_selected_id}")
                    self.table_control.updateSelectedROI(roi_selected_id)
                    self.table_control.q_table.setFocus()
                elif event.button() == Qt.RightButton: # for "pri" view
                    if self.view_control.app_key == AppKeys.PRI:
                        self.view_control_sec: ViewControl = self.control_manager.view_controls[AppKeys.SEC]
                        self.table_control_sec: TableControl = self.control_manager.table_controls[AppKeys.SEC]
                        
                        self.view_control_sec.getROIwithClick(x, y, reg, xyct=True, roi_skip=False)
                        roi_selected_id = self.view_control_sec.control_manager.getSharedAttr(self.view_control_sec.app_key, 'roi_selected_id')
                        self.table_control_sec.updateSelectedROI(roi_selected_id)
                        self.table_control_sec.q_table.setFocus()
                        self.view_control.updateView()
                # Pan
                elif event.button() == Qt.MiddleButton:
                    self.is_dragging = True
                    self.drag_start_pos = self.view_control.q_view.mapToScene(event.pos())

        def mouseMoveEvent(self, event: QMouseEvent):
            # Pan
            if self.is_dragging:
                current_pos = self.view_control.q_view.mapToScene(event.pos())
                delta = current_pos - self.drag_start_pos
                self.view_control.q_view.setTransformationAnchor(QGraphicsView.NoAnchor)
                self.view_control.q_view.translate(delta.x(), delta.y())
                self.drag_start_pos = current_pos
            # ROI Edit
            if self.view_control.roi_edit_mode and self.is_dragging_edit:
                scene_pos = self.view_control.q_view.mapToScene(event.pos())
                x, y = int(scene_pos.x()), int(scene_pos.y())

                if event.buttons() & Qt.LeftButton:
                    xmin, xmax, ymin, ymax = 0, self.view_control.image_sizes[0], 0, self.view_control.image_sizes[1]
                    editROIdraw(self.roi_points_edit, x, y, radius=self.view_control.roi_edit_radius, x_min=xmin, x_max=xmax, y_min=ymin, y_max=ymax)
                elif event.buttons() & Qt.RightButton: 
                    editROIerase(self.roi_points_edit, x, y, radius=self.view_control.roi_edit_radius)

                self.updateROIEditLayer()

        def mouseReleaseEvent(self, event: QMouseEvent):
            if self.is_dragging:
                self.is_dragging = False
                self.drag_start_pos = None
            if self.is_dragging_edit:
                self.is_dragging_edit = False

        def wheelEvent(self, event: QWheelEvent):
            # Zoom
            if self.view_control.dict_key_pushed[Qt.Key_Control]:
                zoomView(self.view_control.q_view, event.angleDelta().y(), event.pos())
                self.view_control.updateView()

    """
    TifStackExplorer Handler
    """
    class TifStackExplorerHandler:
        def __init__(self, view_control: ViewControl):
            self.view_control = view_control
            self.is_dragging = False
            self.drag_start_pos = None

        def keyPressEvent(self, event: QKeyEvent):
            if event.key() in self.view_control.dict_key_pushed:
                self.view_control.dict_key_pushed[event.key()] = True
            if event.key() == Qt.Key_R:
                resetZoomView(self.view_control.q_view, self.view_control.q_scene.sceneRect())
                self.view_control.updateView()

        def keyReleaseEvent(self, event: QKeyEvent) -> None:
            if event.key() in self.view_control.dict_key_pushed:
                self.view_control.dict_key_pushed[event.key()] = False

        def mousePressEvent(self, event: QMouseEvent):
            if event.button() == Qt.MiddleButton:
                self.view_control.is_dragging = True
                self.view_control.drag_start_pos = self.view_control.q_view.mapToScene(event.pos())

        def mouseMoveEvent(self, event: QMouseEvent):
            if self.is_dragging:
                current_pos = self.view_control.q_view.mapToScene(event.pos())
                delta = current_pos - self.drag_start_pos
                self.view_control.q_view.setTransformationAnchor(QGraphicsView.NoAnchor)
                self.view_control.q_view.translate(delta.x(), delta.y())
                self.drag_start_pos = current_pos

        def mouseReleaseEvent(self, event: QMouseEvent):
            if event.button() == Qt.MiddleButton:
                self.is_dragging = False
                self.drag_pos_start = None
            else:
                self.view_control.is_dragging = False
                self.view_control.drag_start_pos = None

        def wheelEvent(self, event: QWheelEvent):
            if self.view_control.dict_key_pushed[Qt.Key_Control]:
                zoomView(self.view_control.q_view, event.angleDelta().y(), event.pos())
                self.view_control.updateView()

    """
    Default Handler
    """
    class DefaultHandler:
        def __init__(self, view_control: ViewControl):
            self.view_control = view_control

        def keyPressEvent(self, event: QKeyEvent):
            print("Default: Key Pressed")

        def keyReleaseEvent(self, event: QKeyEvent):
            pass

        def mousePressEvent(self, event: QMouseEvent):
            print("Default: Mouse Pressed")

        def mouseMoveEvent(self, event: QMouseEvent):
            pass

        def mouseReleaseEvent(self, event: QMouseEvent):
            pass

        def wheelEvent(self, event: QWheelEvent):
            pass