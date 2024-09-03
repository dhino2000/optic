# initialize Managers
from typing import Union, Tuple, List
from .data_manager import DataManager
from .control_manager import ControlManager
from .widget_manager import WidgetManager
from .config_manager import ConfigManager

def initManagers(*managers: Union[DataManager, ControlManager, WidgetManager, ConfigManager]) -> Union[DataManager, ControlManager, WidgetManager, ConfigManager, Tuple[Union[DataManager, ControlManager, WidgetManager, ConfigManager], ...]]:
    initialized_managers = []
    for manager in managers:
        if isinstance(manager, DataManager):
            initialized_managers.append(DataManager())
        elif isinstance(manager, ControlManager):
            initialized_managers.append(ControlManager())
        elif isinstance(manager, WidgetManager):
            initialized_managers.append(WidgetManager())
        elif isinstance(manager, ConfigManager):
            initialized_managers.append(ConfigManager())
        else:
            raise ValueError(f"Unsupported manager type: {type(manager)}")

    if len(initialized_managers) == 1:
        return initialized_managers[0]
    else:
        return tuple(initialized_managers)
