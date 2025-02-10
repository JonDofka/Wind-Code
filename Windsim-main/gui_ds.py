import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QListWidget, QWidget, QLabel, QComboBox
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

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # File selection dropdown
        self.label = QLabel("Select File Type to Load:", self)
        self.layout.addWidget(self.label)

        self.file_type_dropdown = QComboBox(self)
        self.file_type_dropdown.addItems(["All FRT Files","FRT 1P Files", "FRT 2P Files", "FRT 2P-EARTH Files", "FRT 3P Files", "All Logger Files", "1P Files", "2P Files", "2P-EARTH Files", "3P Files",])
        self.file_type_dropdown.currentIndexChanged.connect(self.on_file_type_selected)
        self.layout.addWidget(self.file_type_dropdown)

        self.loaded_files_label = QLabel("Loaded Files: None", self)
        self.layout.addWidget(self.loaded_files_label)

        # **Auto-load "All FRT Files" on startup**
        self.file_type_dropdown.setCurrentText("All FRT Files")  
        self.on_file_type_selected()

    def on_file_type_selected(self):
        file_type_mapping = {
            "All FRT Files": "frt",
            "FRT 1P Files": "1PFRT",
            "FRT 2P Files": "2PFRT",
            "FRT 2P-EARTH Files": "2P-EARTHFRT",
            "FRT 3P Files": "3PFRT",
            "All Logger Files": "logger",
            "1P Files": "1P",
            "2P Files": "2P",
            "2P-EARTH Files": "2P-EARTH",
            "3P Files": "3P"
        }
        selected_file_type = self.file_type_dropdown.currentText()
        self.load_files(file_type_mapping[selected_file_type])

    def load_files(self, file_type, folder_path="Wind_Faults"):
        # Clear previous widgets (except the dropdown and label)
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget not in [self.label, self.file_type_dropdown, self.loaded_files_label]:
                widget.setParent(None)

        self.loaded_files_label.setText(f"Loaded Files: {file_type}")

        # Add file list widget
        self.file_list = QListWidget(self)
        self.file_list.setFixedHeight(100)
        self.layout.addWidget(self.file_list)

        # Add column selection label and list
        self.column_label = QLabel('Select Columns to Plot:', self)
        self.layout.addWidget(self.column_label)

        self.column_list = QListWidget(self)
        self.column_list.setSelectionMode(QListWidget.MultiSelection)
        self.layout.addWidget(self.column_list)

        # Add plot button
        self.plot_button = QPushButton('Plot', self)
        self.plot_button.clicked.connect(self.plot_data)
        self.layout.addWidget(self.plot_button)

        # Check if the folder exists
        if not os.path.exists(folder_path):
            print(f"Folder '{folder_path}' not found!")
            return

        # Filter files based on the selected file type
        if file_type == "frt":
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if "_frt" in f and f.endswith(".csv")]
        elif file_type == "logger":
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if "_frt" not in f and f.endswith(".csv")]
        elif file_type == "1P":
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if "1P" in f and "_frt" not in f and f.endswith(".csv")]
        elif file_type == "2P":
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if "2P" in f and "EARTH" not in f and "_frt" not in f and f.endswith(".csv")]
        elif file_type == "2P-EARTH":
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if "2P.EARTH" in f and "_frt" not in f and f.endswith(".csv")]
        elif file_type == "3P":
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if "3P" in f and "_frt" not in f and f.endswith(".csv")]
        elif file_type == "1PFRT":
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if "1P" in f and "_frt" in f and f.endswith(".csv")]
        elif file_type == "2PFRT":
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if "2P" in f and "EARTH" in f and "_frt" not in f and f.endswith(".csv")]
        elif file_type == "2P-EARTHFRT":
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if "2P.EARTH" in f and "_frt" in f and f.endswith(".csv")]
        elif file_type == "3PFRT":
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if "3P" in f and "_frt" in f and f.endswith(".csv")]
        else:
            files = []

        # Add filtered files to the file list
        if files:
            self.file_list.addItems(files)
            self.load_columns(files[0])  # Load columns from the first file

    def load_columns(self, file_path):
        self.column_list.clear()
        df = pd.read_csv(file_path)
        self.column_list.addItems(df.columns)
    
    def plot_data(self):
        selected_files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        selected_columns = [item.text() for item in self.column_list.selectedItems()]

        if not selected_files or not selected_columns:
            return

        # Create a new figure for the plot
        figure = Figure()
        ax = figure.add_subplot(111)

        # Store the lines and labels
        self.lines = []
        self.labels = []

        for file in selected_files:
            df = pd.read_csv(file)
            for column in selected_columns:
                if column in df.columns:
                    line, = ax.plot(df[column], linewidth=2, alpha=0.7, picker=True, pickradius=5)
                    self.lines.append(line)
                    self.labels.append(f'{os.path.basename(file)} - {column}')

        ax.set_xlabel('Index')
        ax.set_ylabel('Value')
        ax.set_title(f'Plot of {", ".join(selected_columns)}')

        # Create new window for the plot
        self.plot_window = PlotWindow(figure)
        self.plot_window.show()

        # Dropdown for selecting a line to highlight
        self.line_dropdown = QComboBox(self.plot_window)
        self.line_dropdown.addItems(self.labels)
        self.line_dropdown.currentIndexChanged.connect(self.highlight_selected_line)
        self.line_dropdown.setGeometry(20, 60, 200, 30)  # Position dropdown
        self.line_dropdown.show()

        # QLabel for showing the selected line (legend popup)
        self.legend_label = QLabel(self.plot_window)
        self.legend_label.setStyleSheet("font-size: 14px; font-weight: bold; background-color: white; padding: 5px; border: 1px solid black;")
        self.legend_label.setAlignment(Qt.AlignCenter)
        self.legend_label.setVisible(False)

        # mplcursors for hover tooltips
        cursor = mplcursors.cursor(self.lines, hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(self.labels[self.lines.index(sel.artist)]))

    def highlight_selected_line(self):
        selected_index = self.line_dropdown.currentIndex()
        
        if selected_index == -1:
            return

        selected_line = self.lines[selected_index]
        selected_label = self.labels[selected_index]

        for line in self.lines:
            if line == selected_line:
                line.set_alpha(1.0)  # Highlight the selected line
                line.set_linewidth(3)
            else:
                line.set_alpha(0.1)  # Make others transparent
                line.set_linewidth(.5)

        # Show and update the legend popup
        self.legend_label.setText(selected_label)
        self.legend_label.adjustSize()
        self.legend_label.move(20, 20)
        self.legend_label.setVisible(True)

        self.plot_window.canvas.draw()  # Update the plot

    def on_line_click(self, event):
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CSVPlotterApp()
    ex.show()
    sys.exit(app.exec_())