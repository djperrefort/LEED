from functools import partial

from PyQt5 import QtWidgets

from .baseWindow import BaseWindow
from ..settings import SettingsLoader


class FeatureDefinitionsWindow(BaseWindow):
    """Window for editing definitions of spectral features.

    Provides a tabular interface for selecting which spectroscopic
    features should be measured along with the definitions of those features
    stored in settings.
    """

    designFile = 'FeatureDefinitions.ui'

    def __init__(self, parent: QtWidgets.QMainWindow = None) -> None:
        """Window for editing definitions of spectral features.

        Args:
            parent: Optionally set ownership to a parent window
        """

        super().__init__(parent)

        # Connect signals and slots for class widgets
        self.pushButtonAdd.clicked.connect(self.tableWidget.addEmptyRow)
        self.pushButtonRemove.clicked.connect(self.tableWidget.removeSelectedRows)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.apply)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.cancel)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Reset).clicked.connect(self.tableWidget.populateTable)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.RestoreDefaults).clicked.connect(
            partial(self.tableWidget.populateTable, True))

        # Connect keyboard shortcuts
        self.actionSave.triggered.connect(self.save)
        self.actionDelete.triggered.connect(self.tableWidget.removeSelectedRows)
        self.actionNew.triggered.connect(self.tableWidget.addEmptyRow)

        # Populate and format the table
        self.tableWidget.populateTable()
        self.tableWidget.setColumnWidth(0, 200)
        for i in range(self.tableWidget.columnCount()):
            self.tableWidget.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Fixed)

    def apply(self) -> bool:
        """Save changes without exiting the window.

        Returns:
            Boolean indicating if settings were successfully saved
        """

        if self.tableWidget.validateTable():
            settings = SettingsLoader()
            settings.features = self.tableWidget.contentsToList()
            settings.saveToDisk()
            return True

        return False

    def save(self) -> None:
        """Try saving changes and, if successful, exit the window."""

        if self.apply():
            self.close()

    def cancel(self) -> None:
        """Exit the window without saving changes."""

        self.close()
