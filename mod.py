try:
    from PyQt6.QtCore import qInfo
except:
    from PyQt5.QtCore import qInfo
    
import mobase
import re

from typing import List


class Descriptor():

    _name: str
    _version: str
    _categories: List[str]

    def __init__(self, descriptor_path: str):

        self._name = ""
        self._version = ""
        self._categories = []

        with open(descriptor_path, "r") as descriptor_file:
            content = descriptor_file.read()

        name_match = re.search(r"^name=\"(.+)\"$", content, re.MULTILINE)
        if name_match:
            self._name = name_match.group(1)

        version_match = re.search(r"^version=\"(.+)\"$", content, re.MULTILINE)
        if version_match:
            self._version = version_match.group(1)
        
        tags_match = re.search(r"tags={\n*(.*)\n*}", content, re.DOTALL)
        if tags_match:
            tags_chunk = tags_match.group(1)
            self._categories = re.findall(r"^\s*\"(.+)\"\s*$", tags_chunk, re.MULTILINE)
    
    def name(self) -> str:
        return self._name

    def version(self) -> str:
        return self._version

    def categories(self) -> List[str]:
        return self._categories
        


class TreeHelper():

    _valid_dirs: List[str]
    _valid_files: List[str]

    def __init__(self):
        super().__init__()
        self._valid_dirs = [
            "common", "content_source",
            "data_binding", "dlc", "dlc_metadata",
            "events",
            "fonts",
            "gfx", "gui",
            "history",
            "licenses", "localization",
            "map_data", "music",
            "notifications",
            "sound",
            "tests", "tools", "tweakergui_assets"
        ]
        self._valid_files = []

    # Descriptors & Content

    def find_descriptor(self, tree: mobase.IFileTree, deep: bool = False) -> mobase.FileTreeEntry:
        descriptor = self.find_mod_descriptor(tree, deep=deep)
        if not descriptor:
            descriptor = self.find_install_descriptor(tree, deep=deep)
        return descriptor

    def find_mod_descriptor(self, tree: mobase.IFileTree, deep: bool = False) -> mobase.FileTreeEntry:
        descriptor = tree.find("descriptor.mod", mobase.FileTreeEntry.FileTypes.FILE)
        if descriptor:
            return descriptor
        
        if deep:
            for entry in tree:
                if entry.isDir():
                    descriptor = self.find_mod_descriptor(entry, True)
                    if descriptor:
                        return descriptor

        return None

    def find_install_descriptor(self, tree: mobase.IFileTree, deep: bool = False) -> mobase.FileTreeEntry:
        for entry in tree:
            if entry.isFile():
                if entry.suffix() == "mod":
                    return entry
        
        if deep:
            for entry in tree:
                if entry.isDir():
                    descriptor = self.find_install_descriptor(entry, True)
                    if descriptor:
                        return descriptor

        return None

    def get_content_source(self, descriptor: mobase.FileTreeEntry) -> mobase.IFileTree:
        if descriptor.name().casefold() == "descriptor.mod":
            return descriptor.parent()
        
        source_name = descriptor.name()[:-4]
        source_dir = descriptor.parent().find(source_name, mobase.FileTreeEntry.FileTypes.DIRECTORY)
        return source_dir

    # Validate Directories

    def has_dirs(self, tree: mobase.IFileTree) -> bool:
        for entry in tree:
            if entry.isDir():
                return True
        return False

    def validate_dir(self, odir: mobase.FileTreeEntry) -> bool:
        return odir.name().casefold() in self._valid_dirs

    def validate_dirs(self, tree: mobase.IFileTree) -> bool:
        for entry in tree:
            if entry.isDir():
                if not self.validate_dir(entry):
                    return False
        return True

    # Validate Files

    def has_files(self, tree: mobase.IFileTree) -> bool:
        for entry in tree:
            if entry.isFile():
                return True
        return False

    # Installable Layout

    def can_be_installable(self, tree: mobase.IFileTree) -> bool:
        descriptor = self.find_descriptor(tree, deep=True)
        if descriptor:
            content = self.get_content_source(descriptor)
            if content:
                return self.is_installable(content, ignore_descriptor=True)
        return False

    def is_installable(self, tree: mobase.IFileTree, ignore_descriptor: bool = True) -> bool:
        # Installable layout contains a descriptor and valid folders
        # We don't care about files
        if not ignore_descriptor:
            descriptor = self.find_mod_descriptor(tree, deep=False)
            if not descriptor:
                return False
        if not self.has_dirs(tree):
            return False
        return self.validate_dirs(tree)
    
    def to_installable(self, tree: mobase.IFileTree) -> mobase.IFileTree:
        new_tree = tree.createOrphanTree("")
        descriptor = self.find_descriptor(tree, deep=True)
        if descriptor:
            new_tree.copy(descriptor, "descriptor.mod")
            content = self.get_content_source(descriptor)
            for entry in content:
                if entry.isDir():
                    new_tree.copy(entry)
            return new_tree if self.is_installable(new_tree) else None
        return None

    # Final Layout

    def is_final(self, tree: mobase.IFileTree) -> bool:
        # Final layout contains only valid folders
        if self.has_files(tree):
            return False
        if not self.has_dirs(tree):
            return False
        return self.validate_dirs(tree)
    
    def to_final(self, tree: mobase.IFileTree) -> mobase.IFileTree:
        tree = self.to_installable(tree)
        new_tree = tree.createOrphanTree("")
        for entry in tree:
            if entry.isDir():
                new_tree.copy(entry)
        return new_tree if self.is_final(new_tree) else None


class ModDataChecker(mobase.ModDataChecker):

    _tree_helper: TreeHelper

    def __init__(self):
        super().__init__()
        self._tree_helper = TreeHelper()

    def dataLooksValid(self, tree: mobase.IFileTree) -> mobase.ModDataChecker.CheckReturn:

        # Final mod layout, all good
        if self._tree_helper.is_final(tree):
            return mobase.ModDataChecker.CheckReturn.VALID

        # Installer mod layout, still has descriptor.mod
        if self._tree_helper.is_installable(tree):
            return mobase.ModDataChecker.CheckReturn.FIXABLE

        # Invalid mod layout
        return mobase.ModDataChecker.CheckReturn.INVALID
    
    def fix(self, tree: mobase.IFileTree) -> mobase.IFileTree:
        # Fix takes us from Installer -> Final
        return self._tree_helper.to_final(tree)