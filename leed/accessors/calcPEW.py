import numpy as np
import pandas as pd

from leed.accessors.base import Base


class CalcPEW(Base):
    """Represents the pEW calculation for a spectroscopic feature"""

    def pew(self, continuum: pd.Series) -> float:
        """Calculate the pseudo equivalent-width of the feature

        Returns:
            The pseudo equivalent-width of the feature
        """

        return (self.wave[-1] - self.wave[0]) - np.trapz(y=(self._obj / continuum), x=self.wave)
