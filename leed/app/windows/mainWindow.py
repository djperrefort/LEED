from pathlib import Path

from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem

from .baseWindow import BaseWindow
from .featureDefinitionsWindow import FeatureDefinitionsWindow
from .plotSettingsWindow import PlotSettingsWindow
from .savedResultsWindow import SavedResultsWindow
from .spectrumSelection import SpectrumSelection
from ..settings import SettingsLoader
from ..utils import SpectralAccessor, get_results_dataframe


class MainWindow(BaseWindow):
    """The main window for visualizing and measuring spectra"""

    designFile = 'MainWindow.ui'

    def __init__(self, dataAccess: SpectralAccessor, out_path: str) -> None:
        """Visualization tool for measuring spectroscopic features

        Args:
            dataAccess (SpectraIterator): Iterator over the data to measure
            out_path               (str): Name of CSV file where results are saved
        """

        # Store init arguments as attributes
        self.dataAccess = dataAccess
        self._out_path = Path(out_path)

        super().__init__()
        self.graphWidget.updateStyleFromDisk()

        # Setup Tasks
        self._initFeatureTable()
        self._connectSignals()

        self.current_spec_results = get_results_dataframe(self._out_path)
        self.current_feat_results = None

        # # Plot the first spectrum / feature combination for user inspection
        self.updateGui()

    def _initFeatureTable(self):
        """Populate the ``feature_bounds_table`` table with feature boundaries
        from the application config.
        """

        settings = SettingsLoader()
        self.tableFeatureBounds.setRowCount(len(settings.features))

        col_order = ('lower_blue', 'upper_blue', 'lower_red', 'upper_red')
        for row_idx, feature in enumerate(settings.features):
            verticaLabel = feature.feature_id
            if len(verticaLabel) >= 15:
                verticaLabel = verticaLabel[:7] + '...'

            self.tableFeatureBounds.setVerticalHeaderItem(row_idx, QTableWidgetItem(verticaLabel))
            for col_idx, col_key in enumerate(col_order):
                cell_content = QTableWidgetItem(str(feature[col_key]))
                cell_content.setTextAlignment(Qt.AlignCenter)
                self.tableFeatureBounds.setItem(row_idx, col_idx, cell_content)

        # Fix the maximum height of the table to the total height of the rows
        # include a bit extra so the scroll bar disappears
        numRows = (self.tableFeatureBounds.rowCount() + 1)
        height = numRows * self.tableFeatureBounds.verticalHeader().defaultSectionSize() + 2
        self.tableFeatureBounds.setMaximumHeight(height)
        self.tableFeatureBounds.resizeColumnsToContents()

    def _connectSignals(self):
        """Connect signals / slots of GUI widgets"""

        # Connect the buttons
        self.pushButtonCalculate.clicked.connect(self.calculate)
        self.pushButtonSave.clicked.connect(self.save)
        self.pushButtonNext.clicked.connect(self.next_feat)
        self.pushButtonPrevious.clicked.connect(self.last_feat)
        self.pushButtonFinished.clicked.connect(self.nextSpectrum)

        # Connect line inputs to/from plot widgets
        self.graphWidget.lineLowerBound.sigPositionChangeFinished.connect(self._updateFeatureBoundsLineEdit)
        self.graphWidget.lineUpperBound.sigPositionChangeFinished.connect(self._updateFeatureBoundsLineEdit)
        self.lineEditFeatureStart.editingFinished.connect(self._updateFeatureBoundsPlot)
        self.lineEditFeatureEnd.editingFinished.connect(self._updateFeatureBoundsPlot)

        # Only allow numbers in text boxes
        reg_ex = QRegExp(r"([0-9]+)|([0-9]+\.)|([0-9]+\.[0-9]+)")
        input_validator = QRegExpValidator(reg_ex)
        self.lineEditFeatureStart.setValidator(input_validator)
        self.lineEditFeatureEnd.setValidator(input_validator)

        # Menu bar
        self.actionFeatureDefinitions.triggered.connect(self.openFeatureDefinitions)
        self.actionViewResults.triggered.connect(self.openResultsWindow)
        self.actionPlottingStyle.triggered.connect(self.openPlotSettings)
        self.actionGoTo.triggered.connect(self.openSpectrumSelector)
        self.actionResetPlot.triggered.connect(self.reset_plot)
        self.actionNextSpectrum.triggered.connect(self.nextSpectrum)
        self.actionPreviousSpectrum.triggered.connect(self.previousSpectrum)
        self.actionNextSN.triggered.connect(self.nextSN)
        self.actionPreviousSN.triggered.connect(self.previousSN)

    def _updateFeatureBoundsLineEdit(self, *args):
        """Update the location of plotted feature bounds to match line edits"""

        self.lineEditFeatureStart.setText(str(self.graphWidget.lineLowerBound.value()))
        self.lineEditFeatureEnd.setText(str(self.graphWidget.lineUpperBound.value()))

    def _updateFeatureBoundsPlot(self, *args):
        """Update line edits to match the location of plotted feature bounds"""

        self.graphWidget.lineLowerBound.setValue(float(self.lineEditFeatureStart.text()))
        self.graphWidget.lineUpperBound.setValue(float(self.lineEditFeatureEnd.text()))

    def updateGui(self) -> None:

        # Plot demo data and update states of window widgets
        snSpectrum = self.dataAccess.spectrum
        binnedSnSpectrum = snSpectrum.spectrum.bin_spectrum(5, 'median')
        self.graphWidget.plotObservedSpectrum(snSpectrum)
        self.graphWidget.plotBinnedSpectrum(binnedSnSpectrum)

    ###########################################################################
    # Menubar options
    ###########################################################################

    def openFeatureDefinitions(self):
        """Open a window for editing feature definitions"""

        self.setDisabled(True)
        feature_definitions_window = FeatureDefinitionsWindow(self)
        feature_definitions_window.closed.connect(self.enableWindowSlot)
        feature_definitions_window.show()

    def openResultsWindow(self):
        """Open a window for previewing results"""

        SavedResultsWindow(get_results_dataframe(self._out_path), self).show()

    def openPlotSettings(self):
        """Open a window for editing plot settings"""

        PlotSettingsWindow(self).show()

    def openSpectrumSelector(self):

        self.setDisabled(True)
        spectrumSelectionWindow = SpectrumSelection(self.dataAccess, self)
        spectrumSelectionWindow.closed.connect(self.enableWindowSlot)
        spectrumSelectionWindow.show()

    def reset_plot(self):
        """Reset the plot to display the current spectrum with default settings

        Auto zooms the plot and repositions plot widgets to their default
        locations.
        """

        raise NotImplementedError

    def nextSpectrum(self):
        """Update the GUI to inspect the next spectrum"""

        try:
            self.dataAccess.loadNextSpectrum()

        except StopIteration:
            self.nextSN()

        else:
            self.updateGui()

    def previousSpectrum(self):
        """Update the GUI to inspect the previous spectrum"""

        try:
            self.dataAccess.loadPreviousSpectrum()

        except StopIteration:
            self.previousSN()

        else:
            self.updateGui()

    def nextSN(self):
        """Update the GUI to inspect the first spectrum of the next SN"""

        try:
            self.dataAccess.loadNextSN()

        except StopIteration:
            QMessageBox.about(self, 'Info', 'You have reached the end of the data set.')

        else:
            self.updateGui()

    def previousSN(self):
        """Update the GUI to inspect the last spectrum of the previous SN"""

        try:
            self.dataAccess.loadPreviousSN()

        except StopIteration:
            QMessageBox.about(self, 'Info', 'You have reached the beginning of the data set.')

        else:
            self.updateGui()

    ###########################################################################
    # Logic for buttons
    ###########################################################################

    def calculate(self):
        """Logic for the ``calculate`` button

        Measure the current spectral feature and store to the
        ``feature_measurements`` attribute.
        """

        raise NotImplementedError

    def save(self):
        """Logic for the ``save`` button

        Save current feature measurements to internal DataFrame.
        """

        self.current_spec_results.to_csv(self._out_path, mode='a')

    def next_feat(self):
        """Logic for the ``next feature`` button

        Skip inspection for the current feature
        """

        raise NotImplementedError

    def last_feat(self):
        """Logic for the ``last feature`` button

        Skip inspection for the current feature
        """

        raise NotImplementedError
