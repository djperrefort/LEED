from typing import Any


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
