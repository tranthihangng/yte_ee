import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import cv2

from tensorflow.keras.models import load_model
from tensorflow.keras.utils import load_img, img_to_array
from tensorflow.keras.applications.resnet50 import preprocess_input

# ====== Đường dẫn ======
model_path = r"gd\his\best_resnet50_lung.keras"
image_path = r"gd\his\lungaca1001.jpeg"

IMG_SIZE = (224, 224)

# Nếu train bằng flow_from_directory thì class thường sort alphabet
class_names = ["lung_aca", "lung_n", "lung_scc"]

# ====== Load model ======
model = load_model(model_path)

# ====== Tiền xử lý ảnh ======
img = load_img(image_path, target_size=IMG_SIZE)
img_array = img_to_array(img)
img_batch = np.expand_dims(img_array, axis=0)
img_batch = preprocess_input(img_batch)

# ====== Predict ======
pred = model.predict(img_batch, verbose=0)
pred_idx = np.argmax(pred[0])
pred_class = class_names[pred_idx]
pred_conf = float(pred[0][pred_idx])

print("Predicted class:", pred_class)
print("Confidence:", pred_conf)
print("Prediction vector:", pred[0])

# ====== Grad-CAM ======
def make_gradcam_heatmap(img_array, model, last_conv_layer_name="conv5_block3_out", pred_index=None):
    last_conv_layer = model.get_layer(last_conv_layer_name)

    model_output = model.output[0] if isinstance(model.output, list) else model.output

    grad_model = tf.keras.models.Model(
        inputs=model.input,
        outputs=[last_conv_layer.output, model_output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array, training=False)

        if isinstance(predictions, (list, tuple)):
            predictions = predictions[0]

        if pred_index is None:
            pred_index = tf.argmax(predictions[0])

        class_channel = predictions[:, pred_index]

    grads = tape.gradient(class_channel, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = tf.reduce_sum(conv_outputs * pooled_grads, axis=-1)

    heatmap = tf.maximum(heatmap, 0) / (tf.reduce_max(heatmap) + 1e-8)
    return heatmap.numpy()

heatmap = make_gradcam_heatmap(
    img_batch,
    model,
    last_conv_layer_name="conv5_block3_out",
    pred_index=pred_idx
)

# ====== Đọc ảnh gốc ======
orig = cv2.imread(image_path)
orig = cv2.cvtColor(orig, cv2.COLOR_BGR2RGB)

# Resize heatmap theo ảnh gốc
heatmap_uint8 = np.uint8(255 * heatmap)
heatmap_resized = cv2.resize(heatmap_uint8, (orig.shape[1], orig.shape[0]))

# Tạo ảnh overlay
heatmap_color = cv2.applyColorMap(heatmap_resized, cv2.COLORMAP_JET)
heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

alpha = 0.4
gradcam_img = cv2.addWeighted(orig, 1 - alpha, heatmap_color, alpha, 0)

# ====== Hiển thị 2 ảnh ======
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.imshow(orig)
plt.title("Original Image")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(gradcam_img)
plt.title(f"Grad-CAM\n{pred_class} ({pred_conf:.4f})")
plt.axis("off")

plt.tight_layout()
plt.show()