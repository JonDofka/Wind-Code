import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QListWidget, QWidget, QLabel
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mplcursors  # Import the mplcursors library

class PlotWindow(QMainWindow):
    def __init__(self, figure):
        super().__init__()
        self.setWindowTitle("Plot")
        self.setGeometry(100, 100, 800, 600)
        self.showMaximized()  # Open the window in full-screen mode

        # Create a central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add the matplotlib canvas to the layout
        self.canvas = FigureCanvas(figure)
        layout.addWidget(self.canvas)

        # Enable mplcursors to show labels when hovering over lines
        self.cursor = mplcursors.cursor(hover=True)


class CSVPlotterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('CSV Plotter')
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Create selection buttons
        self.label = QLabel("Select File Type to Load:", self)
        self.layout.addWidget(self.label)

        self.frt_button = QPushButton("FRT Files", self)
        self.frt_button.clicked.connect(lambda: self.load_files(file_type="frt"))
        self.layout.addWidget(self.frt_button)

        self.logger_button = QPushButton("Logger Files", self)
        self.logger_button.clicked.connect(lambda: self.load_files(file_type="logger"))
        self.layout.addWidget(self.logger_button)

        # Label to display currently loaded file type
        self.loaded_files_label = QLabel("Loaded Files: None", self)
        self.layout.addWidget(self.loaded_files_label)

    def select_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select CSV Files", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if files:
            self.file_list.clear()
            self.file_list.addItems(files)
            self.load_columns(files[0])  # Load columns from the first file

    def load_columns(self, file_path):
        self.column_list.clear()
        df = pd.read_csv(file_path)
        self.column_list.addItems(df.columns)
    
    def plot_data(self):
        selected_files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        selected_columns = [item.text() for item in self.column_list.selectedItems()]  # Get selected columns

        if not selected_files or not selected_columns:
            return

        # Create a new figure for the plot
        figure = Figure()
        ax = figure.add_subplot(111)

        # Store the lines and their labels for mplcursors
        self.lines = []  # Store all line objects
        self.labels = []  # Store corresponding labels

        for file in selected_files:
            df = pd.read_csv(file)
            for column in selected_columns:
                if column in df.columns:
                    line, = ax.plot(df[column], linewidth=2, alpha=0.7, picker=True, pickradius=5)  # Enable picking
                    self.lines.append(line)
                    self.labels.append(f'{os.path.basename(file)} - {column}')

        ax.set_xlabel('Index')
        ax.set_ylabel('Value')
        ax.set_title(f'Plot of {", ".join(selected_columns)}')

        # Create a new window for the plot
        self.plot_window = PlotWindow(figure)
        self.plot_window.show()

        # QLabel for showing the selected line (legend popup)
        self.legend_label = QLabel(self.plot_window)
        self.legend_label.setStyleSheet("font-size: 14px; font-weight: bold; background-color: white; padding: 5px; border: 1px solid black;")
        self.legend_label.setAlignment(Qt.AlignCenter)
        self.legend_label.setVisible(False)  # Hide initially

        # Connect mplcursors to show tooltips on hover
        cursor = mplcursors.cursor(self.lines, hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(self.labels[self.lines.index(sel.artist)]))

        # Connect the click event to highlight a line and show legend popup
        figure.canvas.mpl_connect('pick_event', self.on_line_click)

    def on_line_click(self, event):
        """Highlight the selected line, make others transparent, and show a legend popup."""
        clicked_line = event.artist  # Get the clicked line
        selected_label = self.labels[self.lines.index(clicked_line)]  # Get label for clicked line

        for line in self.lines:
            if line == clicked_line:
                line.set_alpha(1.0)  # Highlight the selected line
                line.set_linewidth(3)
            else:
                line.set_alpha(0.2)  # Make other lines transparent
                line.set_linewidth(1)

        # Show and update the legend popup
        self.legend_label.setText(selected_label)
        self.legend_label.adjustSize()
        self.legend_label.move(20, 20)  # Position at the top-left of the window
        self.legend_label.setVisible(True)

        event.canvas.draw()  # Update the plot



    def load_files(self, file_type, folder_path="Wind_Faults"):
        # Clear the UI and switch to main interface
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget not in [self.label, self.frt_button, self.logger_button, self.loaded_files_label]:
                widget.setParent(None)

        # Update the loaded files label
        self.loaded_files_label.setText(f"Loaded Files: {file_type.capitalize()}")

        # Add main UI elements
        self.file_list = QListWidget(self)
        self.file_list.setFixedHeight(100)  # Set a smaller height for the file list
        self.layout.addWidget(self.file_list)

        self.column_label = QLabel('Select Columns to Plot:', self)
        self.layout.addWidget(self.column_label)

        self.column_list = QListWidget(self)
        self.column_list.setSelectionMode(QListWidget.MultiSelection)
        self.layout.addWidget(self.column_list)

        self.plot_button = QPushButton('Plot', self)
        self.plot_button.clicked.connect(self.plot_data)
        self.layout.addWidget(self.plot_button)

        # Load files based on type
        if not os.path.exists(folder_path):
            print(f"Folder '{folder_path}' not found!")
            return

        if file_type == "frt":
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if "_frt" in f and f.endswith(".csv")]
        else:  # Logger files
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if "_frt" not in f and f.endswith(".csv")]

        if files:
            self.file_list.addItems(files)
            self.load_columns(files[0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CSVPlotterApp()
    ex.show()
    sys.exit(app.exec_())