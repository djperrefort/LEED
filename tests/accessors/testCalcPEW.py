from unittest import TestCase

import numpy as np
import pandas as pd

import leed
from .. import simulate


class PEW(TestCase):
    """Tests for the pEW calculation"""

    def setUp(self) -> None:
        """Simulate a top-hat feature with a flat continuum at y=5 * x + 10"""

        wave = np.arange(100, 500)

        self.m = 5
        self.b = 10
        self.start_idx = 100
        self.end_idx = -100
        self.flux = simulate.tophat(
            wave,
            start=self.start_idx,
            end=self.end_idx,
            m=self.m,
            b=self.b,
            height=0)

        self.bin_flux = self.m * wave + self.b

    def testPewCalculation(self) -> None:
        """Test the PEW calculation returns the normalized area of the feature"""

        norm_flux = self.flux / self.bin_flux
        w = norm_flux.index[self.end_idx] - norm_flux.index[self.start_idx]
        h1 = norm_flux.iloc[self.start_idx]
        h2 = norm_flux.iloc[self.end_idx]
        area = (w * h1) + (.5 * w * (h2 - h1))

        self.assertEqual(area, self.flux.feature.pew(self.bin_flux))

    def testNoFeature(self) -> None:
        """Assert the PEW is zero for a flat spectrum with no feature"""

        wave = np.arange(1000, 3000)
        flat_spectrum = pd.Series(wave, wave)
        self.assertEqual(0, flat_spectrum.feature.pew(continuum=flat_spectrum))
