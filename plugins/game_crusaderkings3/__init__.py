from .game import GamePlugin
from .installer import ArchiveInstallerPlugin

def createPlugins():
    return [
        GamePlugin(),
        ArchiveInstallerPlugin()
    ]