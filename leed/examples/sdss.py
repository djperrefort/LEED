"""Launch the LEED app for SDSS spectra of confirmed SNe Ia."""

from typing import Dict

import numpy as np
import pandas as pd
from sndata.sdss import Sako18Spec
from sndata.utils import convert_to_jd

# Make sure data is downloaded to the local machine
from leed.app.utils import SpectralAccessor

sako_18_spec = Sako18Spec()
sako_18_spec.download_module_data()

# Load some data tables from the Sako et al. 2018 publication
sdss_master_table = sako_18_spec.load_table('master').to_pandas(index='CID')

# Specify minimum and maximum phase to include in returned data (inclusive)
min_phase = -15
max_phase = 15


def get_sdss_t0(obj_id):
    """Get the t0 value for CSP targets

    Args:
        obj_id (str): The object identifier

    Returns:
        The time of B-band maximum in units of

    Raises:
        ValueError: A published t0 values is not available from SDSS
    """

    # Unknown object ID
    if obj_id not in sdss_master_table.index:
        raise ValueError(f't0 not available for {obj_id}')

    t0_mjd = sdss_master_table.loc[obj_id]['PeakMJDSALT2zspec']

    # Known object Id with unknown peak time
    if np.isnan(t0_mjd):
        raise ValueError(f't0 not available for {obj_id}')

    return convert_to_jd(t0_mjd)


def get_sdss_meta(obj_id: str) -> Dict[str, float]:
    """Get object meta data published by SDSS for a given SN

    Args:
        obj_id: The object identifier

    Returns:
        The time of B-band maximum in units of MJD

    Raises:
        ValueError: Complete meta data is not available from CSP
    """

    return dict(t0=get_sdss_t0(obj_id))


def pre_process(spectral_data: pd.DataFrame, t0: float, ra: float, dec: float, z: float) -> pd.DataFrame:
    """Format data tables for use with the LEED app

    Changes:
        - Drops host galaxy spectra
        - Removes data with phases < ``min_phase`` and phases > ``max_phase``
        - Shifts wavelengths to the rest frame
        - Corrects for MilkyWay extinction

    Args:
        spectral_data: DataFrame with CSP DR1 spectral data
        t0: Time of the peak B-band maximum brightness for the given SN
        ra: Right ascension of the SN
        dec: Declination of the Sn
        z: Redshift of the given SN

    Returns:
        A modified copy of the input dataframe
    """

    phase = spectral_data['time'] - t0

    spectral_data = spectral_data[spectral_data['type'] != 'Gal']
    spectral_data = spectral_data[(min_phase <= phase) & (phase <= max_phase)]

    spectral_data = spectral_data \
        .spectrum.correctExtinction(ra, dec) \
        .spectrum.restFrame(z)

    # Restframe the spectrum
    return spectral_data


def get_data(obj_id: str) -> pd.DataFrame:
    """Get SDSS spectral data for a given object Id

    Args:
        obj_id: The Id of the object to get data for

    Returns:
        A DataFrame of spectral data pre-processed for use with the LEED app
    """

    try:
        object_meta_data = get_sdss_t0(obj_id)

    except ValueError:
        raise

    return pre_process(sako_18_spec.get_data_for_id(obj_id).to_pandas(), **object_meta_data)


def run_sdss(out_path: str) -> None:
    """Run the LEED application on SDSS spectra

    Args:
        out_path: Name of CSV file where results are saved
    """

    from ..app import run
    accessor = SpectralAccessor(get_data, sako_18_spec.get_available_ids(), 'time')
    run(accessor, out_path)
