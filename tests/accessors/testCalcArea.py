from unittest import TestCase

import numpy as np
import pandas as pd

import leed
from .. import simulate


class TestArea(TestCase):
    """Tests for the area calculation"""

    def setUp(self):
        """Simulate top-hat feature with a flat continuum"""

        wave = np.arange(100, 501)
        self.spectrum = simulate.tophat(wave, b=10, height=0)
        self.continuum = pd.Series(np.full_like(wave, 10), index=wave)

    def test_continuum_area(self):
        """Test continuum area is determined relative to the provided continuum"""

        expected_area = np.trapz(x=self.continuum.index, y=self.continuum.values)
        self.assertEqual(expected_area, self.spectrum.feature._continuum_area(self.continuum))

    def test_flux_area(self):
        """Test the flux area is determined relative to observed flux values"""

        expected_area = np.trapz(x=self.spectrum.index, y=self.spectrum.values)
        self.assertEqual(expected_area, self.spectrum.feature._flux_area())

    def test_area(self):
        """Test the returned area is equal to the continuum - flux area"""

        continuum = self.spectrum.feature._continuum_area(self.continuum)
        flux = self.spectrum.feature._flux_area()
        expected_area = continuum - flux
        self.assertEqual(expected_area, self.spectrum.feature.area(self.continuum))

    def test_no_feature(self):
        """Test zero is returned for a spectrum without a feature"""

        wave = np.arange(1000, 3000)
        spectrum = pd.Series(np.ones_like(wave), index=wave)
        self.assertEqual(0, spectrum.feature.area(continuum=spectrum))
