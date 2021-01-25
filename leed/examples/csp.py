"""Launch the LEED app for CSP DR1 spectra of confirmed SNe Ia."""

from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sndata.csp import DR1, DR3
from sndata.utils import convert_to_jd, hourangle_to_degrees

from ..app.utils import SpectralAccessor
from ..accessors import spectrumAccessor

# Make sure data is downloaded to the local machine
dr1 = DR1()
dr1.download_module_data()

dr3 = DR3()
dr3.download_module_data()

# Load some data tables from the CSP DR1 publication
csp_table_1 = dr3.load_table(1).to_pandas(index='SN')
csp_table_3 = dr3.load_table(3).to_pandas(index='SN')

# Specify minimum and maximum phase to include in returned data (inclusive)
min_phase = -15
max_phase = 15


def get_csp_t0(obj_id: str) -> float:
    """Get the t0 value of a CSP observed SN

    Args:
        obj_id: The object identifier

    Returns:
        The time of B-band maximum in units of MJD

    Raises:
        ValueError: A published t0 values is not available from CSP
    """

    # Unknown object ID
    if obj_id not in csp_table_3.index:
        raise ValueError(f't0 not available for {obj_id}')

    t0_mjd = csp_table_3.loc[obj_id]['T(Bmax)']

    # Known object Id with unknown peak time
    if np.isnan(t0_mjd):
        raise ValueError(f't0 not available for {obj_id}')

    return convert_to_jd(t0_mjd)


def get_csp_ra_dec(obj_id: str) -> Tuple[float, float]:
    """Get the coordinates of a CSP observed SN

    Args:
        obj_id: The object identifier

    Returns:
        The RA and Dec of the SN in degrees
    """

    ra_dec_col_names = ['RAh', 'RAm', 'RAs', 'DE-', 'DEd', 'DEm', 'DEs']
    return hourangle_to_degrees(*csp_table_1.loc[obj_id][ra_dec_col_names])


def get_csp_meta(obj_id: str) -> Dict[str, float]:
    """Get object meta data published by CSP for a given SN

    Args:
        obj_id: The object identifier

    Returns:
        The time of B-band maximum in units of MJD

    Raises:
        ValueError: Complete meta data is not available from CSP
    """

    ra, dec = get_csp_ra_dec(obj_id)
    return dict(t0=get_csp_t0(obj_id), ra=ra, dec=dec)


def pre_process(spectral_data: pd.DataFrame, t0: float, ra: float, dec: float) -> pd.DataFrame:
    """Format data tables for use with the LEED app

    Changes:
        - Corrects for MilkyWay extinction
        - Removes data with phases < ``min_phase`` and phases > ``max_phase``

    Args:
        spectral_data: DataFrame with CSP DR1 spectral data
        t0: Time of the peak B-band maximum brightness for the given SN
        ra: Right ascension of the SN
        dec: Declination of the Sn

    Returns:
        A modified copy of the input dataframe
    """

    phase = spectral_data['time'] - t0
    spectral_data = spectral_data[(min_phase <= phase) & (phase <= max_phase)]
    spectral_data.flux = spectral_data.flux.spectrum.correctExtinction(ra, dec)

    return spectral_data


def get_data(obj_id: str) -> pd.DataFrame:
    """Get CSP spectral data for a given object Id

    Args:
        obj_id: The Id of the object to get data for

    Returns:
        A DataFrame of spectral data pre-processed for use with the LEED app
    """

    try:
        object_meta_data = get_csp_meta(obj_id)

    except ValueError:
        # Use standard column names for DR1 tables
        return pd.DataFrame(
            columns=['time', 'wavelength', 'flux', 'epoch', 'wavelength_range', 'telescope', 'instrument']
        )

    return pre_process(dr1.get_data_for_id(obj_id).to_pandas('wavelength'), **object_meta_data)


def run_csp_dr1(out_path: str) -> None:
    """Run the LEED application on CSP DR1 spectra

    Args:
        out_path: Name of CSV file where results are saved
    """

    from ..app import run
    accessor = SpectralAccessor(get_data, dr1.get_available_ids(), 'time')
    run(accessor, out_path)
