from PyQt5 import QtWidgets

from .baseWindow import BaseWindow
from ..utils import SpectralAccessor


class SpectrumSelection(BaseWindow):
    designFile = 'SpectrumSelection.ui'

    def __init__(self, dataAccess: SpectralAccessor, parent: QtWidgets.QMainWindow = None) -> None:
        super().__init__(parent)

        self.dataAccess = dataAccess
        self.comboBoxObjectId.addItems(dataAccess.availableSNe)
        self.comboBoxObjectId.currentTextChanged.connect(self.updateSpectrumCombo)

    def updateSpectrumCombo(self, newId: str) -> None:
        self.comboBoxSpectrumId.clear()
        specIds = self.dataAccess.specForSN(newId)
        if specIds:
            self.comboBoxSpectrumId.setDisabled(False)
            self.comboBoxSpectrumId.addItems((str(x) for x in specIds))

        else:
            self.comboBoxSpectrumId.setDisabled(True)

