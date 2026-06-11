from ultralytics import YOLO

model = YOLO(r"gd\xray\last35.pt")

for k, v in model.names.items():
    print(f"{k}: {v}")