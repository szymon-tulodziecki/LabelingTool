# 🖼️ Image Labeling Application 🏷️

A PyQt5-based application for labeling images with bounding boxes. The application allows users to select a folder of images, draw and resize bounding boxes, and save the annotations in a JSON file. Perfect for computer vision projects and machine learning datasets! 🚀

[![GitHub Stars](https://img.shields.io/github/stars/szymon-tulodziecki/CarLabelingTool?style=social)](https://github.com/szymon-tulodziecki/CarLabelingTool)
[![GitHub Forks](https://img.shields.io/github/forks/szymon-tulodziecki/CarLabelingTool?style=social)](https://github.com/szymon-tulodziecki/CarLabelingTool)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- **Folder Selection:** Easily select a folder containing your images. 📂
- **Image Display:** View images one by one in the application. 🖼️
- **Bounding Box Creation & Resizing:** Draw and resize bounding boxes directly on the images using intuitive sliders. 🖱️
- **Annotation Saving:** Save annotations (bounding boxes and their classes) to a JSON file for easy use in your projects. 💾
- **Zoom Functionality:** Zoom in and out using the mouse scroll wheel for precise labeling. 🔍
- **Class Management:** Add or remove object classes directly from the application. ➕ ➖

## 📸 Screenshots

These screenshots showcase the application in action:

![Screenshot 1](img/img_1.png)
![Screenshot 2](img/img_2.png)

## ⬇️ Installation

Get started with the Image Labeling Application in a few simple steps:

1. **Clone the Repository:**

git clone https://github.com/szymon-tulodziecki/CarLabelingTool.git
cd CarLabelingTool


2. **Create a Virtual Environment:** (Recommended)

python3 -m venv venv
source venv/bin/activate # On Linux/macOS
venv\Scripts\activate # On Windows


3. **Install Dependencies:**

pip install -r requirements.txt


## 💻 Usage

1. **Run the Application:**

python CarLabelingTool/CarLabelingTool.py


2. **Select Folder:** Choose the folder containing the images you want to label.

3. **Start Labeling:**
 - Use the intuitive interface to add, resize, and save bounding boxes.
 - Use the sliders to precisely adjust the coordinates and size of the bounding boxes.
 - Select the class of the object from the dropdown menu.
 - Add or remove classes as needed using the "Add Class" and "Remove Class" buttons.

## 🗂️ File Structure

Understand the project's file structure:

- `CarLabelingTool/CarLabelingTool.py`: The main application code, implementing the image labeling functionality. 🐍
- `annotations.json`: The file where your annotations are stored in JSON format. 📝
- `requirements.txt`: A list of Python packages required to run the application. 📄

## ⚙️ Dependencies

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro): A comprehensive set of Python bindings for Qt v5, used for the graphical user interface.
- Python 3.6+: The programming language used to build the application.

## 🔑 License

This project is licensed under the [MIT License](LICENSE). See the `LICENSE` file for more details. Feel free to use, modify, and distribute this software!

## 🛠️ Key Code Snippets 

Here are some interesting code snippets from the `LabelingTool.py` file:

* **Loading Annotations**:
 ```
 def load_annotations(filepath):
     """Loads existing annotations from a JSON file."""
     if os.path.exists(filepath):
         with open(filepath, 'r') as f:
             return json.load(f)
     return []
 ```
 This function handles loading existing annotations from the `annotations.json` file.

* **Saving Annotations**:
 ```
 def save_annotations(filepath, annotations_data):
     """Saves annotations to a JSON file with an indent of 4 spaces."""
     with open(filepath, 'w') as f:
         json.dump(annotations_data, f, indent=4)
 ```
 This function saves the created annotations to a JSON file with proper formatting.

## Contributing 🤝

Contributions are welcome!  If you find a bug or have an idea for a new feature, please submit an issue or pull request.
