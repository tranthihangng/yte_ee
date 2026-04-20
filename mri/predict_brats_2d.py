"""
Script để predict với BraTS 2D models.
Hỗ trợ visualize kết quả segmentation.

Usage:
    # Predict một sample
    python predict_brats_2d.py --model_path exp/brats/test/fold_0_best.pth --sample_idx 0
    
    # Predict và lưu kết quả
    python predict_brats_2d.py --model_path exp/brats/test/fold_0_best.pth --sample_idx 0 --save_dir results/
"""

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


def load_model(model_path, config_path, device='cuda'):
    """Load trained model từ checkpoint."""
    
    # Load config
    with open(config_path, 'r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    
    # Create args namespace
    class Args:
        pass
    args = Args()
    for key, value in config.items():
        setattr(args, key, value)
    
    # Set dimension (required by get_model)
    if not hasattr(args, 'dimension'):
        args.dimension = '2d'  # Default for this script
    
    # Map 'arch' to 'model' if needed
    if hasattr(args, 'arch') and not hasattr(args, 'model'):
        args.model = args.arch
    
    # Load model
    model = get_model(args)
    checkpoint = torch.load(model_path, map_location=device)
    
    # Try to load EMA model first, fallback to regular model
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
    # Try .npz format first (new format)
    npz_path = os.path.join(data_root, f'{sample_name}.npz')
    if os.path.exists(npz_path):
        data = np.load(npz_path)
        img = data['data'].astype(np.float32)  # (4, H, W)
        seg = data.get('label', np.zeros(img.shape[1:], dtype=np.uint8))
        if seg is not None:
            seg = seg.astype(np.uint8)
        return img, seg, sample_name
    
    # Try .npy format (old format)
    img_path = os.path.join(data_root, f'{sample_name}_img.npy')
    seg_path = os.path.join(data_root, f'{sample_name}_seg.npy')
    
    if os.path.exists(img_path):
        img = np.load(img_path).astype(np.float32)  # (4, H, W)
        seg = np.load(seg_path).astype(np.uint8) if os.path.exists(seg_path) else np.zeros(img.shape[1:], dtype=np.uint8)
        return img, seg, sample_name
    
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
        # Normalize
        img = normalize(img.copy())
        
        # To tensor: (4, H, W) -> (1, 4, H, W)
        tensor_img = torch.from_numpy(img).float().unsqueeze(0).to(device)
        
        # Predict
        output = model(tensor_img)
        
        if isinstance(output, (tuple, list)):
            output = output[0]
        
        # Softmax và lấy argmax
        prob = F.softmax(output, dim=1)
        pred = torch.argmax(prob, dim=1).squeeze(0)  # (H, W)
        
    return pred.cpu().numpy(), prob.cpu().numpy()


def visualize_prediction(img, gt, pred, sample_name, save_path=None):
    """Visualize input, ground truth và prediction."""
    
    # Color map cho BraTS classes
    # 0: Background (black)
    # 1: NCR/NET - Necrotic (red)
    # 2: ED - Edema (green)  
    # 3: ET - Enhancing Tumor (yellow)
    colors = np.array([
        [0, 0, 0],       # Background
        [255, 0, 0],     # NCR/NET - Red
        [0, 255, 0],     # ED - Green
        [255, 255, 0],   # ET - Yellow
    ]) / 255.0
    
    def label_to_rgb(label):
        rgb = np.zeros((*label.shape, 3))
        for i in range(4):
            mask = label == i
            rgb[mask] = colors[i]
        return rgb
    
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    
    # Row 1: 4 modalities
    modality_names = ['FLAIR', 'T1', 'T1ce', 'T2']
    for i in range(4):
        axes[0, i].imshow(img[i], cmap='gray')
        axes[0, i].set_title(modality_names[i], fontsize=12)
        axes[0, i].axis('off')
    
    # Row 2: GT, Prediction, Overlay, Difference
    axes[1, 0].imshow(label_to_rgb(gt))
    axes[1, 0].set_title('Ground Truth', fontsize=12)
    axes[1, 0].axis('off')
    
    axes[1, 1].imshow(label_to_rgb(pred))
    axes[1, 1].set_title('Prediction', fontsize=12)
    axes[1, 1].axis('off')
    
    # Overlay on FLAIR
    axes[1, 2].imshow(img[0], cmap='gray')
    axes[1, 2].imshow(label_to_rgb(pred), alpha=0.5)
    axes[1, 2].set_title('Overlay on FLAIR', fontsize=12)
    axes[1, 2].axis('off')
    
    # Difference (correct=white, wrong=red)
    diff = np.zeros((*gt.shape, 3))
    correct = (pred == gt)
    wrong = (pred != gt)
    diff[correct] = [1, 1, 1]  # White
    diff[wrong] = [1, 0, 0]    # Red
    axes[1, 3].imshow(diff)
    axes[1, 3].set_title('Difference (Red=Wrong)', fontsize=12)
    axes[1, 3].axis('off')
    
    # Calculate Dice
    dice_scores = []
    for cls in range(1, 4):
        intersection = np.sum((pred == cls) & (gt == cls))
        union = np.sum(pred == cls) + np.sum(gt == cls)
        dice = 2 * intersection / (union + 1e-8)
        dice_scores.append(dice)
    
    plt.suptitle(f'{sample_name}\nDice: NCR/NET={dice_scores[0]:.3f}, ED={dice_scores[1]:.3f}, ET={dice_scores[2]:.3f}, Avg={np.mean(dice_scores):.3f}', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()  # Close instead of show when saving
    else:
        plt.show()

    return dice_scores


def get_sample_list(data_root):
    """Lấy danh sách samples."""
    list_path = os.path.join(data_root, 'list', 'dataset.yaml')
    with open(list_path, 'r') as f:
        samples = yaml.load(f, Loader=yaml.SafeLoader)
    return samples


def auto_detect_config(model_path):
    """Auto-detect config path from model path."""
    # Extract model name from path like: exp/brats/brats_fsfa_unet_2d/fold_0_best.pth
    parts = model_path.replace('\\', '/').split('/')
    for part in parts:
        if part.startswith('brats_') and part.endswith('_2d'):
            # e.g., brats_fsfa_unet_2d -> fsfa_unet_2d
            model_name = part.replace('brats_', '')
            config_path = os.path.join(CBIM_ROOT, 'config', 'brats', f'{model_name}.yaml')
            if os.path.exists(config_path):
                return config_path
    return None


def main():
    parser = argparse.ArgumentParser(description='Predict BraTS 2D')
    parser.add_argument('--model_path', type=str, required=True,
                        help='Path to model checkpoint (.pth)')
    parser.add_argument('--config_path', type=str, default=None,
                        help='Path to config file (auto-detected if not specified)')
    parser.add_argument('--data_root', type=str, 
                        default='D:/research2025/y_te/code/CBIM-Medical-Image-Segmentation/dataset/brats2021_2d',
                        help='Path to dataset')
    parser.add_argument('--sample_idx', type=int, default=0,
                        help='Sample index to predict')
    parser.add_argument('--sample_name', type=str, default=None,
                        help='Sample name to predict (overrides sample_idx)')
    parser.add_argument('--save_dir', type=str, default=None,
                        help='Directory to save results')
    parser.add_argument('--save_plot', action='store_true',
                        help='Save plot instead of showing')
    parser.add_argument('--gpu', type=str, default='0')
    
    args = parser.parse_args()

    if not os.path.isabs(args.model_path):
        args.model_path = os.path.join(CBIM_ROOT, args.model_path)
    if args.config_path is not None and not os.path.isabs(args.config_path):
        args.config_path = os.path.join(CBIM_ROOT, args.config_path)
    
    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    print("="*50)
    print("BraTS 2D Prediction")
    print("="*50)
    
    # Auto-detect config if not specified
    if args.config_path is None:
        args.config_path = auto_detect_config(args.model_path)
        if args.config_path is None:
            # Default fallback
            args.config_path = os.path.join(CBIM_ROOT, 'config', 'brats', 'unet_2d.yaml')
        print(f"Auto-detected config: {args.config_path}")
    
    # Load model
    print(f"Loading model from: {args.model_path}")
    model, model_args = load_model(args.model_path, args.config_path, device)
    
    # Get sample
    samples = get_sample_list(args.data_root)
    
    if args.sample_name:
        sample_name = args.sample_name
    else:
        sample_name = samples[args.sample_idx]
    
    print(f"Predicting sample: {sample_name}")
    
    # Load sample
    img, gt, name = load_sample(args.data_root, sample_name)
    
    # Predict
    pred, prob = predict(model, img, device)
    
    # Visualizecdcd
    save_path = None
    if args.save_dir or args.save_plot:
        if args.save_dir:
            os.makedirs(args.save_dir, exist_ok=True)
            save_path = os.path.join(args.save_dir, f'{sample_name}_prediction.png')
        else:
            # Auto save to current directory
            save_path = f'{sample_name}_prediction.png'

    dice_scores = visualize_prediction(img, gt, pred, sample_name, save_path)
    
    print("\n" + "="*50)
    print("Results:")
    print(f"  NCR/NET Dice: {dice_scores[0]:.4f}")
    print(f"  ED Dice:      {dice_scores[1]:.4f}")
    print(f"  ET Dice:      {dice_scores[2]:.4f}")
    print(f"  Average Dice: {np.mean(dice_scores):.4f}")
    print("="*50)


if __name__ == '__main__':
    main()

