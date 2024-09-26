from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .manager.config_manager import ConfigManager
    from .manager.control_manager import ControlManager
    from .manager.data_manager import DataManager
    from .manager.widget_manager import WidgetManager
    from .controls.view_control import ViewControl
    from .controls.table_control import TableControl
    from .controls.canvas_control import CanvasControl
    from .config.constants import *
    from .config.gui_defaults import GuiDefaults
    from .config.table_columns import TableColumns
    from .config.key_function_map import KeyFunctionMap
    from typing import List, Tuple, Dict, Optional, Callable, Literal, Any
    from PyQt5.QtWidgets import *