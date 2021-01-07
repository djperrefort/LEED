from datetime import datetime

import pandas as pd
from PyQt5.QtWidgets import QMainWindow

from .baseWindow import BaseWindow
from ..widgets import PandasTableModel


class SavedResultsWindow(BaseWindow):
    """Window for displaying a ``pandas.DataFrame`` object in a ``QTableWidget``"""

    design_file = '../resources/layouts/ResultsWindow.ui'

    def __init__(self, dataframe: pd.DataFrame, parent: QMainWindow = None) -> None:
        """Populate window with tabular data from a ``pandas.DataFrame`` object

        Args:
            dataframe: ``Dataframe`` to load data from
        """

        super().__init__(parent)
        self.updateTableView(dataframe)

    def updateTableView(self, data: pd.DataFrame) -> None:
        """Update contents of the table widget to reflect contents of a ``DataFrame``

        Args:
            data: The new table data
        """

        self.tableView.setModel(PandasTableModel(data))
        self.tableView.resizeColumnsToContents()
        now = datetime.now()
        self.statusbar.showMessage(f'Loaded on {now: %b %d, %Y} at {now.hour}:{now.minute}')
