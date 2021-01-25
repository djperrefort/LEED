from typing import List, final

import extinction
import numpy as np
import pandas as pd
import sfdmap
import uncertainties as unc
from scipy.ndimage.filters import gaussian_filter, generic_filter, median_filter
from uncertainties.unumpy import nominal_values

from .base import Base
from ..app.settings import RESOURCES_DIR
from ..exceptions import SamplingRangeError

DUSTMAP = sfdmap.SFDMap(RESOURCES_DIR / 'schlegel98_dust_map')


@final
@pd.api.extensions.register_series_accessor('spectrum')
class SpectrumAccessor(Base):
    """Pandas accessor for manipulating spectroscopic data"""

    def bin(self, size: float, method: str) -> pd.Series:
        """Bin a spectrum to a given resolution

        Args:
            size: The width of the bins
            method: Either 'median', 'average', 'sum', or 'gauss'

        Returns:
            The binned spectrum as a new ``Series`` object

        Raises:
            ValueError: For an unknown binning method
        """

        if method == 'sum':
            return pd.Series(generic_filter(self.flux, sum, size), index=self.wave)

        elif method == 'average':
            return pd.Series(generic_filter(self.flux, np.average, size), index=self.wave)

        elif method == 'gauss':
            return pd.Series(gaussian_filter(self.flux, size), index=self.wave)

        elif method == 'median':
            return pd.Series(median_filter(self.flux, size), index=self.wave)

        raise ValueError(f'Unknown method {method}')

    def restFrame(self, z: float) -> pd.Series:
        """Convert spectrum wavelengths into the restframe

        Args:
            z: The redshift of the spectrum

        Returns:
            A copy of the current spectrum, redshifted to the restframe
        """

        out = self._obj.copy()
        out.index /= (1 + z)
        return out

    def correctExtinction(self, ra: float, dec: float, rv: float = 3.1) -> pd.Series:
        """Rest frame spectra and correct for MW extinction

        Spectra are corrected for MW extinction using the
        Schlegel et al. 98 dust map and the Fitzpatrick et al. 99 extinction
        law. If rv is not given, a value of 3.1 is used.

        Args:
            ra: Right Ascension of the object
            dec: Declination of the object
            rv: Rv value to use for extinction
        """

        # Determine extinction
        mwebv = DUSTMAP.ebv(ra, dec, frame='fk5j2000', unit='degree')
        magExt = extinction.fitzpatrick99(self.wave, rv * mwebv, rv)

        # Correct flux to rest-frame
        out = self._obj.copy()
        out /= 10 ** (0.4 * magExt)
        return out

    def sampleFeatureProperties(
            self, featStart: float, featEnd: float, restFrame: float, nstep: int = 0, callback: callable = None
    ) -> List[float]:
        """Calculate the properties of a single feature in a spectrum

        Velocity values are returned in km / s. Error values are determined
        both formally (summed in quadrature) and by re-sampling the feature
        boundaries ``nstep`` flux measurements in either direction.

        Args:
            featStart: Starting wavelength of the feature
            featEnd: Ending wavelength of the feature
            restFrame: Rest frame location of the specified feature
            nstep: Number of samples taken in each direction
            callback: Call a function after every iteration.
                Function is passed the sampled feature.

        Returns:
            - The line velocity
            - The formal error in velocity
            - The sampling error in velocity
            - The equivalent width
            - The formal error in equivalent width
            - The sampling error in equivalent width
            - The feature area
            - The formal error in area
            - The sampling error in area

        Raises:
            ValueError: When the start and end position of the feature are too close together
            SamplingRangeError: When the width of the feature is less than the number of samples
        """

        # Get indices for beginning and end of the feature
        idxStart = np.where(self.wave == featStart)[0][0]
        idxEnd = np.where(self.wave == featEnd)[0][0]
        if idxEnd - idxStart <= 10:
            raise ValueError('Range too small. Please select a wider range')
        print(idxStart, idxEnd)

        # We vary the beginning and end of the feature to estimate the error
        velocity, pEquivWidth, area = [], [], []
        for i in np.arange(-nstep, nstep + 1):
            for j in np.arange(nstep, -nstep - 1, -1):

                # Get sub-sampled wavelength/flux
                idxSampleStart = idxStart + i
                idxSampleEnd = idxEnd + j

                if idxSampleStart < 0 or idxSampleEnd >= len(self._obj):
                    raise SamplingRangeError

                # Determine feature properties
                sample = self._obj[idxSampleStart: idxSampleEnd]
                continuum = sample.feature.fitPseudoContinuum()
                velocity.append(sample.feature.velocity(restFrame))
                pEquivWidth.append(sample.feature.pew(continuum))
                area.append(sample.feature.area(continuum))

                if callback:
                    callback(sample)

        avgVelocity = np.mean(velocity)
        avgEw = np.mean(pEquivWidth)
        avgArea = np.mean(area)

        return [
            unc.nominal_value(avgVelocity),
            unc.std_dev(avgVelocity),
            np.std(nominal_values(velocity)),
            unc.nominal_value(avgEw),
            unc.std_dev(avgEw),
            np.std(nominal_values(pEquivWidth)),
            unc.nominal_value(avgArea),
            unc.std_dev(avgArea),
            np.std(nominal_values(area))
        ]
