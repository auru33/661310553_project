try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets
    from shiboken2 import wrapInstance

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
        self.colorButton.setStyleSheet("QPushButton { background-color: #4283DD; color: white; }")

        self.chosenColor = QtGui.QColor(255, 255, 255)


    def choose_color(self):
        color = QtWidgets.QColorDialog.getColor(self.chosenColor, self, "Choose Material Color")
        if color.isValid():
            self.chosenColor = color
            self.colorButton.setStyleSheet(f"QPushButton {{ background-color: {color.name()}; color: white; }}")

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

        selected_objs = cmds.ls(selection=True, long=True)
        if not selected_objs:
            return

        count = start
        renamed_info = []

        for obj in selected_objs:
            shading_groups = cmds.listConnections(obj, type='shadingEngine') or []
            mats = []

            for sg in shading_groups:
                mats += cmds.ls(cmds.listConnections(sg + ".surfaceShader"), materials=True) or []

            if not mats and self.assign_if_noneCheckbox.isChecked():
                mat = self.create_material(mat_type)
                self.assign_material(obj, mat)
                mats = [mat]

            for mat in mats:
                new_name = "_".join([p for p in [prefix, mat, str(count), suffix] if p])
                if cmds.objExists(new_name):
                    continue

                new_mat = cmds.rename(mat, new_name)
                renamed_info.append((mat, new_mat))
                count += 1

                rgb = [self.chosenColor.redF(), self.chosenColor.greenF(), self.chosenColor.blueF()]
                if cmds.objExists(new_mat + ".color"):
                    cmds.setAttr(new_mat + ".color", *rgb, type="double3")

                self.assign_material(obj, new_mat)


        self.materialList.clear()
        for old, new in renamed_info:
            self.materialList.addItem(f"{old} → {new}")


    def create_material(self, mat_type):

        if mat_type.lower() == "lambert":
            mat = cmds.shadingNode("lambert", asShader=True)
        elif mat_type.lower() == "blinn":
            mat = cmds.shadingNode("blinn", asShader=True)
        else:
            mat = cmds.shadingNode("standardSurface", asShader=True)
        return mat

    def assign_material(self, obj, mat):
 
        sg = mat + "SG"
        if not cmds.objExists(sg):
            sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg)
            cmds.connectAttr(mat + ".outColor", sg + ".surfaceShader", force=True)
        cmds.sets(obj, edit=True, forceElement=sg)


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
