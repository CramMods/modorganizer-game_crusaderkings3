try:
    from PyQt6.QtCore import qCritical
    from PyQt6.QtWidgets import QDialog
except Exception:
    from PyQt5.QtCore import qCritical
    from PyQt5.QtWidgets import QDialog

import mobase

from typing import Dict, List, Union

from ..mod import Descriptor, TreeHelper
from ..localization import localize_string

from .ui import Dialog


class ArchiveInstaller(mobase.IPluginInstallerSimple):
    _organizer: mobase.IOrganizer
    _post_install_data: Dict

    def __init__(self):
        super().__init__()

    # IPlugin Implementation

    def init(self, organizer: mobase.IOrganizer) -> bool:
        self._organizer = organizer
        return True

    def name(self) -> str:
        return "Crusader Kings III Archive Installer"

    def localizedName(self) -> str:
        return localize_string(self.name())

    def author(self) -> str:
        return "Cram42"

    def description(self) -> str:
        return localize_string(
            "Adds support for installing Crusader Kings III mod archives"
        )

    def version(self) -> mobase.VersionInfo:
        return mobase.VersionInfo(0, 1, 0)

    def isActive(self) -> bool:
        return self._organizer.pluginSetting(self.name(), "enabled")

    def settings(self) -> List[mobase.PluginSetting]:
        return [
            mobase.PluginSetting(
                "enabled", localize_string("Check to enable this plugin"), True
            )
        ]

    # IPluginInstaller Implementation

    def isArchiveSupported(self, tree: mobase.IFileTree) -> bool:
        return TreeHelper.can_be_installable(tree)

    def isManualInstaller(self) -> bool:
        return False

    def priority(self) -> int:
        return 50

    def onInstallationEnd(self, result, mod):
        if result == mobase.InstallResult.SUCCESS:
            # Set version
            version_string = self._post_install_data.get("version")
            if version_string:
                version = mobase.VersionInfo(version_string)
                mod.setVersion(version)

            # Set categories
            for category in mod.categories():
                mod.removeCategory(category)
            categories = self._post_install_data.get("categories")
            if categories:
                for category in categories:
                    mod.addCategory(category)

    # IPluginInstallerSimple Implementation

    def install(
        self,
        guessed_name: mobase.GuessedString,
        tree: mobase.IFileTree,
        version: str,
        modId: int,
    ) -> Union[mobase.InstallResult, mobase.IFileTree]:
        install_tree = TreeHelper.to_installable(tree)
        if not install_tree:
            qCritical("Install Failed: to_installable returned None")
            return mobase.InstallResult.FAILED

        descriptor_entry = TreeHelper.find_descriptor(install_tree)
        descriptor_path = self._manager().extractFile(descriptor_entry)
        descriptor = Descriptor(descriptor_path)

        thumbnail_entry = TreeHelper.find_thumbnail(install_tree)
        thumbnail_path = (
            self._manager().extractFile(thumbnail_entry)
            if thumbnail_entry
            else ""
        )

        names = [descriptor.name()]
        for variant in guessed_name.variants():
            if variant not in names:
                names.append(variant)

        dialog = Dialog(
            self._parentWidget(),
            names=names,
            image_path=thumbnail_path,
            categories=descriptor.tags(),
            version=descriptor.version(),
            supported_version=descriptor.supported_version(),
        )

        if dialog.exec_() != QDialog.Accepted:
            if dialog.manual():
                return mobase.InstallResult.MANUAL_REQUESTED
            return mobase.InstallResult.CANCELED

        self._post_install_data = {
            "categories": descriptor.tags(),
            "version": descriptor.version(),
        }

        guessed_name.update(self._cleanName(dialog.name()))

        final_tree = TreeHelper.to_final(install_tree)
        if not final_tree:
            qCritical("Install Failed: to_final returned None")
            return mobase.InstallResult.FAILED

        return final_tree

    def _cleanName(self, name: str) -> str:
        safe_chars = [" ", ".", "_"]
        name_chars = []
        for c in name:
            safe_c = c if c in safe_chars or c.isalnum() else "_"
            name_chars.append(safe_c)
        return "".join(name_chars).rstrip()
