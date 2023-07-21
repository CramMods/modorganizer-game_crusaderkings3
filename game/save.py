try:
    from PyQt6.QtCore import QDateTime
except Exception:
    from PyQt5.QtCore import QDateTime

import mobase
import os

from typing import List


class SaveGame(mobase.ISaveGame):
    _path: str

    def __init__(self, path: str):
        super().__init__()
        self._path = path

    def allFiles(self) -> List[str]:
        return [self.getFilepath()]

    def getCreationTime(self) -> QDateTime:
        ts = int(os.stat(self.getFilepath()).st_mtime)
        return QDateTime.fromSecsSinceEpoch(ts)

    def getFilepath(self) -> str:
        return self._path

    def getName(self) -> str:
        return os.path.basename(self.getFilepath())

    def getSaveGroupIdentifier(self) -> str:
        return ""
