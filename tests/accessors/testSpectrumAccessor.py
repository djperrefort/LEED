from unittest import TestCase

import extinction
import numpy as np
import pandas as pd
from scipy.ndimage.filters import gaussian_filter, generic_filter, median_filter

from leed.accessors.spectrumAccessor import DUSTMAP
from leed.exceptions import SamplingRangeError
from tests import simulate


class FluxBinning(TestCase):
    """Tests for the ``bin`` function."""

    def setUp(self) -> None:
        """Define a mock spectrum"""

        self.bin_size = 5
        wave = np.arange(1000, 2001, 1)
        self.flux = pd.Series(np.ones_like(wave), index=wave)

    def testCorrectBinnedSum(self) -> None:
        """Test``method='sum'`` uses a sum to bin flux values"""

        binnedFlux = self.flux.spectrum.bin(self.bin_size, 'sum')
        sumFlux = generic_filter(self.flux, np.sum, self.bin_size)
        np.testing.assert_equal(sumFlux, binnedFlux)

    def testCorrectBinnedAverage(self) -> None:
        """Test``method='average'`` uses an average to bin flux values"""

        binnedFlux = self.flux.spectrum.bin(self.bin_size, 'average')
        avgFlux = generic_filter(self.flux, np.average, self.bin_size)
        np.testing.assert_equal(avgFlux, binnedFlux)

    def testCorrectBinnedGauss(self) -> None:
        """Test``method='gauss'`` uses a gaussian filter"""

        binnedFlux = self.flux.spectrum.bin(self.bin_size, 'gauss')
        gaussFlux = gaussian_filter(self.flux, self.bin_size)
        np.testing.assert_equal(gaussFlux, binnedFlux)

    def testCorrectBinnedMedian(self) -> None:
        """Test``method='median'`` uses a median filter"""

        binnedFlux = self.flux.spectrum.bin(self.bin_size, 'median')
        medianFlux = median_filter(self.flux, self.bin_size)
        np.testing.assert_equal(medianFlux, binnedFlux)

    def testUnknownMethod(self) -> None:
        """Test a ValueError error is raised for an unknown binning method"""

        with self.assertRaises(ValueError):
            self.flux.spectrum.bin(size=5, method='made up method')


class RestFraming(TestCase):
    """Tests for the rest framing of observed wavelengths"""

    def setUp(self) -> None:
        """Create a spectrum of flux 1 and rest frame it assuming a redshift of 0.5"""

        wave = np.arange(1000, 2000)
        self.flux = pd.Series(np.ones_like(wave), index=wave)

        self.z = .5
        self.restFramed = self.flux.spectrum.restFrame(z=self.z)

    def testWavelengthsAreRestFramed(self) -> None:
        """Assert wavelength values are rest framed"""

        expectedWave = self.flux.spectrum.wave / (1 + self.z)
        np.testing.assert_equal(expectedWave, self.restFramed.spectrum.wave)

    def testFluxUnchanged(self) -> None:
        """Assert flux values are unchanged"""

        np.testing.assert_equal(self.flux.spectrum.flux, self.restFramed.spectrum.flux)


class ExtinctionCorrection(TestCase):
    """Tests for the rest-framing and extinction correction of spectra"""

    @classmethod
    def setUpClass(cls) -> None:
        """Define arguments for mock spectrum"""

        # Simulate flux
        wave = np.arange(7000, 10000, 100)
        cls.flux = pd.Series(np.ones_like(wave, dtype=float), index=wave)

        # Set coordinates pointing towards galactic center
        cls.ra = 266.25
        cls.dec = -29
        cls.rv = 3.1

        # Extinct the simulated flux
        mwebv = DUSTMAP.ebv(cls.ra, cls.dec, frame='fk5j2000', unit='degree')
        ext = extinction.fitzpatrick99(wave, a_v=cls.rv * mwebv)
        cls.extinctedFlux = extinction.apply(ext, cls.flux)

    def testExtinctionCorrection(self) -> None:
        """Test extinction is corrected using Fitzpatrick 99 extinction law"""

        corrected = self.flux.spectrum.correctExtinction(ra=self.ra, dec=self.dec, rv=self.rv)
        pd.testing.assert_series_equal(self.flux, corrected)


class FeatureSampling(TestCase):

    @classmethod
    def setUp(cls) -> None:
        """Define a mock spectrum with a gaussian feature and measure the feature"""

        wave = np.arange(4000, 5000)
        cls.featureStart = 4020
        cls.featureEnd = 4980

        # Define feature using rest and observer frame average wavelength
        cls.lambda_rest = np.mean(wave)
        cls.flux = simulate.gaussian(wave, mean=cls.lambda_rest - 10, stddev=100)

    def testSamplingStepsZero(self) -> None:
        """Test only one sample is taken when ``nstep=0``"""

        callback_returns = []
        self.flux.spectrum.sampleFeatureProperties(
            featStart=self.featureStart,
            featEnd=self.featureEnd,
            restFrame=self.lambda_rest,
            callback=callback_returns.append,
            nstep=0
        )
        self.assertEqual(1, len(callback_returns))

    def testSamplingStepsNonzero(self) -> None:
        """Test correct of samples are taken when ``nstep`` is non-zero"""

        nstep = 5
        nSamples = (2 * nstep + 1) ** 2
        callback_returns = []
        self.flux.spectrum.sampleFeatureProperties(
            featStart=self.featureStart,
            featEnd=self.featureEnd,
            restFrame=self.lambda_rest,
            callback=callback_returns.append,
            nstep=nstep
        )

        self.assertEqual(
            len(callback_returns), nSamples,
            'Incorrect number of samples returned')

    def testCallbackArgumentType(self) -> None:
        """Test callback is passed a pandas Series"""

        def callback(x):
            self.assertIsInstance(
                x, pd.Series,
                f'Callback passed unexpected argument type: {type(x)}'
            )

        self.flux.spectrum.sampleFeatureProperties(
            featStart=self.featureStart,
            featEnd=self.featureEnd,
            restFrame=self.lambda_rest,
            callback=callback,
            nstep=0
        )

    def testRangeTooSmallError(self) -> None:
        """Test a ``ValueError`` is raised when the sampling region is too small"""

        with self.assertRaises(ValueError):
            self.flux.spectrum.sampleFeatureProperties(
                featStart=self.featureStart,
                featEnd=self.featureStart + 1,
                restFrame=self.lambda_rest,
                nstep=0
            )

    def testSamplingRangeError(self) -> None:
        """Test a ``SamplingRangeError`` is raised when the sampling range
        extends passed observed wavelengths
        """

        with self.assertRaises(SamplingRangeError):
            self.flux.spectrum.sampleFeatureProperties(
                featStart=self.flux.spectrum.wave[0],
                featEnd=self.flux.spectrum.wave[-1],
                restFrame=self.lambda_rest,
                nstep=10
            )
