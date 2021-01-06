from tempfile import NamedTemporaryFile
from unittest import TestCase

from PyQt5.QtWidgets import QApplication

from leed.app.windows import BaseWindow

app = QApplication([])


class DesignPath(TestCase):
    """Test the resolution of the windows design file"""

    def setUp(self) -> None:
        self.window = BaseWindow()

    def testPathIsResolved(self) -> None:
        """Test the returned path is fully resolved"""

        with NamedTemporaryFile() as tempfile:
            self.window.designFile = tempfile.name
            self.assertEqual(self.window.designPath().resolve(), self.window.designPath())

    def testFileNotFoundError(self) -> None:
        """Test a ``FileNotFoundError`` error is raised when the given design path cannot be found."""

        self.window.designFile = 'does_not_exist.ui'
        with self.assertRaises(FileNotFoundError):
            self.window.designPath()

    def testNoErrorOnNone(self) -> None:
        """Resolving the design path should fail silently if the path is not defined"""

        self.window.designPath()


class EnableSlot(TestCase):
    """Test the ``enableWindowSlot`` method enables the parent window"""

    def runTest(self) -> None:
        window = BaseWindow()
        window.setDisabled(True)
        window.enableWindowSlot()
        self.assertTrue(window.isEnabled())


class DisableSlot(TestCase):
    """Test the ``disableWindowSlot`` method disables the parent window"""

    def runTest(self) -> None:
        window = BaseWindow()
        window.setDisabled(False)
        window.disableWindowSlot()
        self.assertFalse(window.isEnabled())
