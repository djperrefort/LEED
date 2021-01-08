class FeatureNotObserved(Exception):
    """Feature was not observed or does not span indicated wavelength range"""


class SamplingRangeError(Exception):
    """Resampling process extends beyond available wavelength range"""
