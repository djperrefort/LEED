from typing import Optional

import pandas as pd
from PyQt5 import QtCore


class PandasTableModel(QtCore.QAbstractTableModel):
    """Populate a table view from the contents of a pandas dataframe."""

    def __init__(self, data: pd.DataFrame) -> None:
        """A table view that populates from a ``pandas.DataFrame`` object.

        Args:
            data: The ``DataFrame`` to populate from
        """

        QtCore.QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent: QtCore.QObject = None) -> int:
        """Return the number of rows in the table."""

        # noinspection PyTypeChecker
        return len(self._data.values)

    def columnCount(self, parent: QtCore.QObject = None) -> int:
        """Return the number of columns in the table."""

        return self._data.columns.size

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Optional[str]:
        """Return the contents of a cell at a given index.

        Args:
            index: Index of the cell
            role: The display role

        Returns:
            Contents of the cell if set, else None
        """

        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])

    def headerData(self, col: int, orientation: QtCore.Qt.Orientation, role: int) -> Optional[str]:
        """Return the name of a given column.

        Args:
            col: Index of the column
            orientation: Orientation of the header
            role: The display role

        Returns:
            The name of the column if set, else None
        """

        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]

    def toPandas(self) -> pd.DataFrame:
        """Return data from the table view as a ``pandas.DataFrame`` object."""

        return self._data.copy()

