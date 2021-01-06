"""The ``FeatureDefinitions`` class allows users to modify which spectroscopic
features they want to measure along with the definitions of those features
stored in settings.
"""

from functools import partial

from PyQt5 import QtWidgets

from .baseWindow import BaseWindow
from ..settings import SettingsLoader


class FeatureDefinitions(BaseWindow):
    """Window for editing definitions of spectral features."""

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

    def apply(self) -> None:
        """Save changes without exiting the window."""

        if self.tableWidget.validateTable():
            settings = SettingsLoader()
            settings.features = self.tableWidget.contentsToList()
            settings.saveToDisk()

    def save(self) -> None:
        """Save changes and exit the window."""

        if self.apply():
            self.close()

    def cancel(self) -> None:
        """Exit the window without saving changes."""

        self.close()
