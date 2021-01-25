from typing import Tuple, final

import numpy as np
import pandas as pd

from .calcArea import CalcArea
from .calcPEW import CalcPEW
from .calcPseudoContinuum import calcPseudoContinuum
from .calcVelocity import CalcVelocity
from ..app.settings import FeatureDefinition
from ..exceptions import FeatureNotObserved


@final
@pd.api.extensions.register_series_accessor('feature')
class FeatureAccessor(CalcArea, CalcPEW, CalcVelocity, calcPseudoContinuum):
    """Pandas accessor for calculating the properties of spectroscopic SN features"""

    def findPeakWavelength(self, lowerBound: float, upperBound: float, behavior: str = 'min') -> float:
        """Return wavelength of the maximum flux within given wavelength bounds

        The behavior argument can be used to select the 'min' or 'max' wavelength
        when there are multiple wavelengths having the same peak flux value. The
        default behavior is 'min'.

        Args:
            lowerBound: Lower wavelength boundary
            upperBound: Upper wavelength boundary
            behavior: Return the 'min' or 'max' wavelength when multiple maxima are found

        Returns:
            The wavelength for the maximum flux value
        """

        # Make sure the given spectrum spans the given wavelength bounds
        if not any((self.wave > lowerBound) & (self.wave < upperBound)):
            raise FeatureNotObserved('Feature not in spectral wavelength range.')

        # Select the portion of the spectrum within the given bounds
        featureIndices = (lowerBound <= self.wave) & (self.wave <= upperBound)
        featureFlux = self.flux[featureIndices]
        featureWavelength = self.wave[featureIndices]

        # Get peak according to specified behavior
        peakIndices = np.argwhere(featureFlux == np.max(featureFlux))
        behaviorFunc = getattr(np, behavior)
        return behaviorFunc(featureWavelength[peakIndices])

    def guessBounds(self, feature: FeatureDefinition) -> Tuple[float, float]:
        """Guess the observed start and end wavelengths for a given feature

        Args:
            feature: Feature definition to use when guessing bounds

        Returns:
            - The starting wavelength of the feature
            - The ending wavelength of the feature
        """

        featStart = self.findPeakWavelength(feature.lower_blue, feature.upper_blue, 'min')
        featEnd = self.findPeakWavelength(feature.lower_red, feature.upper_red, 'max')
        return featStart, featEnd
