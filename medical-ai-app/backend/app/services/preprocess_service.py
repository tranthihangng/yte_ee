from app.ml.brain_mri.preprocess import preprocess as preprocess_brain_mri
from app.ml.histopath.preprocess import preprocess as preprocess_histopath
from app.ml.tuberculosis_counting.preprocess import preprocess as preprocess_tuberculosis
from app.ml.wrist_xray.preprocess import preprocess as preprocess_wrist_xray

_PREPROCESSORS = {
    "brain_mri": preprocess_brain_mri,
    "histopath": preprocess_histopath,
    "wrist_xray": preprocess_wrist_xray,
    "tuberculosis_counting": preprocess_tuberculosis,
}


def preprocess(file_path: str, module_type: str) -> str:
    """Gọi hàm preprocess tương ứng từng loại ảnh."""
    handler = _PREPROCESSORS.get(module_type)
    if not handler:
        return file_path
    return handler(file_path)
