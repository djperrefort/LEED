from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional, Tuple
from warnings import warn

import yaml
from PyQt5.QtGui import QBrush, QColor, QPen

RESOURCES_DIR: Path = Path(__file__).resolve().parent.parent / 'resources'
DEFAULT_SETTINGS_PATH = RESOURCES_DIR / 'settings.yml'


@dataclass
class Settings:
    """Generic class for representing package settings"""

    def asdict(self) -> dict:
        """Return the settings instance as a dictionary"""

        return asdict(self)

    def __str__(self) -> str:
        return str(self.asdict())


@dataclass
class FeatureDefinition(Settings):
    """Settings for the automated search of a spectral feature"""

    enabled: int
    feature_id: str
    lower_blue: float
    lower_red: float
    restframe: float
    upper_blue: float
    upper_red: float


@dataclass
class SpectralProcessingSettings(Settings):
    """Settings used when correcting for extinction and binning the spectra"""

    nstep: int = 5
    rv: float = 3.1
    bin_size: float = 10
    bin_method: str = 'median'


@dataclass
class PenSettings(Settings):
    """Style arguments for pen elements"""

    color: Tuple[int, int, int, int]  # in rgba format
    width: Optional[int] = None

    def asColor(self) -> QColor:
        """Use settings values to instantiate a ``QColor``  object"""

        return QColor(*self.color)

    def asPen(self) -> QPen:
        """Use settings values to instantiate a ``QPen``  object"""

        pen = QPen(self.asColor())
        pen.setWidth(self.width)
        return pen

    def asBrush(self) -> QBrush:
        """Use settings values to instantiate a ``QBrush`` object"""

        return QBrush(self.asColor())

    def toCSS(self) -> str:
        """Return the color as RGBA in CSS format"""

        return f'rgba({self.color[0]}, {self.color[1]}, {self.color[2]}, {self.color[3]})'


@dataclass
class PlotSettings(Settings):
    """Collection of ``PenSettings`` defining the visual style of a plot"""

    hide_observed_flux: int
    observed_flux: PenSettings
    binned_flux: PenSettings
    fitted_feature: PenSettings
    boundary: PenSettings
    saved_feature: PenSettings
    start_region: PenSettings
    end_region: PenSettings

    def asdict(self) -> dict:
        """Return the settings instance as a dictionary"""

        return dict(
            hide_observed_flux=self.hide_observed_flux,
            observed_flux=self.observed_flux.asdict(),
            binned_flux=self.binned_flux.asdict(),
            fitted_feature=self.fitted_feature.asdict(),
            boundary=self.boundary.asdict(),
            start_region=self.start_region.asdict(),
            end_region=self.end_region.asdict(),
        )


@dataclass
class ApplicationSettings:
    """Settings accessor for the current application"""

    # All default application settings are defined here
    prepare: SpectralProcessingSettings = SpectralProcessingSettings(5, 3.1, 10, 'median')
    features: List[FeatureDefinition] = (
        FeatureDefinition(2, 'Ca II H & K', 3500.0, 3900.0, 3945.02, 3800.0, 4100.0),
        FeatureDefinition(2, 'Si II λ4130', 3900.0, 4000.0, 4129.78, 4000.0, 4150.0),
        FeatureDefinition(2, 'Mg II, Fe II', 3900.0, 4450.0, 4481.0, 4150.0, 4700.0),
        FeatureDefinition(2, 'Fe II, Si II', 4500.0, 5050.0, 5169.0, 4700.0, 5550.0),
        FeatureDefinition(2, 'S II λ5449, λ5622', 5150.0, 5500.0, 5535.5, 5300.0, 5700.0),
        FeatureDefinition(2, 'Si II λ5972', 5550.0, 5800.0, 5971.89, 5700.0, 6000.0),
        FeatureDefinition(2, 'Si II λ6355', 5800.0, 6200.0, 6356.08, 6000.0, 6600.0),
        FeatureDefinition(2, 'Ca II IR triplet', 7500.0, 8200.0, 8578.79, 8000.0, 8900.0),
    )
    plotting: PlotSettings = PlotSettings(
        hide_observed_flux=0,
        observed_flux=PenSettings((0, 90, 120, 50), 1),
        binned_flux=PenSettings((0, 0, 0, 255), 1),
        fitted_feature=PenSettings((255, 0, 0, 255), 1),
        boundary=PenSettings((255, 0, 0, 255), 3),
        saved_feature=PenSettings((0, 180, 0, 75)),
        start_region=PenSettings((0, 0, 255, 50)),
        end_region=PenSettings((255, 0, 0, 50))
    )

    def loadFromDisk(self, path: Optional[Path] = None) -> ApplicationSettings:
        """Load settings from a file on disk

        Args:
            path: The path to load data from (defaults to internal package path)

        Returns:
            An ``ApplicationSettings`` instance reflecting the on disk data
        """

        try:
            return self._load_from_disk(path)

        except Exception as e:
            warn(f'Could not parse settings file from disk: {e}')
            return ApplicationSettings()

    @staticmethod
    def _load_from_disk(path: Optional[Path] = None) -> ApplicationSettings:
        """Load settings from a file on disk

        Args:
            path: The path to load data from (defaults to internal package path)

        Returns:
            An ``ApplicationSettings`` instance reflecting the on disk data
        """

        path = path or DEFAULT_SETTINGS_PATH
        if not path.exists():
            return ApplicationSettings()

        with path.open() as infile:
            settings_data = yaml.safe_load(infile)

        plot_settings = settings_data.get('plot_settings', dict())
        return ApplicationSettings(
            prepare=SpectralProcessingSettings(**settings_data.get('prepare', dict())),
            features=[FeatureDefinition(**f) for f in settings_data.get('features', [])],
            plotting=PlotSettings(
                hide_observed_flux=0,
                observed_flux=plot_settings.get('observed_flux', dict()),
                binned_flux=plot_settings.get('binned_flux', dict()),
                fitted_feature=plot_settings.get('fitted_feature', dict()),
                boundary=plot_settings.get('boundary', dict()),
                saved_feature=plot_settings.get('saved_feature', dict()),
                start_region=plot_settings.get('start_region', dict()),
                end_region=plot_settings.get('end_region', dict())
            )
        )

    def asdict(self) -> dict:
        """Return the settings instance as a dictionary"""

        return dict(
            prepare=self.prepare.asdict(),
            features=[f.asdict() for f in self.features]
        )

    def saveToDisk(self, path: Path = None) -> None:
        """Save current settings to disk

        Args:
            path: The path to load data from (defaults to internal package path)
        """

        path = path or DEFAULT_SETTINGS_PATH
        path.parent.mkdir(exist_ok=True, parents=True)
        with path.open('w') as ofile:
            yaml.dump(self.asdict(), ofile)

    @property
    def defaults(self) -> ApplicationSettings:
        """The default application settings"""

        return ApplicationSettings()

    @property
    def layout_dir(self) -> Path:
        """Return file path of the UI layout for the current window"""

        return RESOURCES_DIR / 'gui_layouts'

    @staticmethod
    def get_dust_map_dir(map_name) -> Path:
        """Return location of dust map data compatible with the ``extinction`` package

        Args:
            map_name: Name of the dust map

        Returns:
            A Path object pointing to the dust map directory
        """

        return RESOURCES_DIR / f'{map_name}_dust_map'
