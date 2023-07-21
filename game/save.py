try:
    from PyQt6.QtCore import QDateTime, qCritical
except Exception:
    from PyQt5.QtCore import QDateTime, qCritical

import mobase
import os
import re

from typing import List


class SaveGame(mobase.ISaveGame):
    _path: str
    _valid: bool
    _basic_name: str = ""
    _use_basic_name: bool = True

    _id: str = ""
    _character_name: str = ""
    _character_title: str = ""
    _game_date: str = ""

    def __init__(self, path: str):
        super().__init__()
        self._path = path
        self._valid = self._read()

    def allFiles(self) -> List[str]:
        return [self.getFilepath()]

    def getCreationTime(self) -> QDateTime:
        ts = int(os.stat(self.getFilepath()).st_mtime)
        return QDateTime.fromSecsSinceEpoch(ts)

    def getFilepath(self) -> str:
        return self._path

    def getName(self) -> str:
        return (
            self._basic_name
            if self._use_basic_name
            else "{}, {} [{}]".format(
                self.character_name(), self.character_title(), self.game_date()
            )
        )

    def getSaveGroupIdentifier(self) -> str:
        return ""

    def valid(self) -> bool:
        return self._valid

    def character_name(self) -> str:
        return self._character_name

    def character_title(self) -> str:
        return self._character_title

    def game_date(self) -> str:
        return self._game_date

    def _read(self) -> bool:
        file_name = os.path.basename(self._path)
        save_name = os.path.splitext(file_name)[0]
        self._basic_name = save_name

        if save_name.startswith("autosave"):
            return True

        meta_content = ""
        with open(
            self._path, "rt", encoding="utf-8", errors="ignore"
        ) as save_file:
            line_num = 0
            depth = 0
            line = ""
            in_meta = False

            while True:
                line_num += 1
                try:
                    line = save_file.readline().strip()
                except Exception:
                    qCritical("Error reading line {}".format(line_num))
                    break

                if line_num == 1:
                    self._id = line
                    if not self._id.startswith("SAV"):
                        qCritical("Invalid Save ID: {}".format(self._id))
                        return False

                if not in_meta:
                    if "meta_data={" in line:
                        in_meta = True
                        depth = 0
                    continue

                depth += line.count("{")
                depth -= line.count("}")
                if depth < 0:
                    break

                meta_content += "\n{}".format(line)

            match = re.search(r"meta_player_name=\"(.+)\"", meta_content)
            if not match:
                qCritical("No character name found")
                return False
            self._character_name = match.group(1)

            match = re.search(r"meta_title_name=\"(.+)\"", meta_content)
            if not match:
                qCritical("No character title found")
                return False
            self._character_title = match.group(1)

            match = re.search(r"meta_date=(.+)", meta_content)
            if not match:
                qCritical("No game date found")
                return False
            self._game_date = match.group(1)

        self._use_basic_name = False
        return True
