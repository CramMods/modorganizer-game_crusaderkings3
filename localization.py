try:
    from PyQt6.QtWidgets import QApplication
except:
    from PyQt5.QtWidgets import QApplication


def localize_string(string: str) -> str:
    return QApplication.translate("CrusaderKings3Plugin", string)