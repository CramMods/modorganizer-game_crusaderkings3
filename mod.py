import mobase
import re

from typing import List


class Descriptor:
    _version: str = ""
    _name: str = ""
    _tags: List[str] = []
    _supported_version: str = ""

    def __init__(self, descriptor_path: str):
        with open(
            descriptor_path, "r", encoding="utf-8-sig"
        ) as descriptor_file:
            content = descriptor_file.read()

        match = re.search(r"^version=\"(.+)\"$", content, re.MULTILINE)
        if match:
            self._version = match.group(1)

        match = re.search(r"tags={\n*(.*)\n*}", content, re.DOTALL)
        if match:
            tags_chunk = match.group(1)
            self._tags = re.findall(
                r"^\s*\"(.+)\"\s*$", tags_chunk, re.MULTILINE
            )

        match = re.search(r"^name=\"(.+)\"$", content, re.MULTILINE)
        if match:
            self._name = match.group(1)

        match = re.search(
            r"^supported_version=\"(.+)\"$", content, re.MULTILINE
        )
        if match:
            self._supported_version = match.group(1)

    def version(self) -> str:
        return self._version

    def tags(self) -> List[str]:
        return self._tags

    def name(self) -> str:
        return self._name

    def supported_version(self) -> str:
        return self._supported_version


class TreeHelper:
    VALID_DIRS: List[str] = [
        "common",
        "content_source",
        "data_binding",
        "dlc",
        "dlc_metadata",
        "events",
        "fonts",
        "gfx",
        "gui",
        "history",
        "licenses",
        "localization",
        "map_data",
        "music",
        "notifications",
        "sound",
        "tests",
        "tools",
        "tweakergui_assets",
    ]

    # Descriptors & Content

    @staticmethod
    def find_descriptor(
        tree: mobase.IFileTree, deep: bool = False
    ) -> mobase.FileTreeEntry:
        descriptor = TreeHelper.find_mod_descriptor(tree, deep=deep)
        if not descriptor:
            descriptor = TreeHelper.find_install_descriptor(tree, deep=deep)
        return descriptor

    @staticmethod
    def find_mod_descriptor(
        tree: mobase.IFileTree, deep: bool = False
    ) -> mobase.FileTreeEntry:
        descriptor = tree.find(
            "descriptor.mod", mobase.FileTreeEntry.FileTypes.FILE
        )
        if descriptor:
            return descriptor

        if deep:
            for entry in tree:
                if entry.isDir():
                    descriptor = TreeHelper.find_mod_descriptor(entry, True)
                    if descriptor:
                        return descriptor

        return None

    @staticmethod
    def find_install_descriptor(
        tree: mobase.IFileTree, deep: bool = False
    ) -> mobase.FileTreeEntry:
        for entry in tree:
            if entry.isFile():
                if entry.suffix() == "mod":
                    return entry

        if deep:
            for entry in tree:
                if entry.isDir():
                    descriptor = TreeHelper.find_install_descriptor(
                        entry, True
                    )
                    if descriptor:
                        return descriptor

        return None

    @staticmethod
    def get_content_source(
        descriptor: mobase.FileTreeEntry,
    ) -> mobase.IFileTree:
        if descriptor.name().casefold() == "descriptor.mod":
            return descriptor.parent()

        source_name = descriptor.name()[:-4]
        source_dir = descriptor.parent().find(
            source_name, mobase.FileTreeEntry.FileTypes.DIRECTORY
        )
        return source_dir

    # Thumbnail

    @staticmethod
    def find_thumbnail(tree: mobase.IFileTree) -> mobase.FileTreeEntry:
        thumbnail = tree.find(
            "thumbnail.png", mobase.FileTreeEntry.FileTypes.FILE
        )
        if thumbnail:
            return thumbnail

        for entry in tree:
            if entry.isDir():
                thumbnail = TreeHelper.find_thumbnail(entry)
                if thumbnail:
                    return thumbnail

        return None

    # Validate Directories

    @staticmethod
    def has_dirs(tree: mobase.IFileTree) -> bool:
        for entry in tree:
            if entry.isDir():
                return True
        return False

    @staticmethod
    def validate_dir(odir: mobase.FileTreeEntry) -> bool:
        return odir.name().casefold() in TreeHelper.VALID_DIRS

    @staticmethod
    def validate_dirs(tree: mobase.IFileTree) -> bool:
        for entry in tree:
            if entry.isDir():
                if not TreeHelper.validate_dir(entry):
                    return False
        return True

    # Validate Files

    @staticmethod
    def has_files(tree: mobase.IFileTree) -> bool:
        for entry in tree:
            if entry.isFile():
                return True
        return False

    # Installable Layout

    @staticmethod
    def can_be_installable(tree: mobase.IFileTree) -> bool:
        descriptor = TreeHelper.find_descriptor(tree, deep=True)
        if descriptor:
            content = TreeHelper.get_content_source(descriptor)
            if content:
                return TreeHelper.is_installable(
                    content, ignore_descriptor=True
                )
        return False

    @staticmethod
    def is_installable(
        tree: mobase.IFileTree, ignore_descriptor: bool = True
    ) -> bool:
        # Installable layout contains a descriptor and valid folders
        # We don't care about files
        if not ignore_descriptor:
            descriptor = TreeHelper.find_mod_descriptor(tree, deep=False)
            if not descriptor:
                return False
        if not TreeHelper.has_dirs(tree):
            return False
        return TreeHelper.validate_dirs(tree)

    @staticmethod
    def to_installable(tree: mobase.IFileTree) -> mobase.IFileTree:
        new_tree = tree.createOrphanTree("")
        descriptor = TreeHelper.find_descriptor(tree, deep=True)
        thumbnail = TreeHelper.find_thumbnail(tree)
        if descriptor:
            new_tree.copy(descriptor, "descriptor.mod")
            if thumbnail:
                new_tree.copy(thumbnail)
            content = TreeHelper.get_content_source(descriptor)
            for entry in content:
                if entry.isDir():
                    new_tree.copy(entry)
            return new_tree if TreeHelper.is_installable(new_tree) else None
        return None

    # Final Layout

    @staticmethod
    def is_final(tree: mobase.IFileTree) -> bool:
        # Final layout contains only valid folders
        if TreeHelper.has_files(tree):
            return False
        if not TreeHelper.has_dirs(tree):
            return False
        return TreeHelper.validate_dirs(tree)

    @staticmethod
    def to_final(tree: mobase.IFileTree) -> mobase.IFileTree:
        tree = TreeHelper.to_installable(tree)
        new_tree = tree.createOrphanTree("")
        for entry in tree:
            if entry.isDir():
                new_tree.copy(entry)
        return new_tree if TreeHelper.is_final(new_tree) else None


class ModDataChecker(mobase.ModDataChecker):
    def __init__(self):
        super().__init__()

    def dataLooksValid(
        self, tree: mobase.IFileTree
    ) -> mobase.ModDataChecker.CheckReturn:
        # Final mod layout, all good
        if TreeHelper.is_final(tree):
            return mobase.ModDataChecker.CheckReturn.VALID

        # Installer mod layout, still has descriptor.mod
        if TreeHelper.is_installable(tree):
            return mobase.ModDataChecker.CheckReturn.FIXABLE

        # Invalid mod layout
        return mobase.ModDataChecker.CheckReturn.INVALID

    def fix(self, tree: mobase.IFileTree) -> mobase.IFileTree:
        # Fix takes us from Installer -> Final
        return TreeHelper.to_final(tree)
