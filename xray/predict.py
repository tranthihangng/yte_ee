from ultralytics import YOLO
from pathlib import Path
import matplotlib.pyplot as plt
import cv2

BASE_DIR = Path(__file__).resolve().parent

# model = YOLO(str(BASE_DIR / "gd" / "xray" / "last35.pt"))
# image_path = str(BASE_DIR / "gd" / "xray" / "0056_0422451576_03_WRI-L2_F012.png")

model = YOLO("gd/xray/last35.pt")
image_path = r"gd\xray\0055_0845337283_02_WRI-L1_F015.png"

results = model.predict(source=image_path, conf=0.25, save=False)
img = results[0].plot()  # BGR

img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

plt.figure(figsize=(10, 10))
plt.imshow(img_rgb)
plt.axis("off")
plt.title("Prediction Result")
plt.show()