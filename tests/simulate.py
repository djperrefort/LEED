"""The ``simulate`` module provides functions for simulating spectra
(wavlength and lfux arrays) with absorption features according to various
toy models. This is useful when testing or visualizing the behavior of an
analysis procedure.

Usage Examples:
---------------

We here demonstrate the simulation of an absoprion feature with a gaussian
profile. For a list of available profiles, see the API Documentation.

.. code-block:: python
   :linenos:

   import numpy as np
   from matplotlib import pyplot as plt
   from spectral_inspector.simulate import gaussian

   # Simulate a gaussian with a peak at 1200 wavelength units
   wave = np.arange(1000, 2000)
   flux, flux_err = gaussian(wave, stddev=100)

   # Visualize the result
   plt.errorbar(wave, flux, yerr=flux_err, linestyle='', alpha=.5, label='Error')
   plt.plot(wave, flux, color='k', label='Flux')
   plt.xlabel('Wavelength')
   plt.ylabel('Flux')
   plt.legend()
   plt.show()

API Documentation
-----------------
"""

import numpy as np
import pandas as pd


def tophat(wave, m=0, b=1, start=100, end=-100, height=0):
    """Simulate a top-hat absorption feature with normal errors

    Setting ``height=None`` will simulate just the continuum

    Args:
        wave (ndarray): Array of wavelengths to simulate flux for
        m      (float): Slope of the continuum (default: 0)
        b      (float): Y-intercept of the continuum (default: 1)
        start    (int): Starting index for the top-hat (default: 100)
        end      (int): Ending index for the top-hat (default: -100)
        height (float): Height of the top-hat  (default: 0)

    Returns:
        A simualted spectrum
    """

    flux = m * wave + b
    if height is not None:
        flux[start: end] = height

    return pd.Series(flux, index=wave)


def gaussian(wave, depth=-1, mean=None, stddev=1, offset=100):
    """Simulate gaussian flux with normal errors

    Args:
        wave    (ndarray): Array of wavelengths to simulate flux for
        depth (float): Amplitude of the Gaussian
        mean      (float): Average of the Gaussian (default: mean of wave)
        stddev    (float): Standard deviation of the Gaussian
        offset    (float): Vertical offset of the Gaussian

    Returns:
        - An array of flux values
        - An array of error values
    """

    mean = np.mean(wave) if mean is None else mean
    flux = depth * np.exp(
        -((wave - mean) ** 2) / (2 * stddev ** 2)
    ) + offset

    return pd.Series(flux, index=wave)


def delta_func(wave, m=0, b=0, peak_wave=(), amplitude=1, seed=None):
    """Simulate linear flux with interspersed delta functions

    Args:
        wave    (ndarray): Array of wavelengths to simulate flux for
        m         (float): Slope of the continuum
        b         (float): Y-intercept of the continuum
        peak_wave (tuple): Wavelengths of the delta functions
        amplitude (float): Height of the delta functions
        seed      (float): Optional seed for random number generator

    Returns:
        An array of flux values
    """

    flux = m * wave + b
    flux[np.isin(wave, peak_wave)] = amplitude
    np.random.seed(seed)
    return pd.Series(flux, index=wave)
