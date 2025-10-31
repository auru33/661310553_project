try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets
    from shiboken2 import wrapInstance

import importlib
from . import batchMaterialToolUtil
importlib.reload(batchMaterialToolUtil)


import random
import maya.OpenMayaUI as omui
import maya.cmds as cmds


class BatchMaterialTool(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Batch Material Tool")
        self.resize(400, 500)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.setStyleSheet("QDialog { background-color: #072B59; color: white; }")

        self.formLayout = QtWidgets.QFormLayout()
        self.prefixLine = QtWidgets.QLineEdit()
        self.suffixLine = QtWidgets.QLineEdit()
        self.startSpin = QtWidgets.QSpinBox()
        self.startSpin.setMinimum(1)
        self.startSpin.setMaximum(20)
        self.startSpin.setValue(1)
        usLocale = QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates)
        self.startSpin.setLocale(usLocale)
        self.formLayout.addRow("Prefix :", self.prefixLine)
        self.formLayout.addRow("Suffix :", self.suffixLine)
        self.formLayout.addRow("Start :", self.startSpin)
        self.mainLayout.addLayout(self.formLayout)

        self.typeLayout = QtWidgets.QHBoxLayout()
        self.typeCombo = QtWidgets.QComboBox()
        self.typeCombo.addItems(["Lambert", "Blinn", "Standard Surface"])
        self.typeCombo.setStyleSheet("QComboBox { background-color: #2E5B99; }")
        self.colorButton = QtWidgets.QPushButton("Choose Color")
        self.colorButton.clicked.connect(self.choose_color)
        self.randomColorCheckbox = QtWidgets.QCheckBox("Random Color")
        self.typeLayout.addWidget(QtWidgets.QLabel("Material Type:"))
        self.typeLayout.addWidget(self.typeCombo)
        self.typeLayout.addWidget(self.colorButton)
        self.typeLayout.addWidget(self.randomColorCheckbox)
        self.mainLayout.addLayout(self.typeLayout)

        self.uniqueCheckbox = QtWidgets.QCheckBox("Unique per object")
        self.assign_if_noneCheckbox = QtWidgets.QCheckBox("Assign to objects without material")
        self.mainLayout.addWidget(self.uniqueCheckbox)
        self.mainLayout.addWidget(self.assign_if_noneCheckbox)

        self.mainLayout.addWidget(QtWidgets.QLabel("Current Materials:"))
        self.materialList = QtWidgets.QListWidget()
        self.mainLayout.addWidget(self.materialList)


        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.previewButton = QtWidgets.QPushButton("Preview Materials")
        self.renameButton = QtWidgets.QPushButton("Rename & Assign")
        self.resetButton = QtWidgets.QPushButton("Reset")
        self.buttonLayout.addWidget(self.previewButton)
        self.buttonLayout.addWidget(self.renameButton)
        self.buttonLayout.addWidget(self.resetButton)
        self.mainLayout.addLayout(self.buttonLayout)


        self.renameButton.clicked.connect(self.rename_and_assign)
        self.resetButton.clicked.connect(self.reset_ui)
        self.previewButton.clicked.connect(self.preview_materials)
        self.colorButton.setStyleSheet("QPushButton { background-color: #4283DD; color: white; }")

        buttonDown_style = """
        QPushButton {background-color: #2E5B99; border-radius: 20px; font-size: 22px; padding: 12px;}
        QPushButton:hover {background-color: #4587E6; color: white;}
        QPushButton:pressed {background-color: #193255;}
        """

        self.renameButton.setStyleSheet(buttonDown_style)
        self.previewButton.setStyleSheet(buttonDown_style)
        self.resetButton.setStyleSheet(buttonDown_style)

        self.chosenColor = QtGui.QColor(255, 255, 255)


    def choose_color(self):
        colorDialog = QtWidgets.QColorDialog(self)
        colorDialog.setOption(QtWidgets.QColorDialog.DontUseNativeDialog, True)
        usLocale = QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates)
        colorDialog.setLocale(usLocale)
        colorDialog.setWindowTitle("Choose Material Color")
        colorDialog.setCurrentColor(self.chosenColor)

        for child in colorDialog.findChildren(QtWidgets.QDialogButtonBox):
            for button in child.buttons():
                if button.text() == "OK":
                    button.setStyleSheet("""
                        QPushButton {background-color: #25A259; color: white; border-radius: 6px; padding: 12px; width: 150px;}
                        QPushButton:hover {background-color: #2ECC71;}""")
                elif button.text() == "Cancel":
                    button.setStyleSheet("""
                        QPushButton {background-color: #BE3F31; color: white; border-radius: 6px; padding: 12px; width: 150px;} 
                        QPushButton:hover {background-color: #E74C3C;}""")
             


            if colorDialog.exec() == QtWidgets.QDialog.Accepted:
                color = colorDialog.currentColor()
                self.chosenColor = color
                self.colorButton.setStyleSheet(
                    f"QPushButton {{ background-color: {color.name()}; color: white; padding: 6px; }}"
                    )

    def reset_ui(self):
        self.prefixLine.clear()
        self.suffixLine.clear()
        self.startSpin.setValue(1)
        self.materialList.clear()

    def rename_and_assign(self):

        prefix = self.prefixLine.text()
        suffix = self.suffixLine.text()
        start = self.startSpin.value()
        mat_type = self.typeCombo.currentText()
        color = [self.chosenColor.redF(), self.chosenColor.greenF(), self.chosenColor.blueF()]

        selected_objs = cmds.ls(selection=True, long=True)
        if not selected_objs:
            cmds.warning("Please select at least one object.")
            return

        renamed_info = []
        for i, obj in enumerate(selected_objs):
            results = batchMaterialToolUtil.process_materials(
                obj=obj,
                mat_type=mat_type,
                color=color,
                prefix=prefix,
                suffix=suffix,
                start=start + i,
                unique=self.uniqueCheckbox.isChecked(),
                assign_if_none=self.assign_if_noneCheckbox.isChecked()
            )
            renamed_info.extend(results)

        if hasattr(self, "randomColorCheckbox") and self.randomColorCheckbox.isChecked():
            for old_name, new_name in renamed_info:
                if cmds.objExists(new_name + ".color"):
                    r = random.uniform(0.0, 1.0)
                    g = random.uniform(0.0, 1.0)
                    b = random.uniform(0.0, 1.0)
                    cmds.setAttr(f"{new_name}.color", r, g, b, type="double3")

            cmds.inViewMessage(amg='<hl>Random colors applied!</hl>', pos='midCenter', fade=True)

        self.materialList.clear()
        for old, new in renamed_info:
            self.materialList.addItem(f"{old} → {new}")

    def preview_materials(self):
        
        self.materialList.clear()

        selected_objs = cmds.ls(selection=True, long=True)
        materials = []

        if selected_objs:
            for obj in selected_objs:
                shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or [obj]
                for s in shapes:
                    shadingGroups = cmds.listConnections(s, type='shadingEngine') or []
                    for sg in shadingGroups:
                        mats = cmds.ls(cmds.listConnections(sg + ".surfaceShader"), materials=True) or []
                        materials.extend(mats)
        else:
            materials = cmds.ls(materials=True)
        materials = list(set(materials))

        if not materials:
            self.materialList.addItem("No materials found.")
            return

        for mat in materials:
            if cmds.attributeQuery("color", node=mat, exists=True):
                color = cmds.getAttr(f"{mat}.color")[0]
                r, g, b = [int(c * 255) for c in color]
                item = QtWidgets.QListWidgetItem(f"{mat}  |  RGB: ({r}, {g}, {b})")
                item.setBackground(QtGui.QColor(r, g, b))
                item.setForeground(QtGui.QColor(255 - r, 255 - g, 255 - b))
                self.materialList.addItem(item)
            else:
                self.materialList.addItem(f"{mat} (no color attribute)")





def run():
    global ui
    try:
        ui.close()
        ui.deleteLater()
    except Exception:
        pass

    ptr = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
    ui = BatchMaterialTool(parent=ptr)
    ui.show()
