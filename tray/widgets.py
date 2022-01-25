import darkdetect
import draw_items


def Switches():
    if darkdetect.isDark():
        return draw_items.on_white(),draw_items.off_white()
    else:
        return draw_items.on_dark(),draw_items.off_dark()