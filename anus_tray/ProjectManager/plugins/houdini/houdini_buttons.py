import hou


# Cooking
def cook():
    return hou.qt.Icon("BUTTONS_cook")


def cook2():
    return hou.qt.Icon("BUTTONS_cook2")


# Render


def render():
    return hou.qt.Icon("BUTTONS_render")


def ogl_render():
    return hou.qt.Icon("ROP_opengl")


def mantra_render():
    return hou.qt.Icon("ROP_mantra")


def rman_render():
    return hou.qt.Icon("ROP_rman")


# TOPS


def top_gather_all():
    return hou.qt.Icon("TOP_gatherall")


def top_by_index():
    return hou.qt.Icon("TOP_gatherbyindex")


def top_pdg_cooking(numb: int):
    if numb:
        return hou.qt.Icon(f"TOP_pdg_cooking_{str(numb)}")
    else:
        return hou.qt.Icon("TOP_pdg_cooking")


def top_pdg_done():
    return hou.qt.Icon("TOP_pdg_done")


def top_pdg_error():
    return hou.qt.Icon("TOP_pdg_error")


# STATUS


def STATUS_ok():
    return hou.qt.Icon("STATUS_ok")


def STATUS_no():
    return hou.qt.Icon("STATUS_no")


def STATUS_warning():
    return hou.qt.Icon("STATUS_warning")


def STATUS_error():
    return hou.qt.Icon("STATUS_error")