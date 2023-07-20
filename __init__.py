from .game import GamePlugin
from .installer import ArchiveInstaller


def createPlugins():
    return [GamePlugin(), ArchiveInstaller()]
