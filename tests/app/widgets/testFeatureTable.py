from unittest import TestCase

from PyQt5 import QtCore, QtWidgets

from leed.app.widgets import FeatureTableWidget

app = QtWidgets.QApplication([])


class EmptyRowCreation(TestCase):
    """Tests the addition of new rows to a table"""

    def setUp(self) -> None:
        """Create a table widget and add an empty row."""

        self.tableWidget = FeatureTableWidget()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        self.tableWidget.addEmptyRow()

    def testRowIsAdded(self) -> None:
        """Test a new row is added."""

        self.assertEqual(self.tableWidget.rowCount(), 1)

    def testFirstCellCheckbox(self) -> None:
        """Test the first cell contains an enabled checkbox."""

        checkbox_item = self.tableWidget.item(0, 0)
        self.assertEqual(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled, checkbox_item.flags())

    def testAllCellsHaveWidgets(self) -> None:
        """All cells have a ``QTableWidgetItem`` inside them."""

        for column in range(self.tableWidget.columnCount()):
            self.assertIsInstance(self.tableWidget.item(0, 1), QtWidgets.QTableWidgetItem)
