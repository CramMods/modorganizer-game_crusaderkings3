try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QPixmap
    from PyQt6.QtWidgets import QDialog, QWidget
except Exception:
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QPixmap
    from PyQt5.QtWidgets import QDialog, QWidget

from typing import List

from .ui_dialog import Ui_Dialog


class Dialog(QDialog):
    _ui: object
    _manual: bool = False

    def __init__(
        self,
        parent: QWidget,
        names: List[str] = [],
        image_path: str = "",
        categories: List[str] = [],
        version: str = "",
        supported_version: str = "",
    ):
        super().__init__(parent)

        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        if image_path != "":
            image_container = self._ui.label_Image
            image = QPixmap(image_path)
            image = image.scaled(
                image_container.width(),
                image_container.height(),
                Qt.KeepAspectRatio,
            )
            image_container.setPixmap(image)

        self._ui.nameComboBox.addItems(names)

        self._ui.versionLineEdit.setText(version)
        self._ui.supportedVersionLineEdit.setText(supported_version)
        self._ui.listWidget_Categories.addItems(categories)

        def manualClicked():
            self._manual = True
            self.reject()

        self._ui.pushButton_Manual.clicked.connect(manualClicked)

        def cancelClicked():
            self.reject()

        self._ui.pushButton_Cancel.clicked.connect(cancelClicked)

        def okClicked():
            self.accept()

        self._ui.pushButton_OK.clicked.connect(okClicked)

    def manual(self) -> bool:
        return self._manual

    def name(self) -> str:
        return self._ui.nameComboBox.currentText()
