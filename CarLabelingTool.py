from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, \
    QGraphicsScene, QGraphicsView, QComboBox, QWidget, QGraphicsRectItem, QGraphicsItem
from PyQt5.QtGui import QPixmap, QImage, QColor, QPen, QTransform
from PyQt5.QtCore import Qt, QRectF
import sys
import os
import json


class ResizableRectItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height, color, parent=None):
        super().__init__(x, y, width, height, parent)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setPen(QPen(QColor(color), 2))
        self.setAcceptHoverEvents(True)
        self.resizing = False
        self.resize_direction = None

    def hoverMoveEvent(self, event):
        """Change cursor depending on the position (corner/edge)"""
        super().hoverMoveEvent(event)

        rect = self.rect()
        if abs(event.pos().x() - rect.left()) < 5 and abs(event.pos().y() - rect.top()) < 5:
            self.setCursor(Qt.SizeFDiagCursor)  # top left corner
            self.resize_direction = 'top_left'
        elif abs(event.pos().x() - rect.right()) < 5 and abs(event.pos().y() - rect.top()) < 5:
            self.setCursor(Qt.SizeBDiagCursor)  # top right corner
            self.resize_direction = 'top_right'
        elif abs(event.pos().x() - rect.left()) < 5 and abs(event.pos().y() - rect.bottom()) < 5:
            self.setCursor(Qt.SizeBDiagCursor)  # bottom left corner
            self.resize_direction = 'bottom_left'
        elif abs(event.pos().x() - rect.right()) < 5 and abs(event.pos().y() - rect.bottom()) < 5:
            self.setCursor(Qt.SizeFDiagCursor)  # bottom right corner
            self.resize_direction = 'bottom_right'
        elif abs(event.pos().x() - rect.left()) < 5:
            self.setCursor(Qt.SizeHorCursor)  # left edge
            self.resize_direction = 'left'
        elif abs(event.pos().x() - rect.right()) < 5:
            self.setCursor(Qt.SizeHorCursor)  # right edge
            self.resize_direction = 'right'
        elif abs(event.pos().y() - rect.top()) < 5:
            self.setCursor(Qt.SizeVerCursor)  # top edge
            self.resize_direction = 'top'
        elif abs(event.pos().y() - rect.bottom()) < 5:
            self.setCursor(Qt.SizeVerCursor)  # bottom edge
            self.resize_direction = 'bottom'
        else:
            self.setCursor(Qt.OpenHandCursor)  # default cursor
            self.resize_direction = None

    def mousePressEvent(self, event):
        """Start resizing if the user clicks in the appropriate place"""
        if event.button() == Qt.LeftButton and self.resize_direction:
            self.resizing = True
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse movement during resizing or moving"""
        if self.resizing:
            rect = self.rect()
            if self.resize_direction == 'top_left':
                new_rect = QRectF(event.pos().x(), event.pos().y(), rect.right() - event.pos().x(),
                                  rect.bottom() - event.pos().y())
            elif self.resize_direction == 'top_right':
                new_rect = QRectF(rect.left(), event.pos().y(), event.pos().x() - rect.left(),
                                  rect.bottom() - event.pos().y())
            elif self.resize_direction == 'bottom_left':
                new_rect = QRectF(event.pos().x(), rect.top(), rect.right() - event.pos().x(),
                                  event.pos().y() - rect.top())
            elif self.resize_direction == 'bottom_right':
                new_rect = QRectF(rect.left(), rect.top(), event.pos().x() - rect.left(), event.pos().y() - rect.top())
            elif self.resize_direction == 'left':
                new_rect = QRectF(event.pos().x(), rect.top(), rect.right() - event.pos().x(), rect.height())
            elif self.resize_direction == 'right':
                new_rect = QRectF(rect.left(), rect.top(), event.pos().x() - rect.left(), rect.height())
            elif self.resize_direction == 'top':
                new_rect = QRectF(rect.left(), event.pos().y(), rect.width(), rect.bottom() - event.pos().y())
            elif self.resize_direction == 'bottom':
                new_rect = QRectF(rect.left(), rect.top(), rect.width(), event.pos().y() - rect.top())
            self.setRect(new_rect)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """End resizing after releasing the mouse button"""
        self.resizing = False
        super().mouseReleaseEvent(event)
        if self.scene() and hasattr(self.scene(), 'update_bbox'):
            self.scene().update_bbox(self)


class ImageLabelingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Labeling Application")
        self.setGeometry(100, 100, 1200, 800)

        # Select folder with images
        self.image_folder = QFileDialog.getExistingDirectory(self, "Select folder with images")
        if not self.image_folder:
            sys.exit("No folder selected")

        # List of image files
        self.image_list = [f for f in os.listdir(self.image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        self.total_images = len(self.image_list)
        self.current_image_index = 0
        self.bboxes = []

        self.annotation_file = os.path.join(os.getcwd(), "annotations.json")
        self.vehicle_classes = ['passenger', 'SUV/off-road', 'delivery', 'special', 'truck']
        self.colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#000000', '#FFFFFF']
        self.current_color_index = 0
        self.zoom_factor = 1.0
        self.min_zoom = 0.2
        self.max_zoom = 2.0

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Header and buttons in a horizontal layout
        top_layout = QHBoxLayout()
        header = QLabel("Options Menu", self)
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(header)

        self.class_selector = QComboBox(self)
        self.class_selector.addItems(self.vehicle_classes)
        self.class_selector.setStyleSheet("padding: 5px;")
        top_layout.addWidget(self.class_selector)

        self.add_bbox_button = QPushButton("Add Bounding Box", self)
        self.add_bbox_button.setStyleSheet("background-color: #2c3e50; color: white; padding: 10px;")
        self.add_bbox_button.clicked.connect(self.add_bbox)
        top_layout.addWidget(self.add_bbox_button)

        self.reset_button = QPushButton("Reset All Bounding Boxes", self)
        self.reset_button.setStyleSheet("background-color: #7C2A3E; color: white; padding: 10px;")
        self.reset_button.clicked.connect(self.reset_bboxes)
        top_layout.addWidget(self.reset_button)

        self.save_button = QPushButton("Save and Next", self)
        self.save_button.setStyleSheet("background-color: #5A6B7C ; color: white; padding: 10px;")
        self.save_button.clicked.connect(self.save_annotations)
        top_layout.addWidget(self.save_button)

        main_layout.addLayout(top_layout)

        # Image counter
        self.image_counter_label = QLabel(f"Image: {self.current_image_index + 1} / {self.total_images}", self)
        main_layout.addWidget(self.image_counter_label)

        # Main scene and image view
        self.image_label = QLabel(self)
        self.scene = QGraphicsScene(self)
        self.scene.update_bbox = self.update_bbox
        self.view = QGraphicsView(self.scene)
        self.view.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.view)

        # Quit button at the bottom
        self.quit_button = QPushButton("Quit", self)
        self.quit_button.setStyleSheet("background-color: #4B3F72 ; color: white; padding: 10px;")
        self.quit_button.clicked.connect(self.close)
        main_layout.addWidget(self.quit_button)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.load_image()

    def load_image(self):
        if self.current_image_index < len(self.image_list):
            image_path = os.path.join(self.image_folder, self.image_list[self.current_image_index])
            image = QImage(image_path)
            pixmap = QPixmap.fromImage(image)

            # Automatically scale the image to the view
            scaled_pixmap = pixmap.scaled(self.view.width(), self.view.height(), Qt.KeepAspectRatio)

            # Clear the previous scene and add the new image
            self.scene.clear()
            self.scene.addPixmap(scaled_pixmap)
            self.view.setScene(self.scene)

            # Center the image after loading
            self.center_image(scaled_pixmap)

            # Update the image counter
            self.update_image_counter()
        else:
            print("All images have been processed.")
            self.close()

    def center_image(self, pixmap):
        """ Automatically center the image in the view """
        scene_rect = self.view.sceneRect()
        image_width, image_height = pixmap.width(), pixmap.height()

        # Calculate horizontal and vertical offset
        x_offset = (scene_rect.width() - image_width) / 2
        y_offset = (scene_rect.height() - image_height) / 2

        # Move the image to the calculated offset
        self.view.setSceneRect(x_offset, y_offset, image_width, image_height)

    def update_image_counter(self):
        """ Update the image counter """
        self.image_counter_label.setText(f"Image: {self.current_image_index + 1} / {self.total_images}")

    def add_bbox(self):
        rect_item = ResizableRectItem(50, 50, 100, 100, self.colors[self.current_color_index])
        self.scene.addItem(rect_item)
        self.bboxes.append({
            'class': self.class_selector.currentText(),
            'item': rect_item
        })
        self.current_color_index = (self.current_color_index + 1) % len(self.colors)

    def reset_bboxes(self):
        self.bboxes.clear()
        self.scene.clear()
        self.load_image()

    def update_bbox(self, item):
        for bbox in self.bboxes:
            if bbox['item'] == item:
                bbox['bbox'] = item.rect().getRect()

    def save_annotations(self):
        if not self.bboxes:
            # If there are no bounding boxes, display a message
            error_message = QLabel("Please add at least one bounding box!", self)
            error_message.setStyleSheet("color: red; font-size: 16px; font-weight: bold;")
            self.statusBar().clearMessage()  # Clear any old messages
            self.statusBar().showMessage("Please add at least one bounding box!", 3000)  # Show message for 3 seconds
            return  # Do not save if there are no bounding boxes

        # Continue saving if there are bounding boxes
        annotations = []
        for bbox in self.bboxes:
            rect = bbox['item'].rect()
            annotations.append({
                'class': bbox['class'],
                'bbox': [rect.x(), rect.y(), rect.width(), rect.height()]
            })
        image_data = {
            'image': self.image_list[self.current_image_index],
            'annotations': annotations
        }
        if os.path.exists(self.annotation_file):
            with open(self.annotation_file, 'r') as f:
                existing_data = json.load(f)
        else:
            existing_data = []
        existing_data.append(image_data)

        with open(self.annotation_file, 'w') as f:
            json.dump(existing_data, f, indent=4)

        self.current_image_index += 1
        self.bboxes.clear()
        self.load_image()

    def wheelEvent(self, event):
        """ Zoom using the mouse scroll """
        delta = event.angleDelta().y()
        if delta > 0:  # Scroll up - zoom in
            if self.zoom_factor < self.max_zoom:
                self.zoom_factor += 0.1
        elif delta < 0:  # Scroll down - zoom out
            if self.zoom_factor > self.min_zoom:
                self.zoom_factor -= 0.1

        # Apply zoom
        self.view.setTransform(QTransform().scale(self.zoom_factor, self.zoom_factor))
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageLabelingApp()
    ex.show()
    sys.exit(app.exec_())