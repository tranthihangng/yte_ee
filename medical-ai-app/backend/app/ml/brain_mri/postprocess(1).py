from app.utils.overlay_utils import make_brain_overlay


def postprocess(image):
    return make_brain_overlay(image)
