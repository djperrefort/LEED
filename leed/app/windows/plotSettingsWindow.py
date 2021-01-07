from functools import partial
from typing import Optional

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QColorDialog, QMainWindow

from .baseWindow import BaseWindow
from ..settings import SettingsLoader, ColorSettings


class PlotSettingsWindow(BaseWindow):
    """Window for editing package plotting settings

    Allows users to modify individual plotting settings. Includes a example
    plot so that users can preview their decisions in realtime.
    """

    designFile = 'PlotSettings.ui'

    def __init__(self, parent: Optional[QMainWindow] = None) -> None:
        """Window for displaying saved results as tabular data

        Args
            parent: Optionally assign this window as a child to a parent window
        """

        super().__init__(parent)
        self.settings = SettingsLoader()

        # Update states of window widgets
        self.checkBoxObservedFlux.setCheckState(self.settings.plotting.show_observed_flux)
        self._updateStyling()

        # Assign line edit validators
        reg_ex = QtCore.QRegExp(r'[0-9]{,2}\.?[0-9]{,1}')
        for le in (
                self.lineEditObservedFluxThickness,
                self.lineEditBinnedFluxThickness,
                self.lineEditFittedFeatureThickness,
                self.lineEditFeatureBoundaryThickness):
            le.setValidator(QtGui.QRegExpValidator(reg_ex, le))

        # Connect color selection buttons so they each update a different settings value
        self.pushButtonObservedFluxColor.clicked.connect(partial(self._processButtonClick, 'observed_flux'))
        self.pushButtonBinnedFluxColor.clicked.connect(partial(self._processButtonClick, 'binned_flux'))
        self.pushButtonSavedFeatureColor.clicked.connect(partial(self._processButtonClick, 'saved_feature'))
        self.pushButtonFittedFeatureColor.clicked.connect(partial(self._processButtonClick, 'fitted_feature'))
        self.pushButtonFeatureStartSearchRegion.clicked.connect(partial(self._processButtonClick, 'start_region'))
        self.pushButtonFeatureEndSearchRegion.clicked.connect(partial(self._processButtonClick, 'end_region'))
        self.pushButtonFeatureBoundaryColor.clicked.connect(partial(self._processButtonClick, 'boundary'))

        # Connect line edits so they update the appropriate settings values
        self.lineEditObservedFluxThickness.editingFinished.connect(partial(self._processLineEditChange, self.lineEditObservedFluxThickness, 'observed_flux'))
        self.lineEditBinnedFluxThickness.editingFinished.connect(partial(self._processLineEditChange, self.lineEditBinnedFluxThickness, 'binned_flux'))
        self.lineEditFittedFeatureThickness.editingFinished.connect(partial(self._processLineEditChange, self.lineEditFittedFeatureThickness, 'fitted_feature'))
        self.lineEditFeatureBoundaryThickness.editingFinished.connect(partial(self._processLineEditChange, self.lineEditFeatureBoundaryThickness, 'boundary'))

        # Connect button box buttons
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.apply)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.close)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Reset).clicked.connect(self.reset)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.RestoreDefaults).clicked.connect(self.restoreDefaults)

        self.checkBoxObservedFlux.stateChanged.connect(self._processCheckBoxChange)

    def _processButtonClick(self, settingName: str) -> None:
        """Prompt the user for a new color value and assign the result to plot settings

        Args:
            settingName: Name of an attribute for ``ApplicationSettings.plotting`` to modify the color of
        """

        color = QColorDialog.getColor(options=QColorDialog.ShowAlphaChannel)
        if color.isValid():
            getattr(self.settings.plotting, settingName).color = ColorSettings(*color.getRgb())
            self._updateStyling()

    def _processLineEditChange(self, lineEdit: QtWidgets.QLineEdit, settingName: str) -> None:
        """Update the width setting of a plotted line to equal the content of a line edit

        Args:
            lineEdit: The ``QLineEdit`` to get the size from
            settingName: Name of an attribute for ``ApplicationSettings.plotting`` to modify the width of
        """

        getattr(self.settings.plotting, settingName).width = float(lineEdit.text())
        lineEdit.clearFocus()
        self._updateStyling()

    def _processCheckBoxChange(self, checkedState):
        """Update settings values to reflect the checkbox state"""

        self.settings.plotting.show_observed_flux = checkedState
        self._updateStyling()

    def _updateStyling(self) -> None:
        """Restore displayed settings to currently saved values"""

        plotSettings = self.settings.plotting

        # Set graph item colors
        self.graphWidget.lineLowerBound.setPen(plotSettings.boundary.asPen())
        self.graphWidget.lineUpperBound.setPen(plotSettings.boundary.asPen())
        self.graphWidget.regionFeatureStart.setBrush(plotSettings.start_region.asBrush())
        self.graphWidget.regionFeatureEnd.setBrush(plotSettings.end_region.asBrush())

        # There is a bug in pyqtgraph where the plot renders incorrecly if a QPen is passed to the
        # ``PlotDataItem.setPen`` method. Passing the arguments of a QPen works as an alternative
        binFluxPen = plotSettings.binned_flux.asPen()
        self.graphWidget.lineBinnedSpectrum.setPen(binFluxPen.color(), width=binFluxPen.width())

        if plotSettings.show_observed_flux:
            obsFluxPen = plotSettings.observed_flux.asPen()
            self.graphWidget.lineObservedSpectrum.setPen(obsFluxPen.color(), width=obsFluxPen.width())

        else:
            self.graphWidget.lineObservedSpectrum.setPen((0, 0, 0, 0))

        # Set button colors
        self.pushButtonObservedFluxColor.setStyleSheet(f'background-color: {plotSettings.observed_flux.color.toCSS()};')
        self.pushButtonBinnedFluxColor.setStyleSheet(f'background-color: {plotSettings.binned_flux.color.toCSS()}')
        self.pushButtonSavedFeatureColor.setStyleSheet(f'background-color: {plotSettings.saved_feature.color.toCSS()}')
        self.pushButtonFittedFeatureColor.setStyleSheet(f'background-color: {plotSettings.fitted_feature.color.toCSS()}')
        self.pushButtonFeatureStartSearchRegion.setStyleSheet(f'background-color: {plotSettings.start_region.color.toCSS()}')
        self.pushButtonFeatureEndSearchRegion.setStyleSheet(f'background-color: {plotSettings.end_region.color.toCSS()}')
        self.pushButtonFeatureBoundaryColor.setStyleSheet(f'background-color: {plotSettings.boundary.color.toCSS()}')

        # Set line edit content to match line thicknesses values
        self.lineEditObservedFluxThickness.setText(str(plotSettings.observed_flux.width))
        self.lineEditBinnedFluxThickness.setText(str(plotSettings.binned_flux.width))
        self.lineEditFeatureBoundaryThickness.setText(str(plotSettings.boundary.width))
        self.lineEditFittedFeatureThickness.setText(str(plotSettings.fitted_feature.width))

    def reset(self):
        """Reset displayed settings values to reflect package defaults"""

        self.settings = SettingsLoader()
        self._updateStyling()

    def restoreDefaults(self) -> None:
        """Restore displayed settings to default values"""

        self.settings = SettingsLoader(True)
        self._updateStyling()

    def apply(self) -> None:
        """Save application settings to disk"""

        self.settings.saveToDisk()

    def save(self) -> None:
        """Save application settings to disk and exit"""

        self.apply()
        self.close()
