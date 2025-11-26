# pip install mozjpeg-lossless-optimization pillow
import mozjpeg_lossless_optimization
from io import BytesIO
from PIL import Image
import os
import time

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.tiff')
OUTPUT_EXTENSION = ".jpg"


def _optimize_single_image(input_path, output_path, quality):
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return 0, 0, 0

    original_size = os.path.getsize(input_path)
    start_time = time.time()

    try:
        jpeg_io = BytesIO()
        with Image.open(input_path, "r") as image:
            image.convert("RGB").save(jpeg_io, format="JPEG", quality=quality)

        jpeg_io.seek(0)
        jpeg_bytes = jpeg_io.read()

        optimized_jpeg_bytes = mozjpeg_lossless_optimization.optimize(jpeg_bytes)

        with open(output_path, "wb") as output_file:
            output_file.write(optimized_jpeg_bytes)

        duration = time.time() - start_time
        optimized_size = os.path.getsize(output_path)

        savings = original_size - optimized_size
        savings_percent = (savings / original_size) * 100 if original_size > 0 else 0

        print(
            f"  > Optimized {os.path.basename(input_path)}: {original_size / 1024:.1f}KB -> {optimized_size / 1024:.1f}KB ({savings_percent:.1f}% saved) in {duration:.3f}s")

        return original_size, optimized_size, duration

    except Exception as e:
        print(f"\n Error optimizing {input_path}: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return 0, 0, 0


def optimize_folder_batch(input_dir, output_dir, quality=90):
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory not found at {input_dir}")
        return

    total_original_size = 0
    total_optimized_size = 0
    total_duration = 0
    total_files_processed = 0
    total_files_skipped = 0

    start_time = time.time()

    print("-" * 60)
    print(f"Starting MozJPEG Optimization of Folder: {input_dir}")
    print(f"Initial JPEG Quality Target: {quality}")
    print("-" * 60)

    for root, _, files in os.walk(input_dir):
        relative_dir = os.path.relpath(root, input_dir)

        target_dir = os.path.join(output_dir, relative_dir)
        os.makedirs(target_dir, exist_ok=True)

        for filename in files:
            input_path = os.path.join(root, filename)

            _, ext = os.path.splitext(filename)
            if ext.lower() not in IMAGE_EXTENSIONS:
                total_files_skipped += 1
                continue

            base, _ = os.path.splitext(filename)
            output_filename = base + "_optimized" + OUTPUT_EXTENSION
            output_path = os.path.join(target_dir, output_filename)

            print(f"  [PROCESS]: {os.path.join(relative_dir, filename)}...")

            original_size, optimized_size, duration = _optimize_single_image(
                input_path,
                output_path,
                quality
            )

            if original_size > 0:
                total_original_size += original_size
                total_optimized_size += optimized_size
                total_duration += duration
                total_files_processed += 1

    total_files = total_files_processed
    end_time = time.time()
    total_elapsed_time = end_time - start_time

    if total_files == 0:
        print("\nNo eligible image files found to optimize.")
        return

    total_savings = total_original_size - total_optimized_size
    total_savings_percent = (total_savings / total_original_size) * 100

    total_size_mb = total_original_size / (1024 * 1024)
    speed_mbps = total_size_mb / total_elapsed_time if total_elapsed_time > 0 else 0

    print("\n" + "=" * 60)
    print("        FOLDER OPTIMIZATION COMPLETE")
    print("=" * 60)
    print(f"Total Files Processed: {total_files} | Skipped: {total_files_skipped}")
    print(f"Total Time Taken: {total_elapsed_time:.4f} seconds")
    print("-" * 60)
    print(f"Original Total Size: {total_original_size / 1024 / 1024:.2f} MB")
    print(f"Optimized Total Size: {total_optimized_size / 1024 / 1024:.2f} MB")
    print(f"Overall Space Saved: **{total_savings_percent:.2f}%**")
    print(f"Average Processing Speed: **{speed_mbps:.2f} MB/s**")
    print("=" * 60 + "\n")


# --- Test ---
#INPUT_DIR = "input/image/I-3"
#OUTPUT_DIR = "output/image/MOZJPEG_90/I-3"
#JPEG_QUALITY = 90

#optimize_folder_batch(INPUT_DIR, OUTPUT_DIR, quality=JPEG_QUALITY)
