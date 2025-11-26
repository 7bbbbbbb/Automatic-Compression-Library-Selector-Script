# Requires 'pip install pydub' and having 'ffmpeg' installed and in your system PATH.
from pydub import AudioSegment
from pydub.utils import which
import os
import time


def _compress_single_file(input_path, output_path, bitrate):
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return 0, 0, 0

    original_size = os.path.getsize(input_path)
    start_time = time.time()
    filename = os.path.basename(input_path)

    try:
        audio = AudioSegment.from_file(input_path)

        audio.export(output_path, format="mp3", bitrate=bitrate)

        compressed_size = os.path.getsize(output_path)
        duration = time.time() - start_time

        savings_percent = (1 - (compressed_size / original_size)) * 100 if original_size > 0 else 0

        print(f"  > Original: {original_size / (1024 * 1024):.2f} MB")
        print(f"  > MP3 Size: {compressed_size / (1024 * 1024):.2f} MB")
        print(f"  > Savings:  **{savings_percent:.1f}%** in {duration:.3f}s")

        return original_size, compressed_size, duration

    except Exception as e:
        print(f"Error processing {filename}: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return 0, 0, 0


def compress_folder_to_mp3(input_dir, output_dir, bitrate="192k"):
    AudioSegment.converter = which("ffmpeg")
    if AudioSegment.converter is None:
        print("\nFATAL ERROR: FFmpeg not found.")
        print("pydub requires FFmpeg to export MP3s. Please install it and add it to your PATH.")
        return

    if not os.path.isdir(input_dir):
        print(f"Error: Input directory not found at {input_dir}")
        return

    total_original_size = 0
    total_compressed_size = 0
    total_duration = 0
    total_files_processed = 0
    total_files_skipped = 0

    start_time = time.time()

    # Supported input formats for pydub
    ELIGIBLE_EXTENSIONS = ('.wav', '.flac', '.ogg', '.aiff', '.mp3', '.m4a', '.wma')

    print("=" * 70)
    print(f"Starting Audio Batch Compression (Target Bitrate: {bitrate})")
    print("Output format: MP3 | Preserving directory structure.")
    print("=" * 70)

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

            print(f"\n--- Processing: {os.path.join(relative_dir, filename)} ---")

            base, _ = os.path.splitext(filename)
            output_filename = base + ".mp3"
            output_path = os.path.join(target_dir, output_filename)  # Use target_dir to preserve structure

            original_size, compressed_size, duration = _compress_single_file(
                input_path,
                output_path,
                bitrate
            )

            if original_size > 0:
                total_original_size += original_size
                total_compressed_size += compressed_size
                total_duration += duration
                total_files_processed += 1

    total_elapsed_time = time.time() - start_time

    print("\n" + "=" * 70)
    if total_files_processed == 0:
        print("        BATCH COMPRESSION FAILED OR NO FILES PROCESSED")
        print("=" * 70)
        return

    total_savings = total_original_size - total_compressed_size
    total_savings_percent = (total_savings / total_original_size) * 100

    print("        BATCH COMPRESSION COMPLETE")
    print("=" * 70)
    print(f"Total Files Processed: {total_files_processed} | Skipped: {total_files_skipped}")
    print(f"Total Time Taken: {total_elapsed_time:.4f} seconds")
    print("-" * 70)
    print(f"Original Total Size: {total_original_size / (1024 * 1024):.2f} MB")
    print(f"Compressed Total Size: {total_compressed_size / (1024 * 1024):.2f} MB")
    print(f"Overall Space Saved: **{total_savings_percent:.2f}%**")
    print("=" * 70 + "\n")


# --- Test ---
#INPUT_DIR = "input/audio/A-1"
#OUTPUT_DIR = "output/audio/PYDUB192/A-1"
#TARGET_BITRATE = "192k" # Common options: 192k, 320k

#compress_folder_to_mp3(INPUT_DIR, OUTPUT_DIR, bitrate=TARGET_BITRATE)
