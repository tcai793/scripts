from config import CONFIG
from module_exception import ModuleException
from module_interface import Module_Interface
from paper import Paper

class Module_Reminder(Module_Interface):
    def __init__(self, paper):
        self._paper = paper

    def run(self):
        # Parse config
        pass