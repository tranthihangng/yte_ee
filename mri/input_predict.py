"""
Script để predict với BraTS 2D models.
Hỗ trợ visualize kết quả segmentation.

Chạy nhanh:
    python predict_brats_2d.py

Hoặc truyền tham số:
    python predict_brats_2d.py --model_path exp/brats/test/fold_0_best.pth --sample_name BraTS2021_00000_slice070
    python predict_brats_2d.py --save_plot --save_dir results/
"""

import os
import sys
import argparse
import numpy as np
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
import yaml

# =========================================================
# ĐIỀN SẴN THÔNG TIN Ở ĐÂY
# =========================================================
DEFAULT_MODEL_PATH = r'exp\brats\brats_fsfa_unet_2d\epoc47\fold_0_latest.pth'
DEFAULT_SAMPLE_NAME = 'BraTS2021_00000_slice070'
DEFAULT_DATA_ROOT = r'D:/research2025/y_te/code/CBIM-Medical-Image-Segmentation/dataset/brats2021_2d'
DEFAULT_GPU = '0'
DEFAULT_SAVE_DIR = None
DEFAULT_CONFIG_PATH = None   # None = tự dò config
DEFAULT_SAVE_PLOT = False    # True = tự lưu ảnh thay vì chỉ hiển thị
# =========================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CBIM_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', 'CBIM-Medical-Image-Segmentation'))

if CBIM_ROOT not in sys.path:
    sys.path.insert(0, CBIM_ROOT)

from model.utils import get_model


