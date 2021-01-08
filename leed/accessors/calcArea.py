import numpy as np
import pandas as pd

from leed.accessors.base import Base


class CalcArea(Base):
    """Represents the area calculation for a spectroscopic feature"""

    def _continuum_area(self, continuum: pd.Series) -> float:
        """The area under the pseudo continuum curve

        Args:
            continuum: The flux of the pseudo continuum
        """

        # Evaluate continuum at beginning and end of feature
        y1 = np.interp(self.wave.min(), continuum.index, continuum)
        y2 = np.interp(self.wave.max(), continuum.index, continuum)

        # Treat continuum as a straight-line and find the area underneath
        return (self.wave[-1] - self.wave[0]) * (y1 + y2) / 2

    def _flux_area(self) -> float:
        """The area under the flux curve"""

        return np.trapz(y=self.flux, x=self.wave)

    def area(self, continuum: pd.Series) -> float:
        """The area of the feature

        Area is determined between the sudo continuum of the binned flux
        and the flux values from the non-binned flux.

        Args:
            continuum: The flux of the pseudo continuum
        """

        return self._continuum_area(continuum) - self._flux_area()
