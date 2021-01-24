import pandas as pd
import pyqtgraph

from leed.accessors.calcVelocity import GaussianFit
from leed.app.settings import ApplicationSettings, SettingsLoader

# Enable anti-aliasing for prettier plots
pyqtgraph.setConfigOptions(antialias=True)


class InspectionPlotWidget(pyqtgraph.PlotWidget):
    """Plotting widget prepopulated with plot elements used in the visual
    inspection of spectral features.

    Plotted elements:
        - lineLowerBound (InfiniteLine): Vertical line marking the beginning of a feature
        - lineUpperBound (InfiniteLine): Vertical line marking the end of a feature
        - regionFeatureStart (LinearRegionItem): Region expected to contain the start of a feature
        - regionFeatureEnd (LinearRegionItem): Region expected to contain the end of a feature
        - lineObservedSpectrum (PlotDataItem): Observed flux values
        - lineBinnedSpectrum (PlotDataItem): Binned flux values
    """

    def __init__(self, *args, **kwargs):
        # Populate the plot with placeholder widgets

        super().__init__(*args, **kwargs)
        self._plottedFits = []
        self._plottedSavedFeatures = []

        self.setBackground('w')
        self.setLabel('left', 'Flux', color='k', size=25)
        self.setLabel('bottom', 'Wavelength', color='k', size=25)
        self.showGrid(x=True, y=True)

        # Create lines marking estimated start and end of a feature
        self.lineLowerBound = pyqtgraph.InfiniteLine(5600, movable=True)
        self.lineUpperBound = pyqtgraph.InfiniteLine(5900, movable=True)
        self.addItem(self.lineLowerBound)
        self.addItem(self.lineUpperBound)

        # Create regions highlighting wavelength ranges used when estimating
        # the start and end of a feature
        self.regionFeatureStart = pyqtgraph.LinearRegionItem([5550, 5700], movable=False)
        self.regionFeatureEnd = pyqtgraph.LinearRegionItem([5800, 6000], movable=False)
        self.addItem(self.regionFeatureStart)
        self.addItem(self.regionFeatureEnd)

        # Establish lines for the observed and binned spectra
        self.lineObservedSpectrum = self.plot()
        self.lineBinnedSpectrum = self.plot()

    def updateStyleFromDisk(self):
        """Update the plot style to reflect application settings currently saved to disk"""

        self.updateStyleFromSettings(SettingsLoader())

    def updateStyleFromSettings(self, settings: ApplicationSettings) -> None:
        """Update the plot style to reflect application settings from memory

        Args:
            settings: Settings object to use for plot configuration
        """

        plotSettings = settings.plotting

        # Set graph item colors
        self.lineLowerBound.setPen(plotSettings.boundary.asPen())
        self.lineUpperBound.setPen(plotSettings.boundary.asPen())
        self.regionFeatureStart.setBrush(plotSettings.start_region.asBrush())
        self.regionFeatureEnd.setBrush(plotSettings.end_region.asBrush())

        # There is a bug in pyqtgraph where the plot renders incorrectly if a QPen is passed to the
        # ``PlotDataItem.setPen`` method. Passing the arguments of a QPen works as an alternative
        self.lineBinnedSpectrum.setPen(
            plotSettings.binned_flux.color.asColor(),
            width=plotSettings.binned_flux.width)

        if plotSettings.show_observed_flux:
            self.lineObservedSpectrum.setPen(
                plotSettings.observed_flux.color.asColor(),
                width=plotSettings.observed_flux.width)

        else:
            self.lineObservedSpectrum.setPen((0, 0, 0, 0))

    def plotObservedSpectrum(self, spectrum: pd.Series) -> None:
        """Plot an observed spectrum

        Args:
            spectrum: Data for the spectrum to plot
        """

        self.lineObservedSpectrum.setData(spectrum.spectrum.wave, spectrum.spectrum.flux)

    def plotBinnedSpectrum(self, spectrum: pd.Series) -> None:
        """Plot a binned spectrum

        Args:
            spectrum: Data for the spectrum to plot
        """

        self.lineBinnedSpectrum.setData(spectrum.spectrum.wave, spectrum.spectrum.flux)

    def plotFeatureFit(self, fitResult: GaussianFit) -> None:
        """Plot a Gaussian fit to a spectroscopic feature"""

        raise NotImplementedError

    def clearFeatureFits(self) -> None:
        """Clear any plotted feature fit results from the plot"""

        while self._plottedFits:
            self._plottedFits.pop().clear()

    def plotSavedFeature(self):
        """Plot marker indicating a feature has been saved"""

        raise NotImplementedError

    def clearSavedFeatures(self) -> None:
        """Clear any saved feature markers from the plot"""

        while self._plottedSavedFeatures:
            self._plottedSavedFeatures.pop().clear()

    def clearAnnotations(self) -> None:
        """Shorthand for calling the ``clearFeatureFits`` and ``clearSavedFeatures`` methods"""

        self.clearFeatureFits()
        self.clearSavedFeatures()
