from __future__ import annotations
from ..type_definitions import *
from pathlib import Path
import json

CURRENT_DIR = Path(__file__).resolve().parent
JSON_DIR = CURRENT_DIR / "json"

# manage configs of json files
class JsonConfig:
    def __init__(self):
        self.dir_json = JSON_DIR
        self.configs: Dict[str, Dict[str, Any]] = {}
        self.loadAllConfigs()

    def loadAllConfigs(self) -> None:
        for path_json in self.dir_json.glob('*.json'):
            config_name = path_json.stem
            with open(path_json) as f:
                self.configs[config_name] = json.load(f)

    def get(self, config_name: str) -> Dict[str, Any]:
        return self.configs.get(config_name, {})