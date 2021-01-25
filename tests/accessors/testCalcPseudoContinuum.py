from unittest import TestCase

import numpy as np

import leed
from tests import simulate


class calcPseudoContinuum(TestCase):
    """Tests for the fitting of the pseudo continuum"""

    def setUp(self) -> None:
        """Simulate a dummy spectrum with a top-hat feature"""

        wave = np.arange(100, 500)

        m = 5
        b = 10
        self.flux = simulate.tophat(wave, m=m, b=b, height=0)
        self.continuum = m * wave + b

    def testRecoveredContinuum(self) -> None:
        """Test the fitted and simulated continuum are equal"""

        np.testing.assert_equal(self.continuum, self.flux.feature.fitPseudoContinuum())