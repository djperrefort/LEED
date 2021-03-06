from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Tuple

import yaml
from PyQt5.QtGui import QBrush, QColor, QPen

RESOURCES_DIR: Path = Path(__file__).resolve().parent.parent / 'resources'
SETTINGS_PATH = RESOURCES_DIR / 'settings.yml'


@dataclass
class Settings:
    """Generic class for representing package settings"""

    def asDict(self) -> dict:
        """Return the settings instance as a dictionary"""

        out_dict = dict()
        for annotation in self.__dataclass_fields__:
            attr = getattr(self, annotation)

            if hasattr(attr, 'asDict'):
                out_dict[annotation] = attr.asDict()

            elif isinstance(attr, (List, Tuple)):
                out_dict[annotation] = [a.asDict() for a in attr]

            else:
                out_dict[annotation] = attr

        return out_dict

    def __getitem__(self, item):
        if item in self.__dataclass_fields__:
            return getattr(self, item)

        raise IndexError(f'No dataclass field names {item}')

    def __str__(self) -> str:
        return str(self.asDict())


@dataclass
class FeatureDefinition(Settings):
    """Settings for the automated search of a spectral feature"""

    feature_id: str
    lower_blue: float
    lower_red: float
    restframe: float
    upper_blue: float
    upper_red: float
    enabled: int = 2


@dataclass
class SpectralProcessingSettings(Settings):
    """Settings used when correcting for extinction and binning the spectra"""

    nstep: int = 5
    rv: float = 3.1
    bin_size: float = 10
    bin_method: str = 'median'


@dataclass
class ColorSettings(Settings):
    r: int
    g: int
    b: int
    a: int

    def asColor(self) -> QColor:
        """Use settings values to instantiate a ``QColor``  object"""

        return QColor(self.r, self.g, self.b, self.a)

    def toCSS(self) -> str:
        """Return the color as RGBA in CSS format"""

        return f'rgba({self.r}, {self.g}, {self.b}, {self.a})'


@dataclass
class BrushSettings(Settings):
    """Style arguments for brush elements"""

    color: ColorSettings

    def asBrush(self) -> QBrush:
        """Use settings values to instantiate a ``QBrush`` object"""

        return QBrush(self.color.asColor())


@dataclass
class PenSettings(BrushSettings):
    """Style arguments for pen elements"""

    width: float

    def asPen(self) -> QPen:
        """Use settings values to instantiate a ``QPen``  object"""

        pen = QPen(self.color.asColor())
        pen.setWidth(self.width)
        return pen


@dataclass
class PlotSettings(Settings):
    """Collection of ``PenSettings`` defining the visual style of a plot"""

    show_observed_flux: int
    observed_flux: PenSettings
    binned_flux: PenSettings
    fitted_feature: PenSettings
    boundary: PenSettings
    saved_feature: BrushSettings
    start_region: BrushSettings
    end_region: BrushSettings


@dataclass
class ApplicationSettings(Settings):
    """Settings accessor for the current application"""

    prepare: SpectralProcessingSettings
    features: List[FeatureDefinition]
    plotting: PlotSettings

    @classmethod
    def _load_from_disk(cls, path: Optional[Path] = None) -> ApplicationSettings:
        """Load settings from a file on disk

        Returns default setting values if the path does not exist

        Args:
            path: The path to load data from (defaults to internal package path)

        Returns:
            An ``ApplicationSettings`` instance reflecting the on disk data
        """

        # Ensure that a copy of the application settings is available on disk
        path = path or SETTINGS_PATH
        if not path.exists():
            settings = SettingsLoader(defaults=True)
            settings.saveToDisk()
            return settings

        with path.open() as infile:
            settings_data = yaml.safe_load(infile)

        # Construct ApplicationSettings instance using data from disk
        plot_settings = settings_data['plotting']
        return ApplicationSettings(
            prepare=SpectralProcessingSettings(**settings_data['prepare']),
            features=[FeatureDefinition(**f) for f in settings_data['features']],
            plotting=PlotSettings(
                show_observed_flux=2,
                observed_flux=PenSettings(ColorSettings(**plot_settings['observed_flux']['color']), plot_settings['observed_flux']['width']),
                binned_flux=PenSettings(ColorSettings(**plot_settings['binned_flux']['color']), plot_settings['binned_flux']['width']),
                fitted_feature=PenSettings(ColorSettings(**plot_settings['fitted_feature']['color']), plot_settings['fitted_feature']['width']),
                boundary=PenSettings(ColorSettings(**plot_settings['boundary']['color']), plot_settings['boundary']['width']),
                saved_feature=BrushSettings(ColorSettings(**plot_settings['saved_feature']['color'])),
                start_region=BrushSettings(ColorSettings(**plot_settings['start_region']['color'])),
                end_region=BrushSettings(ColorSettings(**plot_settings['end_region']['color']))
            )
        )

    def saveToDisk(self, path: Path = None) -> None:
        """Save current settings to disk

        Args:
            path: The path to load data from (defaults to internal package path)
        """

        path = path or SETTINGS_PATH
        path.parent.mkdir(exist_ok=True, parents=True)

        data = self.asDict()
        with path.open('w') as ofile:
            yaml.dump(data, ofile)

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


class SettingsLoader:
    """Class for loading saved application settings"""

    def __new__(cls, defaults: bool = False) -> ApplicationSettings:
        """Load application settings

        Args:
            defaults: Load default application settings instead of using settings saved on disk
        """

        if defaults:
            return ApplicationSettings(
                # ALL default application settings are defined here
                prepare=SpectralProcessingSettings(5, 3.1, 10, 'median'),
                features=[
                    FeatureDefinition('Ca II H & K', 3500.0, 3900.0, 3945.02, 3800.0, 4100.0, 2),
                    FeatureDefinition('Si II λ4130', 3900.0, 4000.0, 4129.78, 4000.0, 4150.0, 2),
                    FeatureDefinition('Mg II, Fe II', 3900.0, 4450.0, 4481.0, 4150.0, 4700.0, 2),
                    FeatureDefinition('Fe II, Si II', 4500.0, 5050.0, 5169.0, 4700.0, 5550.0, 2),
                    FeatureDefinition('S II λ5449, λ5622', 5150.0, 5500.0, 5535.5, 5300.0, 5700.0, 2),
                    FeatureDefinition('Si II λ5972', 5550.0, 5800.0, 5971.89, 5700.0, 6000.0, 2),
                    FeatureDefinition('Si II λ6355', 5800.0, 6200.0, 6356.08, 6000.0, 6600.0, 2),
                    FeatureDefinition('Ca II IR triplet', 7500.0, 8200.0, 8578.79, 8000.0, 8900.0, 2),
                ],
                plotting=PlotSettings(
                    show_observed_flux=2,
                    observed_flux=PenSettings(ColorSettings(0, 90, 120, 50), 1.),
                    binned_flux=PenSettings(ColorSettings(0, 0, 0, 255), 1.),
                    fitted_feature=PenSettings(ColorSettings(255, 0, 0, 255), 1.),
                    boundary=PenSettings(ColorSettings(255, 0, 0, 255), 3.),
                    saved_feature=BrushSettings(ColorSettings(0, 180, 0, 75)),
                    start_region=BrushSettings(ColorSettings(0, 0, 255, 50)),
                    end_region=BrushSettings(ColorSettings(255, 0, 0, 50))
                )
            )

        else:
            return ApplicationSettings._load_from_disk()
