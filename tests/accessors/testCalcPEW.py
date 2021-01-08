from unittest import TestCase

import numpy as np
from uncertainties import UFloat
from uncertainties.unumpy import uarray

from .. import simulate


class PEW(TestCase):
    """Tests for the pEW calculation"""

    def setUp(self):
        """Simulate tophat feature with a flat continuum at y=10 and a
        flat binned flux at y=11
        """

        self.wave = np.arange(100, 500)

        self.flux_m = 5
        self.flux_b = 10
        self.flux, self.eflux = simulate.tophat(
            self.wave,
            m=self.flux_m,
            b=self.flux_b,
            height=0)

        self.bin_flux_m = 5
        self.bin_flux_b = 11
        self.bin_flux = self.bin_flux_m * self.wave + self.bin_flux_b

        self.feature = features.calcPEW(self.wave, self.flux, self.bin_flux)


    def test_no_feature(self):
        """Pass a dummy spectra that is a straight line (f = 2 * lambda)
        and check that the pew is zero.
        """

        wave = np.arange(1000, 3000)
        feature = features.calcPEW(wave, wave, wave)
        self.assertEqual(0, feature.pew)

