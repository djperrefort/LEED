from unittest import TestCase

import numpy as np

from leed.exceptions import FeatureNotObserved
from leed.app.settings import FeatureDefinition
from .. import simulate


class FindPeakWavelength(TestCase):
    """Tests for the ``findPeakWavelength`` function"""

    def setUp(self) -> None:
        """Simulate delta function emission features"""

        wave = np.arange(100, 300)
        self.peak_wavelengths = (210, 250)
        self.spectrum = simulate.delta_func(wave, m=1, b=10, amplitude=500, peak_wave=self.peak_wavelengths)

    def testCorrectPeakCoordinates(self) -> None:
        """Test the correct peak wavelength is found for a single flux spike"""

        expected_peak = self.peak_wavelengths[0]
        recovered_peak = self.spectrum.feature.findPeakWavelength(
            lowerBound=expected_peak - 10,
            upperBound=expected_peak + 10
        )

        self.assertEqual(expected_peak, recovered_peak)

    def test_unobserved_feature(self) -> None:
        """Test an error is raise if the feature is out of bounds"""

        maxWave = self.spectrum.index.max()
        with self.assertRaises(FeatureNotObserved):
            self.spectrum.feature.findPeakWavelength(lowerBound=maxWave + 10, upperBound=maxWave + 20)

    def test_double_peak(self) -> None:
        """Test the correct wavelengths are returned for ``behavior='min'`` and ``behavior='max'``"""

        lowerPeak = min(self.peak_wavelengths)
        upperPeak = max(self.peak_wavelengths)

        returned_lower_peak = self.spectrum.feature.findPeakWavelength(lowerPeak - 10, upperPeak + 10, 'min')
        self.assertEqual(lowerPeak, returned_lower_peak, 'Incorrect min peak')

        returned_upper_peak = self.spectrum.feature.findPeakWavelength(lowerPeak - 10, upperPeak + 10, 'max')
        self.assertEqual(upperPeak, returned_upper_peak, 'Incorrect max peak')


class GuessFeatureBounds(TestCase):
    """Tests for the ``guessBounds`` function"""

    def setUp(self) -> None:
        wave = np.arange(7000, 8001)
        self.peak_wavelengths = (7100, 7500)
        self.spectrum = simulate.delta_func(wave, peak_wave=self.peak_wavelengths)

        self.feature = FeatureDefinition(
            'test feature',
            self.peak_wavelengths[0] - 10,
            self.peak_wavelengths[1] - 10,
            wave.mean(),
            self.peak_wavelengths[0] + 10,
            self.peak_wavelengths[1] + 10
        )

    def test_bounds_for_simulated_feature(self) -> None:
        """Test correct boundaries are returned for a simulated feature"""

        feat_start, feat_end = self.spectrum.feature.guessBounds(self.feature)
        self.assertEqual(self.peak_wavelengths[0], feat_start, 'Incorrect min peak')
        self.assertEqual(self.peak_wavelengths[1], feat_end, 'Incorrect max peak')
