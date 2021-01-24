from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from leed.app.utils import SpectralAccessor


def run(dataAccess: SpectralAccessor, out_path: str) -> None:
    import sys

    from PyQt5.QtWidgets import QApplication
    from leed.app.windows import MainWindow
    app = QApplication([])
    x = MainWindow(dataAccess, out_path)
    x.show()
    sys.exit(app.exec_())
