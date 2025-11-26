# pip install pyoxipng pillow
import oxipng
from PIL import Image
import numpy as np
import os
import time


def _process_image_for_oxipng(input_path, output_path, level=6):
    original_size = os.path.getsize(input_path)
    start_time = time.time()

    try:
        with Image.open(input_path, "r") as image:
            filename = os.path.basename(input_path)

            if filename.lower().endswith(('.jpg', '.jpeg', '.bmp', '.webp')):
                print(f"  > Converting {filename} to PNG format before optimization...")

            prepared_image = image.convert("RGBA")

            rgb_array = np.array(prepared_image, dtype=np.uint8)

        height, width, channels = rgb_array.shape
        data = rgb_array.tobytes()

        color_type = oxipng.ColorType.rgba()
        raw = oxipng.RawImage(data, width, height, color_type=color_type)

        optimized_bytes = raw.create_optimized_png(level=level)

        with open(output_path, "wb") as f:
            f.write(optimized_bytes)

        duration = time.time() - start_time
        optimized_size = os.path.getsize(output_path)

        savings = original_size - optimized_size
        savings_percent = (savings / original_size) * 100 if original_size > 0 else 0

        print(
            f"  > Final Size: {original_size / 1024:.1f}KB (Original) -> {optimized_size / 1024:.1f}KB (Optimized PNG)")
        print(f"  > Savings: {savings_percent:.1f}% in {duration:.3f}s")

        return original_size, optimized_size, duration

    except Exception as e:
        print(f"An error occurred processing {os.path.basename(input_path)}: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return 0, 0, 0


def optimize_folder_with_oxipng(input_dir, output_dir, level=6, png_only=False):
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory not found at {input_dir}")
        return

    total_original_size = 0
    total_optimized_size = 0
    total_duration = 0
    total_files_processed = 0
    total_files_skipped = 0

    start_time = time.time()

    if png_only:
        ELIGIBLE_EXTENSIONS = ('.png',)
    else:
        ELIGIBLE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.webp')

    print("-" * 70)
    print(f"Starting OxiPNG Folder Optimization (Level: {level})")
    print(f"Mode: {'PNG Files Only' if png_only else 'All Supported Images (Converting to PNG)'}")
    print("-" * 70)

    for root, _, files in os.walk(input_dir):
        relative_dir = os.path.relpath(root, input_dir)

        target_dir = os.path.join(output_dir, relative_dir)
        os.makedirs(target_dir, exist_ok=True)

        for filename in files:
            input_path = os.path.join(root, filename)

            _, ext = os.path.splitext(filename)
            if ext.lower() not in ELIGIBLE_EXTENSIONS:
                total_files_skipped += 1
                continue

            print(f"\n--- Processing {os.path.join(relative_dir, filename)} ---")

            base, _ = os.path.splitext(filename)
            output_filename = base + "_optimized.png"
            output_path = os.path.join(target_dir, output_filename)  # Use target_dir

            original_size, optimized_size, duration = _process_image_for_oxipng(
                input_path,
                output_path,
                level
            )

            if original_size > 0 and optimized_size > 0:
                total_original_size += original_size
                total_optimized_size += optimized_size
                total_duration += duration
                total_files_processed += 1

    total_elapsed_time = time.time() - start_time
    total_files = total_files_processed

    if total_files == 0:
        print("\nNo eligible image files were found or successfully processed.")
        return

    total_savings = total_original_size - total_optimized_size
    total_savings_percent = (total_savings / total_original_size) * 100

    total_size_mb = total_original_size / (1024 * 1024)
    speed_mbps = total_size_mb / total_elapsed_time if total_elapsed_time > 0 else 0

    print("\n" + "=" * 70)
    print("        FOLDER OPTIMIZATION COMPLETE")
    print("=" * 70)
    print(f"Files Processed: {total_files} | Files Skipped: {total_files_skipped}")
    print(f"Total Time Taken: {total_elapsed_time:.4f} seconds")
    print("-" * 70)
    print(f"Original Total Size (Source Files): {total_original_size / 1024 / 1024:.2f} MB")
    print(f"Optimized Total Size (Final PNGs): {total_optimized_size / 1024 / 1024:.2f} MB")
    print(f"Overall Space Saved: **{total_savings_percent:.2f}%**")
    print(f"Average Processing Speed: **{speed_mbps:.2f} MB/s** (based on original data size)")
    print("=" * 70 + "\n")


# --- Test ---
#INPUT_DIR = "input/image/I-3"
#OUTPUT_DIR = "output/image/OXIPNG_6/I-3"
#OPTIMIZATION_LEVEL = 6  # Range 1-6

#optimize_folder_with_oxipng(INPUT_DIR, OUTPUT_DIR, level=OPTIMIZATION_LEVEL, png_only=False)
