"""The ``FeatureTable`` widget is a subclass of the Qt built-in
``QTableWidget`` class. It extends table functionality to automatically
format, validate, and export spectral feature definitions.
"""

from typing import List

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt

from ..settings import ApplicationSettings, FeatureDefinition
from ..utils import BlockSignals


class CustomDelegate(QtWidgets.QStyledItemDelegate):
    """Delegator that adds a checkbox to the left side of a ``QTableWidget`` column"""

    def initStyleOption(self, option, index):
        with BlockSignals(self.parent()):  # Avoid stray signals while updating style options
            if index.data(Qt.CheckStateRole) is None:
                index.model().setData(index, Qt.Unchecked, Qt.CheckStateRole)

            super().initStyleOption(option, index)
            option.displayAlignment = Qt.AlignLeft | Qt.AlignVCenter


class FeatureTableWidget(QtWidgets.QTableWidget):
    """A ``QTableWidget`` designed to display feature definitions.

    Each table row has a checkbox in the first cell, with following cells
    used to display data relevant to the definition of spectral features.
    The table is automatically populated on instantiation.
    """

    # List values from settings file in order of their associated table columns
    settingsColumnOrder = ('feature_id', 'restframe', 'lower_blue', 'upper_blue', 'lower_red', 'upper_red')

    def __init__(self, *args, **kwargs) -> None:
        """Populate and style the table."""

        super().__init__(*args, **kwargs)
        self.setItemDelegateForColumn(0, CustomDelegate(self))  # Add checkbox to first table column
        self.itemChanged.connect(self._processCellChanged)  # Connect signals and slots
        self.settings = ApplicationSettings().loadFromDisk()

    def contentsToList(self) -> List[FeatureDefinition]:
        """Return current table contents as a list of feature definitions."""

        features = []
        for row in range(self.rowCount()):
            kwargs = {name: self.item(row, column).text() for column, name in enumerate(self.settingsColumnOrder)}
            kwargs['enabled'] = self.item(row, 0).checkState()
            features.append(FeatureDefinition(**kwargs))

        return features

    def removeSelectedRows(self) -> None:
        """Delete the currently selected row from the window's center table."""

        for index in sorted(self.selectionModel().selectedRows()):
            self.removeRow(index.row())

    def addEmptyRow(self) -> int:
        """Add a new row to the table, including a checkbox in the first column.

        Returns:
            The index of the newly added row
        """

        # Add a new empty row
        newRowIndex = self.rowCount()

        # Add empty widgets to each cell so the cell is stylable
        with BlockSignals(self):
            self.setRowCount(newRowIndex + 1)
            for column in range(self.columnCount()):
                newItem = QtWidgets.QTableWidgetItem()
                newItem.setTextAlignment(Qt.AlignCenter)
                self.setItem(newRowIndex, column, newItem)

        return newRowIndex

    def populateTable(self, defaults: bool = False) -> None:
        """Restore values of the table widget to currently saved values.

        Args:
            defaults: Restore the table to default values instead of currently saved settings
        """

        if defaults:
            self.settings = self.settings.loadFromDisk()

        # Clear the table so we can repopulate it row by row
        self.setRowCount(0)
        self.setColumnCount(len(self.settingsColumnOrder))

        for feature in self.settings.features:
            rowIndex = self.addEmptyRow()
            for column, columnName in enumerate(self.settingsColumnOrder):
                self.item(rowIndex, column).setText(str(getattr(feature, columnName)))

            self.item(rowIndex, 0).setCheckState(feature.enabled)

    def validateCell(self, item: QtWidgets.QTableWidgetItem) -> bool:
        """Validate the contents of a given cell and issue an error dialog if invalid.

        Checks the cell is non-empty and that for columns with wavelength
        values the cell contains a float.

        Args:
            item: The table item to validate

        Returns:
            Whether the cell passes validation
        """

        status = True  # Assume the cell is valid
        cellText = item.text()

        if not cellText:
            status = False
            QtWidgets.QMessageBox.about(self, 'Invalid Input', 'The table cannot have empty cells.')

        elif item.column() > 0:
            try:
                float(cellText)

            except ValueError:
                status = False
                QtWidgets.QMessageBox.about(
                    self, 'Invalid Input',
                    f'The value "{cellText}" is not valid. Please choose a new value.')

        if not status:  # Strongly encourage the user to fix their mistake by reelecting the cell in edit mode
            self.setCurrentItem(None)  # Exit editing mode if already enabled
            self.setCurrentItem(item)
            self.editItem(item)  # Enter editing mode for the invalid cell

        return status

    def validateTable(self) -> bool:
        """Call validation procedure for all cells in the table.

        Stop the validation process after encountering any invalid values.

        Returns:
            Whether the table passes validation
        """

        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                if not self.validateCell(self.item(row, column)):
                    return False

        return True

    def _processCellChanged(self, item: QtWidgets.QTableWidgetItem) -> None:
        """Process the changing of cell content in the table widget.

        Args:
            item: The cell item that was changed
        """

        self.validateCell(item)
        if item.column() == 0:
            self._updateRowColor(item.row())

    def _updateRowColor(self, row: int) -> None:
        """Update the color of a given row to match it's checkbox state

        Args:
            row: Index of the cell row
        """

        if self.item(row, 0).checkState():
            color = QtGui.QColor('white')

        else:
            color = QtGui.QColor('lightgrey')

        with BlockSignals(self):
            for column in range(self.columnCount()):
                self.item(row, column).setBackground(color)
