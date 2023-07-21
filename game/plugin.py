try:
    from PyQt6.QtCore import QDir, QFileInfo, QStandardPaths
    from PyQt6.QtGui import QIcon
except Exception:
    from PyQt5.QtCore import QDir, QFileInfo, QStandardPaths
    from PyQt5.QtGui import QIcon

import mobase
import os

from typing import Dict, List

from basic_games.steam_utils import find_games as find_steam_games

from ..localization import localize_string
from ..mod import ModDataChecker


class GamePlugin(mobase.IPluginGame):
    _gamePath: str
    _features: Dict
    _organizer: mobase.IOrganizer

    def __init__(self):
        super().__init__()
        self._gamePath = ""
        self._features = {}

    # IPlugin Implementation

    def init(self, organizer: mobase.IOrganizer) -> bool:
        self._organizer = organizer
        self._features[mobase.ModDataChecker] = ModDataChecker()
        return True

    def name(self) -> str:
        return "Crusader Kings III"

    def localizedName(self) -> str:
        return localize_string(self.name())

    def author(self) -> str:
        return "Cram42"

    def description(self) -> str:
        return localize_string("Adds basic support for Crusader Kings III")

    def version(self) -> mobase.VersionInfo:
        return mobase.VersionInfo(0, 1, 1)

    def isActive(self) -> bool:
        if not self._organizer.managedGame():
            return False
        return self.name() == self._organizer.managedGame().name()

    def settings(self) -> List[mobase.PluginSetting]:
        return []

    # IPluginGame Implementation:

    def CCPlugins() -> List[str]:
        return []

    def DLCPlugins() -> List[str]:
        return []

    def binaryName(self) -> str:
        return "binaries/ck3.exe"

    def dataDirectory(self) -> QDir:
        return QDir(self.gameDirectory().absoluteFilePath("game"))

    def detectGame(self):
        self.setGamePath("")

        steam_games = find_steam_games()
        if self.steamAPPId() in steam_games:
            self.setGamePath(steam_games[self.steamAPPId()])
            return

    def documentsDirectory(self) -> QDir:
        docs_path = QStandardPaths.writableLocation(
            QStandardPaths.DocumentsLocation
        )
        full_path = os.path.join(
            docs_path, "Paradox Interactive/Crusader Kings III"
        )
        return QDir(full_path)

    def executableForcedLoads(
        self,
    ) -> List[mobase.ExecutableForcedLoadSetting]:
        return []

    def executables(self) -> List[mobase.ExecutableInfo]:
        return [
            (
                mobase.ExecutableInfo(
                    self.gameName(),
                    QFileInfo(
                        self.gameDirectory().absoluteFilePath(
                            self.binaryName()
                        )
                    ),
                ).withWorkingDirectory(self.gameDirectory())
            ),
            (
                mobase.ExecutableInfo(
                    "{} (Debug Mode)".format(self.gameName()),
                    QFileInfo(
                        self.gameDirectory().absoluteFilePath(
                            self.binaryName()
                        )
                    ),
                )
                .withWorkingDirectory(self.gameDirectory())
                .withArgument("-debug_mode")
            ),
        ]

    def _featureList(self):
        return self._features

    def gameDirectory(self) -> QDir:
        return QDir(self._gamePath)

    def gameIcon(self) -> QIcon:
        return mobase.getIconForExecutable(
            self.gameDirectory().absoluteFilePath(self.binaryName())
        )

    def gameName(self) -> str:
        return "Crusader Kings III"

    def gameNexusName(self) -> str:
        return self.gameShortName()

    def gameShortName(self) -> str:
        return "crusaderkings3"

    def gameVariants(self) -> List[str]:
        return []

    def gameVersion(self) -> str:
        return mobase.getFileVersion(
            self.gameDirectory().absoluteFilePath(self.binaryName())
        )

    def getLauncherName(self) -> str:
        return ""

    def iniFiles(self) -> List[str]:
        return []

    def initializeProfile(self, directory: QDir, settings: int):
        pass

    def isInstalled(self) -> bool:
        return bool(self._gamePath)

    def listSaves(self, folder: QDir) -> List[mobase.ISaveGame]:
        return []

    def loadOrderMechanism(self) -> mobase.LoadOrderMechanism:
        return mobase.LoadOrderMechanism.PluginsTxt

    def looksValid(self, directory: QDir) -> bool:
        return directory.exists(self.binaryName())

    def nexusGameID(self) -> int:
        return 0

    def nexusModOrganizerID(self) -> int:
        return 0

    def primaryPlugins(self) -> List[str]:
        return []

    def primarySources(self) -> List[str]:
        return []

    def savesDirectory(self) -> QDir:
        savesPath = self.documentsDirectory().absoluteFilePath("save games")
        return QDir(savesPath)

    def setGamePath(self, path):
        self._gamePath = str(path)

    def setGameVariant(self, variant: str):
        pass

    def sortMechanism(self) -> mobase.SortMechanism:
        return mobase.SortMechanism.NONE

    def steamAPPId(self) -> str:
        return "1158310"

    def validShortNames(self) -> List[str]:
        return []
