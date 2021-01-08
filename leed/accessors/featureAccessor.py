from typing import Tuple, final

import numpy as np
import pandas as pd

from .calcArea import CalcArea
from .calcPEW import CalcPEW
from .calcVelocity import CalcVelocity
from ..app.settings import FeatureDefinition
from ..exceptions import FeatureNotObserved


@final
@pd.api.extensions.register_series_accessor('feature')
class FeatureAccessor(CalcArea, CalcPEW, CalcVelocity):

    def find_peak_wavelength(self, lower_bound: float, upper_bound: float, behavior: str = 'min') -> float:
        """Return wavelength of the maximum flux within given wavelength bounds

        The behavior argument can be used to select the 'min' or 'max' wavelength
        when there are multiple wavelengths having the same peak flux value. The
        default behavior is 'min'.

        Args:
            lower_bound: Lower wavelength boundary
            upper_bound: Upper wavelength boundary
            behavior: Return the 'min' or 'max' wavelength when multiple maxima are found

        Returns:
            The wavelength for the maximum flux value
        """

        # Make sure the given spectrum spans the given wavelength bounds
        if not any((self.wave > lower_bound) & (self.wave < upper_bound)):
            raise FeatureNotObserved('Feature not in spectral wavelength range.')

        # Select the portion of the spectrum within the given bounds
        feature_indices = (lower_bound <= self.wave) & (self.wave <= upper_bound)
        feature_flux = self.flux[feature_indices]
        feature_wavelength = self.wave[feature_indices]

        # Get peak according to specified behavior
        peak_indices = np.argwhere(feature_flux == np.max(feature_flux))
        behavior_func = getattr(np, behavior)
        return behavior_func(feature_wavelength[peak_indices])

    def guess_bounds(self, feature: FeatureDefinition) -> Tuple[float, float]:
        """Guess the observed start and end wavelengths for a given feature

        Args:
            feature: Feature definition to use when guessing bounds

        Returns:
            - The starting wavelength of the feature
            - The ending wavelength of the feature
        """

        feat_start = self.find_peak_wavelength(feature.lower_blue, feature.upper_blue, 'min')
        feat_end = self.find_peak_wavelength(feature.lower_red, feature.upper_red, 'max')
        return feat_start, feat_end

    def fit_pseudo_continuum(self) -> np.array:
        """Array of values for the fitted sudo continuum"""

        # Fit a line to the end points
        x0, x1 = self.wave[0], self.wave[-1]
        y0, y1 = self.flux[0], self.flux[-1]
        m = (y0 - y1) / (x0 - x1)
        b = - m * x0 + y0

        return m * self.wave + b
