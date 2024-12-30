import os
import sys
import json
import logging
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsScene,
    QGraphicsView,
    QComboBox,
    QWidget,
    QGraphicsRectItem,
    QSlider,
    QStatusBar,
    QGridLayout,
    QMessageBox,
    QInputDialog
)
from PyQt5.QtGui import QPixmap, QImage, QColor, QPen
from PyQt5.QtCore import Qt

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')


class Label(QGraphicsRectItem):
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height)
        self.setPen(QPen(QColor(color), 2))
        self.setBrush(QColor(color).lighter(160))
        self.setOpacity(0.5)


def load_annotations(filepath):
    """
    Loads existing annotations from a JSON file.
    Returns a list of annotations or an empty list if the file does not exist or is empty.
    """
    if os.path.exists(filepath):
        if os.path.getsize(filepath) > 0:
            with open(filepath, 'r') as f:
                return json.load(f)
    return []


def save_annotations(filepath, annotations_data):
    """
    Saves annotations to a JSON file with an indent of 4 spaces.
    """
    with open(filepath, 'w') as f:
        json.dump(annotations_data, f, indent=4)


class ImageAnnotationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Annotation Application")
        self.setGeometry(100, 100, 800, 600)

        try:
            self.image_folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
            if not self.image_folder:
                raise FileNotFoundError("No image folder selected.")
        except FileNotFoundError as e:
            QMessageBox.warning(self, "Error", str(e))
            sys.exit(1)

        self.image_list = [
            f for f in os.listdir(self.image_folder)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ]

        if not self.image_list:
            QMessageBox.warning(self, "Error", "Folder does not contain PNG/JPG/JPEG files.")
            sys.exit(1)

        self.num_images = len(self.image_list)
        self.current_image_index = 0
        self.labels = []

        self.annotation_file = os.path.join(os.getcwd(), "annotations.json")
        self.object_classes = ['car', 'none']

        self.colors = ['#00FF99', '#FF6600', '#3366FF', '#FF0066', '#33FFCC', '#9900FF', '#CCCC00', '#FFCCFF']
        self.current_color_index = 0

        self.existing_data = load_annotations(self.annotation_file)

        self.init_UI()

    def init_UI(self):
        main_layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        top_background = QWidget(self)
        top_background.setStyleSheet("background-color: #2C3E50; padding: 10px;")
        top_background.setLayout(top_layout)

        header = QLabel("Options Menu", self)
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #ECF0F1; margin-right: 10px;")
        top_layout.addWidget(header)

        self.class_selection = QComboBox(self)
        self.class_selection.addItems(self.object_classes)
        self.class_selection.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                background-color: #34495E;
                color: #ECF0F1;
            }
            QComboBox::drop-down {
                border: 0px;
            }
        """)
        top_layout.addWidget(self.class_selection)

        self.add_class_button = QPushButton("Add Class", self)
        self.add_class_button.setStyleSheet("""
            QPushButton {
                background-color: #1ABC9C;
                color: #FFFFFF;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #16A085;
            }
        """)
        self.add_class_button.clicked.connect(self.add_class)
        top_layout.addWidget(self.add_class_button)

        self.remove_class_button = QPushButton("Remove Class", self)
        self.remove_class_button.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: #FFFFFF;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        self.remove_class_button.clicked.connect(self.remove_class)
        top_layout.addWidget(self.remove_class_button)

        self.add_label_button = QPushButton("Add Label", self)
        self.add_label_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: #FFFFFF;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        self.add_label_button.clicked.connect(self.add_label)
        top_layout.addWidget(self.add_label_button)

        self.reset_button = QPushButton("Reset", self)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: #FFFFFF;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        self.reset_button.clicked.connect(self.reset_labels)
        top_layout.addWidget(self.reset_button)

        self.save_button = QPushButton("Save", self)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: #FFFFFF;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        self.save_button.clicked.connect(self.save_annotations)
        top_layout.addWidget(self.save_button)

        self.finish_button = QPushButton("Finish", self)
        self.finish_button.setStyleSheet("""
            QPushButton {
                background-color: #9B59B6;
                color: #FFFFFF;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #8E44AD;
            }
        """)
        self.finish_button.clicked.connect(self.close)
        top_layout.addWidget(self.finish_button)

        main_layout.addWidget(top_background)

        self.image_counter_label = QLabel(
            f"Image: {self.current_image_index + 1} / {self.num_images}",
            self
        )
        self.image_counter_label.setStyleSheet("margin-top: 5px; color: #34495E; font-weight: bold;")
        main_layout.addWidget(self.image_counter_label)

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setAlignment(Qt.AlignCenter)

        self.current_scale = 1.0
        self.min_scale = 0.5
        self.max_scale = 2.0

        zoom_layout = QHBoxLayout()
        self.zoom_in_btn = QPushButton("Zoom In")
        self.zoom_in_btn.setStyleSheet("background-color: #27AE60; color: #FFFFFF; padding: 5px; border-radius: 5px;")
        self.zoom_in_btn.clicked.connect(self.zoom_in)

        self.zoom_out_btn = QPushButton("Zoom Out")
        self.zoom_out_btn.setStyleSheet("background-color: #F39C12; color: #FFFFFF; padding: 5px; border-radius: 5px;")
        self.zoom_out_btn.clicked.connect(self.zoom_out)

        zoom_layout.addWidget(self.zoom_in_btn)
        zoom_layout.addWidget(self.zoom_out_btn)
        main_layout.addLayout(zoom_layout)

        self.slider_y1 = QSlider(Qt.Vertical)
        self.slider_y1.setMinimum(0)
        self.slider_y1.setMaximum(1000)
        self.slider_y1.setInvertedAppearance(True)
        self.slider_y1.setTickInterval(1)
        self.slider_y1.setSingleStep(1)
        self.slider_y1.setStyleSheet("""
            QSlider::handle:vertical {
                background-color: #3498DB;
                border: 1px solid #2980B9;
                height: 10px;
                margin: 0 -2px;
            }
        """)
        self.slider_y1.valueChanged.connect(self.update_rectangle)

        self.slider_y2 = QSlider(Qt.Vertical)
        self.slider_y2.setMinimum(0)
        self.slider_y2.setMaximum(1000)
        self.slider_y2.setInvertedAppearance(True)
        self.slider_y2.setTickInterval(1)
        self.slider_y2.setSingleStep(1)
        self.slider_y2.setStyleSheet(self.slider_y1.styleSheet())
        self.slider_y2.valueChanged.connect(self.update_rectangle)

        self.slider_x1 = QSlider(Qt.Horizontal)
        self.slider_x1.setMinimum(0)
        self.slider_x1.setMaximum(1000)
        self.slider_x1.setTickInterval(1)
        self.slider_x1.setSingleStep(1)
        self.slider_x1.setStyleSheet("""
            QSlider::handle:horizontal {
                background-color: #1ABC9C;
                border: 1px solid #16A085;
                width: 10px;
                margin: -2px 0;
            }
        """)
        self.slider_x1.valueChanged.connect(self.update_rectangle)

        self.slider_x2 = QSlider(Qt.Horizontal)
        self.slider_x2.setMinimum(0)
        self.slider_x2.setMaximum(1000)
        self.slider_x2.setTickInterval(1)
        self.slider_x2.setSingleStep(1)
        self.slider_x2.setStyleSheet(self.slider_x1.styleSheet())
        self.slider_x2.valueChanged.connect(self.update_rectangle)

        slider_layout = QGridLayout()
        slider_layout.addWidget(self.view, 0, 0, 3, 3)
        slider_layout.addWidget(self.slider_y1, 0, 3, 1, 1)
        slider_layout.addWidget(self.slider_y2, 1, 3, 1, 1)
        slider_layout.addWidget(self.slider_x1, 3, 0, 1, 3)
        slider_layout.addWidget(self.slider_x2, 4, 0, 1, 3)

        main_layout.addLayout(slider_layout)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.setStatusBar(QStatusBar(self))

        self.load_image()

    def zoom_in(self):
        """Zoom in the view, but only to the maximum limit."""
        if self.current_scale < self.max_scale:
            self.view.scale(1.2, 1.2)
            self.current_scale *= 1.2
            if self.current_scale > self.max_scale:
                self.current_scale = self.max_scale

    def zoom_out(self):
        """Zoom out the view, but only to the minimum limit."""
        if self.current_scale > self.min_scale:
            self.view.scale(0.8, 0.8)
            self.current_scale *= 0.8
            if self.current_scale < self.min_scale:
                self.current_scale = self.min_scale

    def load_image(self):
        """Load the next image and update the scene."""
        if self.current_image_index < len(self.image_list):
            image_path = os.path.join(self.image_folder, self.image_list[self.current_image_index])
            logging.debug(f"Loading image: {image_path}")

            self.image = QImage(image_path)
            if self.image.isNull():
                QMessageBox.warning(self, "Error", f"Cannot load image: {image_path}")
                self.current_image_index += 1
                self.load_image()
                return

            pixmap = QPixmap.fromImage(self.image)
            width = pixmap.width()
            height = pixmap.height()

            self.scene.clear()
            self.scene.setSceneRect(0, 0, width, height)
            self.scene.addPixmap(pixmap)

            self.slider_x1.setMaximum(width)
            self.slider_x2.setMaximum(width)
            self.slider_y1.setMaximum(height)
            self.slider_y2.setMaximum(height)

            self.view.setScene(self.scene)
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

            self.update_image_counter()
        else:
            QMessageBox.information(self, "End", "All images have been processed.")
            self.close()

    def update_image_counter(self):
        """Update the image counter label."""
        self.image_counter_label.setText(
            f"Image: {self.current_image_index + 1} / {self.num_images}"
        )

    def update_rectangle(self):
        """
        Update the display of the rectangle on the image
        based on the current slider values.
        """
        if self.slider_y1.value() > self.slider_y2.value():
            self.slider_y2.setValue(self.slider_y1.value())
        if self.slider_x1.value() > self.slider_x2.value():
            self.slider_x2.setValue(self.slider_x1.value())

        x1 = self.slider_x1.value()
        x2 = self.slider_x2.value()
        y1 = self.slider_y1.value()
        y2 = self.slider_y2.value()

        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1

        width = x2 - x1
        height = y2 - y1

        self.scene.clear()
        self.scene.addPixmap(QPixmap.fromImage(self.image))

        if width > 0 and height > 0:
            label = Label(x1, y1, width, height, self.colors[self.current_color_index])
            self.scene.addItem(label)

    def add_label(self):
        """Add a label (save coordinates and class)."""
        klass = self.class_selection.currentText()
        x1 = self.slider_x1.value()
        x2 = self.slider_x2.value()
        y1 = self.slider_y1.value()
        y2 = self.slider_y2.value()

        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1

        width = x2 - x1
        height = y2 - y1

        if width <= 0 or height <= 0:
            QMessageBox.warning(self, "Warning", "Cannot add a label with zero dimensions.")
            return

        label = Label(x1, y1, width, height, self.colors[self.current_color_index])
        self.scene.addItem(label)

        self.labels.append({
            'class': klass,
            'rectangle': [x1, y1, width, height]
        })
        self.current_color_index = (self.current_color_index + 1) % len(self.colors)

        self.slider_x1.setValue(0)
        self.slider_x2.setValue(0)
        self.slider_y1.setValue(0)
        self.slider_y2.setValue(0)

    def reset_labels(self):
        """Clear the list of labels and refresh the image."""
        self.labels.clear()
        self.scene.clear()
        self.load_image()

    def save_annotations(self):
        """
        Save the current labels to a JSON file and load the next image.
        """
        self.add_label()

        annotations = []
        for label in self.labels:
            klass = label['class']
            x_min, y_min, width, height = label['rectangle']
            annotations.append({
                'class': klass,
                'bbox': [x_min, y_min, width, height]
            })

        image_data = {
            'image': self.image_list[self.current_image_index],
            'annotations': annotations,
        }

        self.existing_data.append(image_data)

        save_annotations(self.annotation_file, self.existing_data)

        self.current_image_index += 1
        self.labels.clear()
        self.load_image()

    def add_class(self):
        """Add a new object class."""
        new_class, ok = QInputDialog.getText(self, "Add Class", "Enter new class name:")
        if ok and new_class:
            self.object_classes.append(new_class)
            self.class_selection.addItem(new_class)

    def remove_class(self):
        """Remove the selected object class."""
        class_to_remove = self.class_selection.currentText()
        if class_to_remove in self.object_classes:
            self.object_classes.remove(class_to_remove)
            self.class_selection.removeItem(self.class_selection.currentIndex())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageAnnotationApp()
    ex.show()
    sys.exit(app.exec_())
