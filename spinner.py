from PyQt5.QtWidgets import QLabel
from pyqtspinner import WaitingSpinner

class SpinnerUtility:
    def __init__(self, parent):
        print("initiating spinner")
        """Initialize the spinner with the given parent widget."""
        self.label = QLabel(parent)
        self.spinner = WaitingSpinner(self.label)
        self.spinner.setMinimumSize(100, 100)  # Set a minimum size for visibility

        # Center the spinner in the parent window
        self.label.setGeometry(
            (parent.width() - 50) // 2, 
            (parent.height() - 50) // 2, 
            50, 
            50
        )
        self.label.hide()  # Initially hide the label

    def start_spinner(self):
        """Start the spinner animation."""
        print("starting spinner")
        self.label.show()  # Show the label
        self.spinner.start()

    def stop_spinner(self):
        """Stop the spinner animation."""
        print("stoping spinner")
        self.spinner.stop()
        self.label.hide()  # Hide the label after stopping
