from __future__ import annotations

from app.ml.brain_mri.predictor import BrainMRIPredictor
from app.ml.histopath.predictor import HistopathPredictor
from app.ml.wrist_xray.predictor import WristXrayPredictor


class PredictionService:
    _brain_mri = BrainMRIPredictor()
    _histopath = HistopathPredictor()
    _wrist_xray = WristXrayPredictor()

    @classmethod
    def predict(cls, module_type: str, file_path: str, confidence_threshold: float = 0.5) -> dict:
        if module_type == "brain_mri":
            return cls._brain_mri.predict(file_path, confidence_threshold)
        if module_type == "histopath":
            return cls._histopath.predict(file_path, confidence_threshold)
        if module_type == "wrist_xray":
            return cls._wrist_xray.predict(file_path, confidence_threshold)
        raise ValueError(f"Mô-đun không hợp lệ: {module_type}")
