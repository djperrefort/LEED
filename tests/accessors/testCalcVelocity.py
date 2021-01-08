from unittest import TestCase

import numpy as np
from astropy import units as units
from astropy.constants import c

import leed
from .. import simulate


class FitGaussian(TestCase):
    """Tests for the fitting of a gaussian to spectral data"""

    @classmethod
    def setUpClass(cls):
        """Simulate gaussian feature"""

        wave = np.arange(1000, 2000)

        # Rest and observer frame wavelengths
        cls.lambda_rest = np.mean(wave)
        cls.avg = cls.lambda_rest - 100
        cls.stdDev = 100
        cls.depth = -1.5
        cls.offset = 100
        cls.spectrum = simulate.gaussian(
            wave, mean=cls.avg, stddev=cls.stdDev, depth=cls.depth, offset=cls.offset)

        cls.gaussianFit = cls.spectrum.feature._fit_gaussian()

    def test_correct_average(self):
        """Test the fit recovers the simulated average"""

        np.testing.assert_almost_equal(self.avg, self.gaussianFit.avg)

    def test_correct_stdDev(self):
        """Test the fit recovers the simulated standard deviation"""

        np.testing.assert_almost_equal(self.stdDev, self.gaussianFit.stdDev)

    def test_correct_amplitude(self):
        """Test the fit recovers the simulated amplitude"""

        np.testing.assert_almost_equal(-self.depth, self.gaussianFit.amplitude)

    def test_correct_offset(self):
        """Test the fit recovers the simulated offset"""

        np.testing.assert_almost_equal(self.offset, self.gaussianFit.offset)


class Velocity(TestCase):
    """Tests for the velocity calculation"""

    @classmethod
    def setUpClass(cls):
        """Simulate gaussian feature"""

        cls.wave = np.arange(1000, 2000)

        # Rest and observer frame wavelengths
        cls.lambda_rest = np.mean(cls.wave)
        cls.restFrame = cls.lambda_rest - 100
        cls.flux = simulate.gaussian(cls.wave, mean=cls.restFrame, stddev=100)

    def test_velocity_estimation(self):
        """Test the calculated velocity matches the simulated velocity"""

        # Doppler equation: λ_observed = λ_source (c − v_source) / c
        # v_expected = (c * (1 - (lambda_observed / lambda_rest))).value

        lambda_ratio = ((self.lambda_rest - self.restFrame) / self.lambda_rest) + 1
        speed_of_light = c.to(units.km / units.s).value
        v_expected = speed_of_light * (
                (lambda_ratio ** 2 - 1) / (lambda_ratio ** 2 + 1)
        )

        np.testing.assert_almost_equal(
            v_expected, self.flux.feature.velocity(self.restFrame),
            err_msg='Fitted velocity not close to simulated velocity')
