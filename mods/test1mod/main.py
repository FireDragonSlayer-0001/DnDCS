from dndcs.core.module_base import ModuleBase
from typing import Dict, Any

class TestModule(ModuleBase):
    def __init__(self, manifest: Dict[str, Any]):
        super().__init__(manifest)
