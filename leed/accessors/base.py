import numpy as np

import pandas as pd


class Base:
    """Base class to use for constructing pandas accessors for spectral data."""

    def __init__(self, obj: pd.Series) -> None:
        self._obj = obj
        # self._validate()

    def _validate(self):
        """Raise an error if the pandas object is not sorted."""

        if not self._obj.index.is_monotonic:
            raise RuntimeError('Series index must be sorted')

    @property
    def wave(self) -> np.array:
        """Return index values as an array."""

        return self._obj.index.values

    @property
    def flux(self) -> np.array:
        """Return series data as an array."""

        return self._obj.values
