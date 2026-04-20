import os
import sys
import argparse
import numpy as np
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CBIM_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', 'CBIM-Medical-Image-Segmentation'))
if CBIM_ROOT not in sys.path:
    sys.path.insert(0, CBIM_ROOT)

from model.utils import get_model


# =========================
# DEFAULTS: điền sẵn ở đây
# =========================
DEFAULT_MODEL_PATH = r'exp\brats\brats_fsfa_unet_2d\epoc47\fold_0_latest.pth'
DEFAULT_SAMPLE_NAME = 'BraTS2021_00000_slice070'
DEFAULT_DATA_ROOT = r'D:/research2025/y_te/code/CBIM-Medical-Image-Segmentation/dataset/brats2021_2d'
DEFAULT_GPU = '0'


def load_model(model_path, config_path, device='cuda'):
    """Load trained model từ checkpoint."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    class Args:
        pass

    args = Args()
    for key, value in config.items():
        setattr(args, key, value)

    if not hasattr(args, 'dimension'):
        args.dimension = '2d'

    if hasattr(args, 'arch') and not hasattr(args, 'model'):
        args.model = args.arch

    model = get_model(args)
    checkpoint = torch.load(model_path, map_location=device)

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
    """Load một sample chỉ gồm image, không dùng mask/gt."""
    npz_path = os.path.join(data_root, f'{sample_name}.npz')
    if os.path.exists(npz_path):
        data = np.load(npz_path)
        img = data['data'].astype(np.float32)  # (4, H, W)
        return img, sample_name

    img_path = os.path.join(data_root, f'{sample_name}_img.npy')
    if os.path.exists(img_path):
        img = np.load(img_path).astype(np.float32)  # (4, H, W)
        return img, sample_name

    raise FileNotFoundError(f"Sample not found: {sample_name} (tried .npz and .npy formats)")


def normalize(img):
    """Normalize mỗi modality."""
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
        tensor_img = torch.from_numpy(img).float().unsqueeze(0).to(device)  # (1, 4, H, W)

        output = model(tensor_img)
        if isinstance(output, (tuple, list)):
            output = output[0]

        prob = F.softmax(output, dim=1)
        pred = torch.argmax(prob, dim=1).squeeze(0)  # (H, W)

    return pred.cpu().numpy(), prob.cpu().numpy()


def visualize_prediction(img, pred, sample_name, save_path=None):
    """Chỉ visualize ảnh FLAIR và ảnh FLAIR overlay kết quả prediction."""
    colors = np.array([
        [0, 0, 0],       # Background
        [255, 0, 0],     # NCR/NET - Red
        [0, 255, 0],     # ED - Green
        [255, 255, 0],   # ET - Yellow
    ]) / 255.0

    def label_to_rgb(label):
        rgb = np.zeros((*label.shape, 3), dtype=np.float32)
        for i in range(4):
            rgb[label == i] = colors[i]
        return rgb

    flair = img[0]  # channel 0 = FLAIR
    pred_rgb = label_to_rgb(pred)

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    axes[0].imshow(flair, cmap='gray')
    axes[0].set_title('FLAIR', fontsize=12)
    axes[0].axis('off')

    axes[1].imshow(flair, cmap='gray')
    axes[1].imshow(pred_rgb, alpha=0.5)
    axes[1].set_title('FLAIR Overlay Prediction', fontsize=12)
    axes[1].axis('off')

    plt.suptitle(sample_name, fontsize=14, fontweight='bold')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()
    else:
        plt.show()


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


def main():
    parser = argparse.ArgumentParser(description='Predict BraTS 2D')

    parser.add_argument('--model_path', type=str, default=DEFAULT_MODEL_PATH,
                        help='Path to model checkpoint (.pth)')
    parser.add_argument('--config_path', type=str, default=None,
                        help='Path to config file (auto-detected if not specified)')
    parser.add_argument('--data_root', type=str, default=DEFAULT_DATA_ROOT,
                        help='Path to dataset')
    parser.add_argument('--sample_idx', type=int, default=0,
                        help='Sample index to predict (chỉ dùng khi không có sample_name)')
    parser.add_argument('--sample_name', type=str, default=DEFAULT_SAMPLE_NAME,
                        help='Sample name to predict')
    parser.add_argument('--save_dir', type=str, default=None,
                        help='Directory to save results')
    parser.add_argument('--save_plot', action='store_true',
                        help='Save plot instead of showing')
    parser.add_argument('--gpu', type=str, default=DEFAULT_GPU)

    args = parser.parse_args()

    if not os.path.isabs(args.model_path):
        args.model_path = os.path.join(CBIM_ROOT, args.model_path)

    if args.config_path is not None and not os.path.isabs(args.config_path):
        args.config_path = os.path.join(CBIM_ROOT, args.config_path)

    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    print("=" * 50)
    print("BraTS 2D Prediction")
    print("=" * 50)

    if args.config_path is None:
        args.config_path = auto_detect_config(args.model_path)
        if args.config_path is None:
            args.config_path = os.path.join(CBIM_ROOT, 'config', 'brats', 'unet_2d.yaml')
        print(f"Auto-detected config: {args.config_path}")

    print(f"Loading model from: {args.model_path}")
    model, model_args = load_model(args.model_path, args.config_path, device)

    print(f"Predicting sample: {args.sample_name}")

    img, name = load_sample(args.data_root, args.sample_name)

    pred, prob = predict(model, img, device)

    save_path = None
    if args.save_dir or args.save_plot:
        if args.save_dir:
            os.makedirs(args.save_dir, exist_ok=True)
            save_path = os.path.join(args.save_dir, f'{args.sample_name}_prediction.png')
        else:
            save_path = f'{args.sample_name}_prediction.png'

    visualize_prediction(img, pred, name, save_path)

    print("\nDone.")


if __name__ == '__main__':
    main()