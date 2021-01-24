from typing import final

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

dust_map = sfdmap.SFDMap(RESOURCES_DIR / 'schlegel98_dust_map')


@final
@pd.api.extensions.register_series_accessor('spectrum')
class SpectrumAccessor(Base):

    def bin_spectrum(self, bin_size, bin_method):
        """Bin a spectrum to a given resolution

        Args:
            bin_size (float): The width of the bins
            bin_method (str): Either 'median', 'average', 'sum', or 'gauss'
        """

        if bin_method == 'sum':
            return pd.Series(generic_filter(self.flux, sum, bin_size), index=self.wave)

        elif bin_method == 'average':
            return pd.Series(generic_filter(self.flux, np.average, bin_size), index=self.wave)

        elif bin_method == 'gauss':
            return pd.Series(gaussian_filter(self.flux, bin_size), index=self.wave)

        elif bin_method == 'median':
            return pd.Series(median_filter(self.flux, bin_size), index=self.wave)

        raise ValueError(f'Unknown method {bin_method}')

    def restframe(self, z):
        """Convert spectrum wavelengths into the restframe"""

        out = self._obj.copy()
        out._obj.index /= (1 + z)
        return out

    def correct_extinction(self, ra, dec, rv=3.1):
        """Rest frame spectra and correct for MW extinction

        Spectra are rest-framed and corrected for MW extinction using the
        Schlegel et al. 98 dust map and the Fitzpatrick et al. 99 extinction
        law. if rv is not given, a value of 3.1 is used.

        Args:
            rv  (float): Rv value to use for extinction
        """

        # Determine extinction
        mwebv = dust_map.ebv(ra, dec, frame='fk5j2000', unit='degree')
        mag_ext = extinction.fitzpatrick99(self.wave, rv * mwebv, rv)

        # Correct flux to rest-frame
        out = self._obj.copy()
        out /= 10 ** (0.4 * mag_ext)
        return out

    def sample_feature_properties(self, feat_start, feat_end, rest_frame, nstep=0, callback=None):
        """Calculate the properties of a single feature in a spectrum

        Velocity values are returned in km / s. Error values are determined
        both formally (summed in quadrature) and by re-sampling the feature
        boundaries ``nstep`` flux measurements in either direction.

        Args:
            feat_start  (float): Starting wavelength of the feature
            feat_end    (float): Ending wavelength of the feature
            rest_frame  (float): Rest frame location of the specified feature
            nstep         (int): Number of samples taken in each direction
            callback (callable): Call a function after every iteration.
                Function is passed the sampled feature.

        Returns:
            - The line velocity
            - The formal error in velocity
            - The sampling error in velocity
            - The equivalent width
            - The formal error in equivalent width
            - The sampling error in equivalent width
            - The feature calc_area
            - The formal error in calc_area
            - The sampling error in calc_area
        """

        # Get indices for beginning and end of the feature
        idx_start = np.where(self._obj.index == feat_start)[0][0]
        idx_end = np.where(self._obj.index == feat_end)[0][0]
        if idx_end - idx_start <= 10:
            raise ValueError('Range too small. Please select a wider range')

        # We vary the beginning and end of the feature to estimate the error
        velocity, pequiv_width, area = [], [], []
        for i in np.arange(-nstep, nstep + 1):
            for j in np.arange(nstep, -nstep - 1, -1):

                # Get sub-sampled wavelength/flux
                sample_start_idx = idx_start + i
                sample_end_idx = idx_end + j

                if sample_start_idx < 0 or sample_end_idx >= len(self._obj):
                    raise SamplingRangeError

                # Determine feature properties
                sample = self._obj[sample_start_idx: sample_end_idx]
                velocity.append(sample.feature.velocity(rest_frame))
                pequiv_width.append(sample.feature.pew())
                area.append(sample.feature.area())

                if callback:
                    callback(sample)

        avg_velocity = np.mean(velocity)
        avg_ew = np.mean(pequiv_width)
        avg_area = np.mean(area)

        return [
            unc.nominal_value(avg_velocity),
            unc.std_dev(avg_velocity),
            np.std(nominal_values(velocity)),
            unc.nominal_value(avg_ew),
            unc.std_dev(avg_ew),
            np.std(nominal_values(pequiv_width)),
            unc.nominal_value(avg_area),
            unc.std_dev(avg_area),
            np.std(nominal_values(area))
        ]
