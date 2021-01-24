from pathlib import Path
from typing import Any, List, Optional, Sequence, Union

import pandas as pd


def get_results_dataframe(fpath: Path = None) -> pd.DataFrame:
    """Load any existing results from a given file path

     Args:
         fpath: Path to load data from

    Returns:
        A pandas DataFrame indexed by ['obj_id', 'time', 'feat_name']
    """

    # Read existing results if they exist and make sure objectIds are strings
    if fpath is not None:
        if fpath.exists():
            data = pd.read_csv(fpath)
            data['obj_id'] = data['obj_id'].astype(str)
            return data.set_index(['obj_id', 'time', 'feat_name'])

        else:
            fpath.parent.mkdir(exist_ok=True, parents=True)

    col_names = ['obj_id', 'time', 'feat_name', 'feat_start', 'feat_end']
    for value in ('vel', 'pew', 'area'):
        col_names.append(value)
        col_names.append(value + '_err')
        col_names.append(value + '_samperr')

    col_names.append('spec_flag')
    col_names.append('feat_flag')
    col_names.append('notes')
    df = pd.DataFrame(columns=col_names)
    return df.set_index(['obj_id', 'time', 'feat_name'])


class BlockSignals:
    """Context manager that temporarily disables signal / slot communication

    Allows the modification GUI elements without triggering GUI behaviors
    """

    def __init__(self, attr: Any) -> None:
        """Store the current state of the given attribute

        Args:
           attr: QObject to block signals from
        """

        self.original_state = attr.signalsBlocked()
        self.attr = attr

    def __enter__(self) -> None:
        """Disable signal / slot communication"""

        self.attr.blockSignals(True)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Reset signal / slot communication to the original state"""

        self.attr.blockSignals(self.original_state)


class SpectralAccessor:
    def __init__(self, accessFunc: callable, objectIds: Sequence[str], groupBy: str = None) -> None:
        """Data Access Object for spectroscopic observations of Type Ia Supernovae

        Args:
            accessFunc: Callable object that returns supernova data for a given object Id
            objectIds: List of object Ids to provide access to
            groupBy: Group supernova data into individual spectra by the given column
        """

        if len(objectIds) == 0:
            raise ValueError('Object Id list cannot be empty')

        self._func = accessFunc
        self._objIds = objectIds
        self._groupBy = groupBy

        self._currentObjectIndex = -1
        self._currentSpectrumIndex = 0
        self._snData: Optional[pd.DataFrame] = None
        self.loadNextSN()

    @property
    def availableSNe(self) -> List[str]:
        """List of supernova Ids accessible by the current accessor instance"""

        return list(self._objIds)

    @property
    def currentSN(self) -> str:
        """Id value for the current supernova loaded into memory"""

        return self._objIds[self._currentObjectIndex]

    @property
    def availableSpecIds(self) -> List[Union[str, float, int]]:
        """List of available spectra for the current supernova"""

        if self._groupBy:
            return sorted(set(self._snData[self._groupBy]))

        return []

    def specForSN(self, objId: Optional[str] = None) -> List[Union[str, float, int]]:
        """Return a list of available spectra for a given supernova id

        Args:
            objId: Id of the supernova

        Returns:
            A list of spectrum Id's
        """

        if objId:
            return sorted(set(self._func(self.currentSN)[self._groupBy]))

    @property
    def currentSpecId(self) -> Union[str, float, int]:
        """Identifier for the current spectrum being accessed"""

        return self.availableSpecIds[self._currentSpectrumIndex]

    def loadNextSN(self) -> None:
        """Iterate to the next available supernova"""

        if self._currentObjectIndex >= len(self._objIds):
            raise StopIteration

        self._currentObjectIndex += 1
        self._snData = self._func(self.currentSN)
        if self._snData.empty:
            self.loadNextSN()

        self._currentSpectrumIndex = 0

    def loadPreviousSN(self) -> None:
        """Iterate to the previous available supernova"""

        if self._currentObjectIndex <= 0:
            raise StopIteration

        self._currentObjectIndex -= 1
        self._snData = self._func(self.currentSN)
        if self._snData.empty:
            self.loadPreviousSN()

        self._currentSpectrumIndex = min(len(self.availableSpecIds) - 1, 0)

    def loadNextSpectrum(self):
        """Iterate to the next available spectrum for the current supernova"""

        next_idx = self._currentSpectrumIndex + 1
        if next_idx >= len(self.availableSpecIds):
            raise StopIteration

        self._currentSpectrumIndex = next_idx

    def loadPreviousSpectrum(self):
        """Iterate to the previous available spectrum for the current supernova"""

        if self._currentSpectrumIndex <= 0:
            raise StopIteration

        self._currentSpectrumIndex -= 1

    @property
    def spectrum(self) -> pd.Series:
        """Data for the current supernova spectrum"""

        if self._groupBy is not None:
            return self._snData[self._snData[self._groupBy] == self.currentSpecId].flux

        return self._snData.flux

    def goTo(self, objId, specId):
        """Load data for the given object and spectrum Id

        Args:
            objId: The Id of the SNe to load data for
            specId: The Id of the spectrum to load

        Raises:
            ValueError: For an invalid object or spectrum Id
        """

        try:
            self._currentObjectIndex = self.availableSNe.index(objId)

        except ValueError:
            raise ValueError(f'Invalid object Id: {objId}')

        self._snData = self._func(self.currentSN)

        try:
            self._currentSpectrumIndex = self.availableSpecIds.index(specId)

        except ValueError:
            self._currentSpectrumIndex = 0
            raise ValueError(f'Invalid spectrum Id: {specId}')
