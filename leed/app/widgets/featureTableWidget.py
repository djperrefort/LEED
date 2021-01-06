"""The ``FeatureTable`` widget is a subclass of the Qt built-in
``QTableWidget`` class. It extends table functionality to automatically
format, validate, and export spectral feature definitions.
"""

from typing import List

from PyQt5 import QtCore, QtWidgets
from PyQt5 import QtGui

from ..settings import ApplicationSettings, FeatureDefinition
from ..utils import BlockSignals


class FeatureTableWidget(QtWidgets.QTableWidget):
    """A ``QTableWidget`` designed to display feature definitions.

    Each table row has a checkbox in the first cell, with following cells
    used to display data relevant to the definition of spectral features.
    The table is automatically populated on instantiation.
    """

    # List values from settings file in order of their associated table columns
    settingsColumnOrder = ('enabled', 'feature_id', 'restframe', 'lower_blue', 'upper_blue', 'lower_red', 'upper_red')

    def __init__(self, *args, **kwargs) -> None:
        """Populate and style the table."""

        super().__init__(*args, **kwargs)
        self.settings = ApplicationSettings().loadFromDisk()
        self.populateTable()
        self.itemChanged.connect(self._processCellChanged)

    def contentsToList(self) -> List[FeatureDefinition]:
        """Return current table contents as a list of feature definitions."""

        tableContent = []
        for row in range(self.rowCount()):
            rowData = dict()

            for column in range(self.columnCount()):
                columnName = self.settingsColumnOrder[column]
                cell = self.item(row, column)

                if column == 0:
                    rowData[columnName] = int(cell.checkState())

                else:
                    rowData[columnName] = cell.text()

            tableContent.append(FeatureDefinition(**rowData))

        return tableContent

    def removeSelectedRows(self) -> None:
        """Delete the currently selected row from the window's center table."""

        for index in sorted(self.selectionModel().selectedRows()):
            self.removeRow(index.row())

    def addEmptyRow(self) -> int:
        """Add a new row to the table, including a checkbox in the first column.

        Returns:
            The index of the newly added row
        """

        newRowIndex = self.rowCount()
        self.setRowCount(newRowIndex + 1)

        checkbox = QtWidgets.QTableWidgetItem()
        checkbox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)

        with BlockSignals(self):
            self.setItem(newRowIndex, 0, checkbox)

            # Add empty widgets to any empty cells so the cell is stylable
            for column in range(1, self.columnCount()):
                self.setItem(newRowIndex, column, QtWidgets.QTableWidgetItem())

        checkbox.setCheckState(QtCore.Qt.Unchecked)
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

            for columnIndex, columnName in enumerate(self.settingsColumnOrder):
                cellValue = getattr(feature, columnName)

                # The first column is comprised of checkboxes
                if columnIndex == 0:
                    self.item(rowIndex, columnIndex).setCheckState(cellValue)
                    continue

                self.setItem(rowIndex, columnIndex, QtWidgets.QTableWidgetItem(str(cellValue)))

            # Set row background color according to the checkbox value in column 0
            self._updateRowColor(rowIndex)

    def validateCell(self, item: QtWidgets.QTableWidgetItem) -> bool:
        """Validate the contents of a given cell and issue an error dialog if invalid.

        Checks the cell is non-empty and that for columns with wavelength
        values the cell contains a float.

        Args:
            item: The table item to validate

        Returns:
            Whether the cell passes validation
        """

        status = True
        if item.column() == 0:
            return status

        cellText = item.text()
        if not cellText:
            QtWidgets.QMessageBox.about(self, 'Invalid Input', 'The table cannot have empty cells.')
            status = False

        elif item.column() > 1:
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
            self.editItem(item)

        return status

    def validateTable(self) -> bool:
        """Call validation procedure for all cells in the table.

        Stop the validation process after encountering any invalid values.

        Returns:
            Whether the table passes validation
        """

        for row in range(self.rowCount()):
            for column in range(1, self.columnCount()):
                if not self.validateCell(self.item(row, column)):
                    return False

        return True

    def _processCellChanged(self, item: QtWidgets.QTableWidgetItem) -> None:
        """Process the changing of cell content in the table widget.

        Args:
            item: The cell item that was changed
        """

        row = item.row()
        column = item.column()

        self.validateCell(item)
        if column == 0:  # Change the row color to reflect the checkbox state
            self._updateRowColor(row)

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
