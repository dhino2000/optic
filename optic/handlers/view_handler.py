from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QKeyEvent, QMouseEvent, QWheelEvent
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem
from ..visualization.view_visual import zoomView, resetZoomView
from ..visualization.view_visual_rectangle import initializeDragRectangle, updateDragRectangle, clipRectangleRange
from ..config.constants import AppKeys, PenColors, PenWidth


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
        if current_app == "SUITE2P_ROI_CHECK":
            return self.Suite2pROICheckHandler(self.view_control, self.view_control.control_manager.table_controls[self.app_key])
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
    Suite2pROICheck Handler
    """
    class Suite2pROICheckHandler:
        def __init__(self, view_control: ViewControl, table_control: TableControl):
            self.view_control = view_control
            self.table_control = table_control
            self.is_dragging = False

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
                self.is_dragging = True
                self.drag_start_pos = self.view_control.q_view.mapToScene(event.pos())

        def mouseMoveEvent(self, event: QMouseEvent):
            if self.is_dragging:
                current_pos = self.view_control.q_view.mapToScene(event.pos())
                delta = current_pos - self.drag_start_pos
                self.view_control.q_view.setTransformationAnchor(QGraphicsView.NoAnchor)
                self.view_control.q_view.translate(delta.x(), delta.y())
                self.drag_start_pos = current_pos

        def mouseReleaseEvent(self, event: QMouseEvent):
            if self.is_dragging:
                self.is_dragging = False
                self.drag_start_pos = None

        def wheelEvent(self, event: QWheelEvent):
            if self.view_control.dict_key_pushed[Qt.Key_Control]:
                zoomView(self.view_control.q_view, event.angleDelta().y(), event.pos())
                self.view_control.updateView()

    """
    Suite2pROITracking Handler
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
            if event.button() == Qt.LeftButton: # for "pri", "sec" views
                scene_pos = self.view_control.q_view.mapToScene(event.pos())
                reg = self.view_control.getShowRegImROI() # registered ROI
                self.view_control.getROIwithClick(int(scene_pos.x()), int(scene_pos.y()), reg)
                roi_selected_id = self.view_control.control_manager.getSharedAttr(self.view_control.app_key, 'roi_selected_id')
                self.table_control.updateSelectedROI(roi_selected_id)
                self.table_control.q_table.setFocus()
            elif event.button() == Qt.RightButton: # for "pri" view
                if self.app_key == AppKeys.PRI:
                    self.view_control_sec: ViewControl = self.control_manager.view_controls[AppKeys.SEC]
                    self.table_control_sec: TableControl = self.control_manager.table_controls[AppKeys.SEC]
                    
                    scene_pos = self.view_control.q_view.mapToScene(event.pos())
                    reg = self.view_control.getShowRegImROI() # registered ROI
                    self.view_control_sec.getROIwithClick(int(scene_pos.x()), int(scene_pos.y()), reg)
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
    """
    class MicrogliaTrackingHandler:
        def __init__(self, view_control: ViewControl):
            self.view_control = view_control
            self.table_control = view_control.control_manager.table_controls[view_control.app_key]
            self.is_dragging = False
            self.drag_start_pos = None

        def keyPressEvent(self, event: QKeyEvent):
            if event.key() in self.view_control.dict_key_pushed:
                self.view_control.dict_key_pushed[event.key()] = True
            if event.key() == Qt.Key_R:
                resetZoomView(self.view_control.q_view, self.view_control.q_scene.sceneRect())
                self.view_control.updateView()

        def keyReleaseEvent(self, event: QKeyEvent):
            if event.key() in self.view_control.dict_key_pushed:
                self.view_control.dict_key_pushed[event.key()] = False

        def mousePressEvent(self, event: QMouseEvent):
            if event.button() == Qt.LeftButton:
                scene_pos = self.view_control.q_view.mapToScene(event.pos())
                reg = self.view_control.getShowRegImROI() # registered ROI
                self.view_control.getROIwithClick(int(scene_pos.x()), int(scene_pos.y()), reg, xyct=True)
                roi_selected_id = self.view_control.control_manager.getSharedAttr(self.view_control.app_key, 'roi_selected_id')
                self.table_control.updateSelectedROI(roi_selected_id)
                self.table_control.q_table.setFocus()
            elif event.button() == Qt.MiddleButton:
                self.is_dragging = True
                self.drag_start_pos = self.view_control.q_view.mapToScene(event.pos())

        def mouseMoveEvent(self, event: QMouseEvent):
            if self.is_dragging:
                current_pos = self.view_control.q_view.mapToScene(event.pos())
                delta = current_pos - self.drag_start_pos
                self.view_control.q_view.setTransformationAnchor(QGraphicsView.NoAnchor)
                self.view_control.q_view.translate(delta.x(), delta.y())
                self.drag_start_pos = current_pos

        def mouseReleaseEvent(self, event: QMouseEvent):
            if self.is_dragging:
                self.is_dragging = False
                self.drag_start_pos = None

        def wheelEvent(self, event: QWheelEvent):
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
                self.is_dragging = True
                self.drag_start_pos = self.view_control.q_view.mapToScene(event.pos())

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
                self.is_dragging = False
                self.drag_start_pos = None

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