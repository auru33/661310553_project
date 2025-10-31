import maya.cmds as cmds
import random

def process_materials(obj, mat_type, color, prefix, suffix, start, unique, assign_if_none):
    renamed_info = []
    shadingGroups = cmds.listConnections(obj, type='shadingEngine') or []
    mats = []

    is_in_initial_sg = False
    for sg in shadingGroups:
        if sg == "initialShadingGroup":
            is_in_initial_sg = True
        else:
            mats += cmds.ls(cmds.listConnections(sg + ".surfaceShader"), materials=True) or []

    existing_mats = [m for m in mats if m.startswith(prefix)]
    if unique or (assign_if_none and not existing_mats):
        mat = create_material(mat_type, prefix, suffix, start)
        assign_material(obj, mat)
        mats = [mat]
   
    for mat in mats:
        new_name = "_".join([p for p in [prefix, mat, str(start), suffix] if p])

        if cmds.objExists(new_name):
            new_name = cmds.rename(mat, new_name + "_{}".format(random.randint(100, 999)))
        else:
            new_name = cmds.rename(mat, new_name)

        if cmds.objExists(new_name + ".color"):
            cmds.setAttr(new_name + ".color", *color, type="double3")

        renamed_info.append((mat, new_name))

    return renamed_info


def create_material(mat_type, prefix, suffix, count):
    base_name = f"{prefix or ''}{mat_type}_{count}{('_' + suffix) if suffix else ''}"

    if mat_type.lower() == "lambert":
        mat = cmds.shadingNode("lambert", asShader=True, name=base_name)
    elif mat_type.lower() == "blinn":
        mat = cmds.shadingNode("blinn", asShader=True, name=base_name)
    else:
        mat = cmds.shadingNode("standardSurface", asShader=True, name=base_name)

    return mat


def assign_material(obj, mat):
    sg = mat + "SG"
    if not cmds.objExists(sg):
        sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg)
        cmds.connectAttr(mat + ".outColor", sg + ".surfaceShader", force=True)
    cmds.sets(obj, edit=True, forceElement=sg)


def generate_random_color():
    return [random.random(), random.random(), random.random()]


def apply_random_color_to_material(mat):
    if cmds.objExists(mat + ".color"):
        color = generate_random_color()
        cmds.setAttr(mat + ".color", *color, type="double3")
        return color
    return None
