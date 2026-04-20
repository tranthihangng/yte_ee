from app.utils.overlay_utils import make_gradcam


def postprocess(image):
    return make_gradcam(image)
