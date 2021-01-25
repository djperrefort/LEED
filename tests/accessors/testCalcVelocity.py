from unittest import TestCase

import numpy as np
import pandas as pd
from astropy import units as units
from astropy.constants import c

import leed
from .. import simulate


class FitGaussian(TestCase):
    """Tests for the fitting of a gaussian to spectral data"""

    @classmethod
    def setUpClass(cls) -> None:
        """Simulate gaussian feature"""

        wave = np.arange(1000, 2000)

        # Rest and observer frame wavelengths
        cls.lambdaRestFrame = np.mean(wave)
        cls.avg = cls.lambdaRestFrame - 100
        cls.stdDev = 100
        cls.depth = -1.5
        cls.offset = 100
        cls.spectrum = simulate.gaussian(
            wave, mean=cls.avg, stddev=cls.stdDev, depth=cls.depth, offset=cls.offset)

        cls.gaussianFit = cls.spectrum.feature._fitGaussian()

    def testCorrectAverage(self) -> None:
        """Test the fit recovers the simulated average"""

        np.testing.assert_almost_equal(self.avg, self.gaussianFit.avg)

    def testCorrectStdDev(self) -> None:
        """Test the fit recovers the simulated standard deviation"""

        np.testing.assert_almost_equal(self.stdDev, self.gaussianFit.stdDev)

    def testCorrectAmplitude(self) -> None:
        """Test the fit recovers the simulated amplitude"""

        np.testing.assert_almost_equal(-self.depth, self.gaussianFit.amplitude)

    def testCorrectOffset(self) -> None:
        """Test the fit recovers the simulated offset"""

        np.testing.assert_almost_equal(self.offset, self.gaussianFit.offset)


class Velocity(TestCase):
    """Tests for the velocity calculation"""

    @classmethod
    def setUpClass(cls) -> None:
        """Simulate gaussian feature"""

        cls.wave = np.arange(1000, 2000)

        # Rest and observer frame wavelengths
        cls.lambdaRestFrame = np.mean(cls.wave)
        cls.lambdaObserverFrame = cls.lambdaRestFrame - 100
        cls.flux = simulate.gaussian(cls.wave, mean=cls.lambdaObserverFrame, stddev=100)

    def testVelocityEstimation(self) -> None:
        """Test the calculated velocity matches the simulated velocity"""

        # Doppler equation: λ_observed = λ_source (c − v_source) / c

        lambdaRatio = ((self.lambdaRestFrame - self.lambdaObserverFrame) / self.lambdaRestFrame) + 1
        speedOfLight = c.to(units.km / units.s).value
        expected = speedOfLight * (
                (lambdaRatio ** 2 - 1) / (lambdaRatio ** 2 + 1)
        )

        np.testing.assert_almost_equal(
            expected, self.flux.feature.velocity(self.lambdaRestFrame),
            err_msg='Fitted velocity not close to simulated velocity')