def load_model(model_path, config_path, device='cuda'):
    """Load trained model từ checkpoint."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    class Args:
        pass

    args = Args()
    for key, value in config.items():
        setattr(args, key, value)

    # Set dimension (required by get_model)
    if not hasattr(args, 'dimension'):
        args.dimension = '2d'

    # Map 'arch' to 'model' if needed
    if hasattr(args, 'arch') and not hasattr(args, 'model'):
        args.model = args.arch

    model = get_model(args)
    checkpoint = torch.load(model_path, map_location=device)

    # Try EMA first, fallback to regular model
    if 'ema_model_state_dict' in checkpoint and checkpoint['ema_model_state_dict'] is not None:
        model.load_state_dict(checkpoint['ema_model_state_dict'])
        print("Loaded EMA model")
    else:
        model.load_state_dict(checkpoint['model_state_dict'])
        print("Loaded regular model")

    model.to(device)
    model.eval()
    return model, args


def load_sample(data_root, sample_name):
    """Load một sample từ dataset."""
    # New format: .npz
    npz_path = os.path.join(data_root, f'{sample_name}.npz')
    if os.path.exists(npz_path):
        data = np.load(npz_path)
        img = data['data'].astype(np.float32)  # (4, H, W)
        seg = data.get('label', np.zeros(img.shape[1:], dtype=np.uint8))
        if seg is not None:
            seg = seg.astype(np.uint8)
        return img, seg, sample_name

    # Old format: _img.npy / _seg.npy
    img_path = os.path.join(data_root, f'{sample_name}_img.npy')
    seg_path = os.path.join(data_root, f'{sample_name}_seg.npy')

    if os.path.exists(img_path):
        img = np.load(img_path).astype(np.float32)  # (4, H, W)
        seg = np.load(seg_path).astype(np.uint8) if os.path.exists(seg_path) else np.zeros(img.shape[1:], dtype=np.uint8)
        return img, seg, sample_name

    raise FileNotFoundError(
        f"Sample not found: {sample_name}\n"
        f"Tried:\n"
        f"  {npz_path}\n"
        f"  {img_path}\n"
        f"  {seg_path}"
    )


def normalize(img):
    """Normalize từng modality."""
    for i in range(img.shape[0]):
        channel = img[i]
        if channel.max() > 0:
            p1, p99 = np.percentile(channel, [1, 99])
            channel = np.clip(channel, p1, p99)
            channel = (channel - channel.min()) / (channel.max() - channel.min() + 1e-8)
        img[i] = channel
    return img


def predict(model, img, device='cuda'):
    """Predict segmentation cho một image."""
    model.eval()

    with torch.no_grad():
        img = normalize(img.copy())

        # (4, H, W) -> (1, 4, H, W)
        tensor_img = torch.from_numpy(img).float().unsqueeze(0).to(device)

        output = model(tensor_img)

        if isinstance(output, (tuple, list)):
            output = output[0]

        prob = F.softmax(output, dim=1)
        pred = torch.argmax(prob, dim=1).squeeze(0)  # (H, W)

    return pred.cpu().numpy(), prob.cpu().numpy()


def label_to_rgb(label):
    """Convert label mask sang RGB."""
    colors = np.array([
        [0, 0, 0],       # Background
        [255, 0, 0],     # NCR/NET
        [0, 255, 0],     # ED
        [255, 255, 0],   # ET
    ]) / 255.0

    rgb = np.zeros((*label.shape, 3))
    for i in range(4):
        mask = label == i
        rgb[mask] = colors[i]
    return rgb


def calculate_dice_scores(gt, pred, num_classes=4):
    """Tính Dice cho từng class 1..3."""
    dice_scores = []
    for cls in range(1, num_classes):
        intersection = np.sum((pred == cls) & (gt == cls))
        union = np.sum(pred == cls) + np.sum(gt == cls)
        dice = 2 * intersection / (union + 1e-8)
        dice_scores.append(dice)
    return dice_scores


def visualize_prediction(img, gt, pred, sample_name, save_path=None):
    """Visualize input, ground truth và prediction."""
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))

    modality_names = ['FLAIR', 'T1', 'T1ce', 'T2']

    # Row 1: 4 modalities
    for i in range(4):
        axes[0, i].imshow(img[i], cmap='gray')
        axes[0, i].set_title(modality_names[i], fontsize=12)
        axes[0, i].axis('off')

    # Row 2
    axes[1, 0].imshow(label_to_rgb(gt))
    axes[1, 0].set_title('Ground Truth', fontsize=12)
    axes[1, 0].axis('off')

    axes[1, 1].imshow(label_to_rgb(pred))
    axes[1, 1].set_title('Prediction', fontsize=12)
    axes[1, 1].axis('off')

    axes[1, 2].imshow(img[0], cmap='gray')
    axes[1, 2].imshow(label_to_rgb(pred), alpha=0.5)
    axes[1, 2].set_title('Overlay on FLAIR', fontsize=12)
    axes[1, 2].axis('off')

    diff = np.zeros((*gt.shape, 3))
    correct = (pred == gt)
    wrong = (pred != gt)
    diff[correct] = [1, 1, 1]  # white
    diff[wrong] = [1, 0, 0]    # red
    axes[1, 3].imshow(diff)
    axes[1, 3].set_title('Difference (Red=Wrong)', fontsize=12)
    axes[1, 3].axis('off')

    dice_scores = calculate_dice_scores(gt, pred)

    plt.suptitle(
        f'{sample_name}\n'
        f'Dice: NCR/NET={dice_scores[0]:.3f}, ED={dice_scores[1]:.3f}, '
        f'ET={dice_scores[2]:.3f}, Avg={np.mean(dice_scores):.3f}',
        fontsize=14,
        fontweight='bold'
    )

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()
    else:
        plt.show()

    return dice_scores


def get_sample_list(data_root):
    """Lấy danh sách samples."""
    list_path = os.path.join(data_root, 'list', 'dataset.yaml')
    with open(list_path, 'r', encoding='utf-8') as f:
        samples = yaml.load(f, Loader=yaml.SafeLoader)
    return samples


def auto_detect_config(model_path):
    """Auto-detect config path from model path."""
    parts = model_path.replace('\\', '/').split('/')
    for part in parts:
        if part.startswith('brats_') and part.endswith('_2d'):
            model_name = part.replace('brats_', '')
            config_path = os.path.join(CBIM_ROOT, 'config', 'brats', f'{model_name}.yaml')
            if os.path.exists(config_path):
                return config_path
    return None


def resolve_path(path_value, base_root):
    """Nếu path tương đối thì ghép với base_root."""
    if path_value is None:
        return None
    if os.path.isabs(path_value):
        return path_value
    return os.path.join(base_root, path_value)


def main():
    parser = argparse.ArgumentParser(description='Predict BraTS 2D')

    parser.add_argument('--model_path', type=str, default=DEFAULT_MODEL_PATH,
                        help='Path to model checkpoint (.pth)')
    parser.add_argument('--config_path', type=str, default=DEFAULT_CONFIG_PATH,
                        help='Path to config file (auto-detected if not specified)')
    parser.add_argument('--data_root', type=str, default=DEFAULT_DATA_ROOT,
                        help='Path to dataset root')
    parser.add_argument('--sample_idx', type=int, default=0,
                        help='Sample index to predict (used when sample_name is empty)')
    parser.add_argument('--sample_name', type=str, default=DEFAULT_SAMPLE_NAME,
                        help='Sample name to predict')
    parser.add_argument('--save_dir', type=str, default=DEFAULT_SAVE_DIR,
                        help='Directory to save results')
    parser.add_argument('--save_plot', action='store_true', default=DEFAULT_SAVE_PLOT,
                        help='Save plot instead of showing')
    parser.add_argument('--gpu', type=str, default=DEFAULT_GPU,
                        help='GPU id, ví dụ: 0')

    args = parser.parse_args()

    # Resolve paths
    args.model_path = resolve_path(args.model_path, CBIM_ROOT)
    if args.config_path is not None:
        args.config_path = resolve_path(args.config_path, CBIM_ROOT)

    # GPU
    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    print("=" * 60)
    print("BraTS 2D Prediction")
    print("=" * 60)
    print(f"CBIM_ROOT   : {CBIM_ROOT}")
    print(f"DATA_ROOT   : {args.data_root}")
    print(f"MODEL_PATH  : {args.model_path}")
    print(f"SAMPLE_NAME : {args.sample_name}")
    print(f"GPU         : {args.gpu}")
    print(f"DEVICE      : {device}")
    print("=" * 60)

    # Auto detect config
    if args.config_path is None:
        args.config_path = auto_detect_config(args.model_path)
        if args.config_path is None:
            args.config_path = os.path.join(CBIM_ROOT, 'config', 'brats', 'unet_2d.yaml')

    print(f"CONFIG_PATH : {args.config_path}")

    if not os.path.exists(args.model_path):
        raise FileNotFoundError(f"Model not found: {args.model_path}")

    if not os.path.exists(args.data_root):
        raise FileNotFoundError(f"Data root not found: {args.data_root}")

    if not os.path.exists(args.config_path):
        raise FileNotFoundError(f"Config not found: {args.config_path}")

    # Load model
    print("\nLoading model...")
    model, model_args = load_model(args.model_path, args.config_path, device)

    # Resolve sample
    if args.sample_name and str(args.sample_name).strip():
        sample_name = args.sample_name.strip()
    else:
        samples = get_sample_list(args.data_root)
        if args.sample_idx < 0 or args.sample_idx >= len(samples):
            raise IndexError(f"sample_idx={args.sample_idx} is out of range. Total samples: {len(samples)}")
        sample_name = samples[args.sample_idx]

    print(f"Predicting sample: {sample_name}")

    # Load sample
    img, gt, name = load_sample(args.data_root, sample_name)

    # Predict
    pred, prob = predict(model, img, device)

    # Save path
    save_path = None
    if args.save_dir or args.save_plot:
        if args.save_dir:
            os.makedirs(args.save_dir, exist_ok=True)
            save_path = os.path.join(args.save_dir, f'{sample_name}_prediction.png')
        else:
            save_path = f'{sample_name}_prediction.png'

    # Visualize
    dice_scores = visualize_prediction(img, gt, pred, sample_name, save_path)

    print("\n" + "=" * 60)
    print("Results:")
    print(f"  NCR/NET Dice: {dice_scores[0]:.4f}")
    print(f"  ED Dice     : {dice_scores[1]:.4f}")
    print(f"  ET Dice     : {dice_scores[2]:.4f}")
    print(f"  Average Dice: {np.mean(dice_scores):.4f}")
    print("=" * 60)


if __name__ == '__main__':
    main()