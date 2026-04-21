from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt

# Đường dẫn
model_path = r"gd\tuberculosis_counting\best.pt"
image_path = r"gd\tuberculosis_counting\tuberculosis-phone-0012_jpg.rf.842c36dd65e712a4feba50cc050b26bc.jpg"

# Load model
model = YOLO(model_path)

# Đọc ảnh gốc
img = cv2.imread(image_path)
if img is None:
    raise FileNotFoundError(f"Không đọc được ảnh: {image_path}")

img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Dự đoán
results = model.predict(source=image_path, conf=0.25, save=False)

# Lấy kết quả đầu tiên
result = results[0]

# Đếm số bounding box
num_boxes = len(result.boxes)
print("Số bounding box:", num_boxes)

# Ảnh kết quả có bbox/label
result_img = result.plot()
result_img_rgb = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)

# Hiển thị 2 ảnh cạnh nhau
plt.figure(figsize=(14, 7))

plt.subplot(1, 2, 1)
plt.imshow(img_rgb)
plt.title("Ảnh gốc")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(result_img_rgb)
plt.title(f"Ảnh kết quả - {num_boxes} bounding box")
plt.axis("off")

plt.tight_layout()
plt.show()