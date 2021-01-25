from dataclasses import dataclass

import numpy as np
from astropy import units
from astropy.constants import c
from scipy.optimize import curve_fit

from leed.accessors.base import Base


@dataclass
class GaussianFit:
    """Basic wrapper to provide easy access to fitted Gaussian parameters"""

    amplitude: float
    avg: float
    stdDev: float
    offset: float
    cov: np.array

    @property
    def amplitudeErr(self) -> None:  # pragma: no cover
        return np.sqrt(self.cov[0][0])

    @property
    def avgErr(self) -> None:  # pragma: no cover
        return np.sqrt(self.cov[1][1])

    @property
    def stdDevErr(self) -> None:  # pragma: no cover
        return np.sqrt(self.cov[2][2])

    @property
    def offsetErr(self) -> None:  # pragma: no cover
        return np.sqrt(self.cov[3][3])


class CalcVelocity(Base):
    """Represents the velocity calculation for a spectroscopic feature"""

    @staticmethod
    def gaussian(x: np.array, depth: float, avg: float, std: float, offset: float) -> np.array:
        """Evaluate a negative gaussian

        f = -depth * e^(-((x - avg)^2) / (2 * std ** 2)) + offset

        Args:
            x: Values to evaluate the gaussian at
            depth: Amplitude of the gaussian
            avg: Average of the gaussian
            std: Standard deviation of the gaussian
            offset: Vertical offset

        Returns:
            The evaluated gaussian
        """

        return -depth * np.exp(-((x - avg) ** 2) / (2 * std ** 2)) + offset

    def _fitGaussian(self) -> GaussianFit:
        """Fitted an negative gaussian to the binned flux

        Returns:
            A list of fitted parameters
        """

        try:
            gaussParams, cov = curve_fit(
                f=self.gaussian,
                xdata=self.wave,
                ydata=self.flux,
                p0=[0.5, np.median(self.wave), 50., 0])

        except RuntimeError:
            gaussParams = [np.nan, np.nan, np.nan, np.nan]
            cov = np.full((4, 4), np.nan)

        return GaussianFit(*gaussParams, cov)

    def velocity(self, restFrame: float) -> float:
        """Calculate the velocity of a feature

        Fit a feature with a negative gaussian and determine the feature's
        velocity. Returned value is ``np.nan`` if the fit fails.
        
        Args:
            restFrame: The rest frame wavelength of the feature

        Returns:
            The velocity of the feature in km / s
        """

        gaussFit = self._fitGaussian()

        # Calculate velocity
        unit = units.km / units.s
        speedOfLight = c.to(unit).value
        return speedOfLight * (
                ((((restFrame - gaussFit.avg) / restFrame) + 1) ** 2 - 1) /
                ((((restFrame - gaussFit.avg) / restFrame) + 1) ** 2 + 1)
        )
