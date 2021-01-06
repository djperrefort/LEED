from pathlib import Path
from typing import Optional

from PyQt5 import QtCore, QtWidgets, uic

from leed.app.settings import ApplicationSettings

LAYOUT_DIR = Path(__file__).resolve().parent.parent / 'resources' / 'layouts'


class BaseWindow(QtWidgets.QMainWindow):
    """Base class for creating GUI windows

    Signals:
        closed: Emitted on window close

    Slots:
        enableWindowSlot: Enable the window
        disableWindowSlot: Disable the window
    """

    designFile = None
    closed = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QMainWindow = None) -> None:
        """Load a UI layout file for the current class if specified

        Args:
            parent: Optionally set ownership to a parent window
        """

        super().__init__(parent)
        self.settings = ApplicationSettings().loadFromDisk()

        # Automatically load the style file
        if dp := self.designPath():
            uic.loadUi(dp, self)

    def designPath(self) -> Optional[Path]:
        """Path of the design file for the current window"""

        if self.designFile is not None:
            path = LAYOUT_DIR / self.designFile
            if not path.exists():
                raise FileNotFoundError(f'Design file not found: {path}')

            return path

    def closeEvent(self, event) -> None:
        """Emit the ``closed`` signal when the window closes"""

        # noinspection PyUnresolvedReferences
        self.closed.emit()
        super().closeEvent(event)

    @QtCore.pyqtSlot()
    def enableWindowSlot(self) -> None:
        """Slot for enabling the window"""

        self.setDisabled(False)

    @QtCore.pyqtSlot()
    def disableWindowSlot(self) -> None:
        """Slot for disabling the window"""

        self.setDisabled(True)
