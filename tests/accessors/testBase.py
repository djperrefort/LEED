from unittest import TestCase

import numpy as np
import pandas as pd

from leed.accessors.base import Base


class AttributeGetters(TestCase):
    """Test access to Series data from custom class attributes"""

    def setUp(self) -> None:
        """Load mock data from the ``pandas`` package"""

        self.series = pd.Series(np.arange(10, 20))
        self.base = Base(self.series)

    def testWave(self) -> None:
        """Test ``wave`` attribute matches index values"""

        np.testing.assert_array_equal(self.series.index.values, self.base.wave)

    def testFlux(self) -> None:
        """Test ``flux`` attribute matches Series data values"""

        np.testing.assert_array_equal(self.series.values, self.base.flux)


class Validation(TestCase):
    """Tests for the ``validation`` method"""

    def runTest(self) -> None:
        """Test a ValueError is raised when validating an unsorted series"""

        with self.assertRaises(ValueError):
            Base(pd.Series([1, 2, 3], index=[3, 2, 1])).validate()
