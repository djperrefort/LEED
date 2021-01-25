from unittest import TestCase

import numpy as np
import pandas as pd

import leed
from .. import simulate


class TestArea(TestCase):
    """Tests for the area calculation"""

    def setUp(self) -> None:
        """Simulate top-hat feature with a flat continuum"""

        wave = np.arange(100, 501)
        self.spectrum = simulate.tophat(wave, b=10, height=0)
        self.continuum = pd.Series(np.full_like(wave, 10), index=wave)

    def testContinuumArea(self) -> None:
        """Test continuum area is determined relative to the provided continuum"""

        expected = np.trapz(x=self.continuum.index, y=self.continuum.values)
        self.assertEqual(expected, self.spectrum.feature._continuumArea(self.continuum))

    def testFluxArea(self) -> None:
        """Test the flux area is determined relative to observed flux values"""

        expected = np.trapz(x=self.spectrum.index, y=self.spectrum.values)
        self.assertEqual(expected, self.spectrum.feature._fluxArea())

    def testArea(self) -> None:
        """Test the returned area is equal to the continuum - flux area"""

        continuum = self.spectrum.feature._continuumArea(self.continuum)
        flux = self.spectrum.feature._fluxArea()
        expected = continuum - flux
        self.assertEqual(expected, self.spectrum.feature.area(self.continuum))

    def testNoFeature(self) -> None:
        """Test zero is returned for a spectrum without a feature"""

        wave = np.arange(1000, 3000)
        spectrum = pd.Series(np.ones_like(wave), index=wave)
        self.assertEqual(0, spectrum.feature.area(continuum=spectrum))
