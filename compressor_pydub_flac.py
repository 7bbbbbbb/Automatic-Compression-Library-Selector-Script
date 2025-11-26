# Requires 'pip install pydub' and having 'ffmpeg' installed and in your system PATH.
from pydub import AudioSegment
from pydub.utils import which
import os
import time


def _compress_single_file_flac(input_path, output_path, compression_level):
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return 0, 0, 0

    original_size = os.path.getsize(input_path)
    start_time = time.time()
    filename = os.path.basename(input_path)

    try:
        audio = AudioSegment.from_file(input_path)

        audio.export(
            output_path,
            format="flac",
            parameters=['-compression_level', str(compression_level)]
        )

        compressed_size = os.path.getsize(output_path)
        processing_time = time.time() - start_time

        track_duration_s = len(audio) / 1000.0

        savings_percent = (1 - (compressed_size / original_size)) * 100 if original_size > 0 else 0

        print(f"  > Track Duration: {track_duration_s:.2f} seconds")
        print(f"  > Original Size: {original_size / (1024 * 1024):.2f} MB")
        print(f"  > FLAC Size:     {compressed_size / (1024 * 1024):.2f} MB")
        print(f"  > Savings:       **{savings_percent:.1f}%**")
        print(f"  > Time Taken:    {processing_time:.3f} seconds")

        return original_size, compressed_size, track_duration_s

    except Exception as e:
        print(f"Error processing {filename}: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return 0, 0, 0


def compress_folder_to_flac(input_dir, output_dir, compression_level=5):

    AudioSegment.converter = which("ffmpeg")
    if AudioSegment.converter is None:
        print("\nFATAL ERROR: FFmpeg not found.")
        print("pydub requires FFmpeg to export audio. Please install it and add it to your PATH.")
        return

    if not os.path.isdir(input_dir):
        print(f"Error: Input directory not found at {input_dir}")
        return

    total_original_size = 0
    total_compressed_size = 0
    total_track_duration = 0
    total_files_processed = 0
    total_files_skipped = 0

    start_time_batch = time.time()

    ELIGIBLE_EXTENSIONS = ('.wav', '.flac', '.ogg', '.aiff', '.mp3', '.m4a', '.wma')

    print("=" * 70)
    print(f"Starting Audio Batch Compression (Target Format: FLAC Level {compression_level})")
    print("Output format: FLAC | Preserving directory structure.")
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
            output_filename = base + ".flac"
            output_path = os.path.join(target_dir, output_filename)

            original_size, compressed_size, track_duration_s = _compress_single_file_flac(
                input_path,
                output_path,
                compression_level
            )

            if original_size > 0:
                total_original_size += original_size
                total_compressed_size += compressed_size
                total_track_duration += track_duration_s
                total_files_processed += 1

    total_elapsed_time = time.time() - start_time_batch

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
    print(f"Total Track Duration: {total_track_duration:.2f} seconds")
    print("-" * 70)
    print(f"Original Total Size: {total_original_size / (1024 * 1024):.2f} MB")
    print(f"Compressed Total Size: {total_compressed_size / (1024 * 1024):.2f} MB")
    print(f"Overall Space Saved: **{total_savings_percent:.2f}%**")
    print("=" * 70 + "\n")


# --- Test ---
#INPUT_DIR = "input/audio/A-3"
#OUTPUT_DIR = "output/audio/FLAC/A-3"
#TARGET_LEVEL = 5  # FLAC Compression Level (0=Fastest, 8=Highest Quality/Smallest Size)

#compress_folder_to_flac(INPUT_DIR, OUTPUT_DIR, compression_level=TARGET_LEVEL)