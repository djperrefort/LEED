import pyqtgraph
from astropy.table import Table

from leed.app.settings import RESOURCES_DIR

exampleSpectrum = Table.read(RESOURCES_DIR / 'sn2005kc.ecsv').to_pandas(index='wavelength').flux
exampleBinnedSpectrum = exampleSpectrum.spectrum.bin_spectrum(10, 'median')


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
        super().__init__(*args, **kwargs)

        self.setBackground('w')
        self.setLabel('left', 'Flux', color='k', size=25)
        self.setLabel('bottom', 'Wavelength', color='k', size=25)
        self.showGrid(x=True, y=True)

        # Create lines marking estimated start and end of a feature
        self.lineLowerBound = pyqtgraph.InfiniteLine(5600)
        self.lineUpperBound = pyqtgraph.InfiniteLine(5900)
        self.addItem(self.lineLowerBound)
        self.addItem(self.lineUpperBound)

        # Create regions highlighting wavelength ranges used when estimating
        # the start and end of a feature
        self.regionFeatureStart = pyqtgraph.LinearRegionItem([5550, 5700], movable=False)
        self.regionFeatureEnd = pyqtgraph.LinearRegionItem([5800, 6000], movable=False)
        self.addItem(self.regionFeatureStart)
        self.addItem(self.regionFeatureEnd)

        # Establish a dummy place holder for the plotted spectrum
        # Todo: Plot feature measurements
        self.lineObservedSpectrum = self.plot(exampleSpectrum.spectrum.wave, exampleSpectrum.spectrum.flux)
        self.lineBinnedSpectrum = self.plot(exampleBinnedSpectrum.spectrum.wave, exampleBinnedSpectrum.spectrum.flux)
