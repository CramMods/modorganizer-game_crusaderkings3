import mobase
from .tree import TreeHelper


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
