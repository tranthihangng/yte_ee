from app.utils.overlay_utils import make_detection_view


def postprocess(image):
    return make_detection_view(image)
