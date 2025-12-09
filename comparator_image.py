#pip install scikit-image
import numpy as np
from PIL import Image
import os
import re
from skimage.metrics import structural_similarity as ssim


def calculate_metrics(image_path_1: str, image_path_2: str, max_i: float = 255.0):
    try:
        img_a_rgb = np.array(Image.open(image_path_1).convert('RGB'))
        img_b_rgb = np.array(Image.open(image_path_2).convert('RGB'))

        img_a_gray = np.array(Image.open(image_path_1).convert('L'))
        img_b_gray = np.array(Image.open(image_path_2).convert('L'))

    except FileNotFoundError:
        print(f"File not found: {image_path_1} or {image_path_2}")
        return None, None, None
    except Exception as e:
        print(f"Error loading images: {e} for {os.path.basename(image_path_1)} and {os.path.basename(image_path_2)}")
        return None, None, None

    if img_a_rgb.shape != img_b_rgb.shape:
        print(
            f"Error: Dimension mismatch between {os.path.basename(image_path_1)} and {os.path.basename(image_path_2)}")
        return None, None, None

    difference = img_a_rgb.astype("float") - img_b_rgb.astype("float")
    squared_difference = difference ** 2
    mse_value = np.mean(squared_difference)

    if mse_value == 0:
        psnr_value = 100.0
    else:
        psnr_value = 10 * np.log10((max_i ** 2) / mse_value)

    ssim_value = ssim(img_a_gray, img_b_gray, data_range=255)

    return mse_value, psnr_value, ssim_value


def compare_folders(input_dir: str, output_dir: str, optimized_suffix: str):
    input_images = {}
    output_images = {}

    IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')

    for root, _, files in os.walk(input_dir):
        relative_dir = os.path.relpath(root, input_dir)

        for filename in files:
            if filename.startswith('.'): continue
            if not filename.lower().endswith(IMAGE_EXTENSIONS): continue

            stem, _ = os.path.splitext(filename)
            map_key = os.path.join(relative_dir, stem)
            input_images[map_key] = os.path.join(relative_dir, filename)

    pattern = re.compile(f'(.+?){optimized_suffix}(\..+)?$', re.IGNORECASE)

    for root, _, files in os.walk(output_dir):
        relative_dir = os.path.relpath(root, output_dir)

        for filename in files:
            if filename.startswith('.'): continue

            match = pattern.match(filename)
            if match:
                original_stem = match.group(1)
                map_key = os.path.join(relative_dir, original_stem)
                output_images[map_key] = os.path.join(relative_dir, filename)

    results = []

    if not input_images:
        print(f"\nNo image files found in the '{input_dir}' directory.")
        return

    for map_key, input_relative_path in sorted(input_images.items()):

        input_full_path = os.path.join(input_dir, input_relative_path)

        if map_key in output_images:
            output_relative_path = output_images[map_key]
            output_full_path = os.path.join(output_dir, output_relative_path)

            output_filename = os.path.basename(output_relative_path)
            if not output_filename.lower().endswith(IMAGE_EXTENSIONS):
                results.append({'filename': input_relative_path, 'mse': 'N/A', 'psnr': 'N/A', 'ssim': 'N/A',
                                'status': 'Output File is Not an Image'})
                continue

            mse, psnr, ssim_score = calculate_metrics(input_full_path, output_full_path, max_i=255.0)

            results.append({
                'filename': input_relative_path,
                'mse': f"{mse:.4f}" if mse is not None else 'Error',
                'psnr': f"{psnr:.2f}" if psnr is not None else 'Error',
                'ssim': f"{ssim_score:.4f}" if ssim_score is not None else 'Error',
                'status': 'OK' if mse is not None else 'Error'
            })
        else:
            results.append({
                'filename': input_relative_path,
                'mse': 'N/A', 'psnr': 'N/A', 'ssim': 'N/A',
                'status': f'Missing Optimized File ({os.path.basename(map_key)}{optimized_suffix}*)'
            })

    print("\n--- Image Quality Comparison Results (MSE/PSNR/SSIM) ---")

    FN_WIDTH = 45
    MSE_WIDTH = 12
    PSNR_WIDTH = 10
    SSIM_WIDTH = 8
    STATUS_WIDTH = 35
    TOTAL_WIDTH = FN_WIDTH + MSE_WIDTH + PSNR_WIDTH + SSIM_WIDTH + STATUS_WIDTH + 4

    header = (
        f"{'Original Path/File':<{FN_WIDTH}} "
        f"{'MSE':>{MSE_WIDTH}} "
        f"{'PSNR (dB)':>{PSNR_WIDTH}} "
        f"{'SSIM':>{SSIM_WIDTH}} "
        f"{'Status':<{STATUS_WIDTH}}"
    )
    print(header)
    print("-" * TOTAL_WIDTH)

    for r in results:
        display_filename = r['filename']
        if len(display_filename) >= FN_WIDTH:
            display_filename = "..." + display_filename[-(FN_WIDTH - 3):]

        line = (
            f"{display_filename:<{FN_WIDTH}} "
            f"{r['mse']:>{MSE_WIDTH}} "
            f"{r['psnr']:>{PSNR_WIDTH}} "
            f"{r['ssim']:>{SSIM_WIDTH}} "
            f"{r['status']:<{STATUS_WIDTH}}"
        )
        print(line)

# --- Test ---
# INPUT_DIR = 'input/image/I-3'
# OUTPUT_DIR = 'output/image/MOZJPEG_90/I-3'
# OPTIMIZED_SUFFIX = '_optimized'
# compare_folders(INPUT_DIR, OUTPUT_DIR, OPTIMIZED_SUFFIX)
