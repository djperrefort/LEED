import pandas as pd

from leed.accessors.base import Base


class calcPseudoContinuum(Base):
    """Fitting of the pseudo-continuum for a spectroscopic SN feature"""

    def fitPseudoContinuum(self) -> pd.Series:
        """Array of values for the fitted sudo continuum"""

        # Fit a line to the end points
        x0, x1 = self.wave[0], self.wave[-1]
        y0, y1 = self.flux[0], self.flux[-1]
        m = (y0 - y1) / (x0 - x1)
        b = - m * x0 + y0

        return pd.Series(m * self.wave + b, index=self.wave)
