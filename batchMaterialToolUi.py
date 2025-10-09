try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets
    from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui

class BatchMaterialTool(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Batch Material Tool")
        self.resize(400, 500)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        
        self.form_layout = QtWidgets.QFormLayout()
        self.prefix_line = QtWidgets.QLineEdit()
        self.suffix_line = QtWidgets.QLineEdit()
        self.start_spin = QtWidgets.QSpinBox()
        self.start_spin.setMinimum(1)
        self.start_spin.setMaximum(20)
        self.start_spin.setValue(1)
        usLocale = QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates)
        self.start_spin.setLocale(usLocale)
        self.form_layout.addRow("Prefix:", self.prefix_line)
        self.form_layout.addRow("Suffix:", self.suffix_line)
        self.form_layout.addRow("Start :", self.start_spin)
        self.main_layout.addLayout(self.form_layout)
        
        self.type_layout = QtWidgets.QHBoxLayout()
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["Lambert", "Blinn", "Standard Surface"])
        self.color_button = QtWidgets.QPushButton("Choose Color")
        self.random_color_checkbox = QtWidgets.QCheckBox("Random Color")
        self.type_layout.addWidget(QtWidgets.QLabel("Material Type:"))
        self.type_layout.addWidget(self.type_combo)
        self.type_layout.addWidget(self.color_button)
        self.type_layout.addWidget(self.random_color_checkbox)
        self.main_layout.addLayout(self.type_layout)

        self.unique_checkbox = QtWidgets.QCheckBox("Unique per object")
        self.assign_if_none_checkbox = QtWidgets.QCheckBox("Assign to objects without material")
        self.main_layout.addWidget(self.unique_checkbox)
        self.main_layout.addWidget(self.assign_if_none_checkbox)

        self.main_layout.addWidget(QtWidgets.QLabel("Current Materials:"))
        self.material_list = QtWidgets.QListWidget()
        self.main_layout.addWidget(self.material_list)

        self.material_list.addItem("pCube1 -> lambert1")
        self.material_list.addItem("pSphere1 -> blinn1")
        self.material_list.addItem("pCone1 -> lambert2")

        self.button_layout = QtWidgets.QHBoxLayout()
        self.preview_button = QtWidgets.QPushButton("Preview Materials")
        self.rename_button = QtWidgets.QPushButton("Rename & Assign")
        self.reset_button = QtWidgets.QPushButton("Reset")
        self.button_layout.addWidget(self.preview_button)
        self.button_layout.addWidget(self.rename_button)
        self.button_layout.addWidget(self.reset_button)
        self.main_layout.addLayout(self.button_layout)


def run():
    global ui
    try:
        ui.close()
    except:
        pass

    ptr = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
    ui = BatchMaterialTool(parent=ptr)
    ui.show()