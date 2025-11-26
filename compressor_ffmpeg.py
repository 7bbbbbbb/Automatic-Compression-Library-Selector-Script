import subprocess
import os
import time


def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, capture_output=True, text=True)
        return True
    except FileNotFoundError:
        print("\nFATAL ERROR: FFmpeg is not found.")
        print("Please ensure FFmpeg is installed on your system and available in the PATH.")
        return False


def _execute_ffmpeg_command(command, input_path, output_path, original_size, start_time):

    try:
        process = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )

        optimized_size = os.path.getsize(output_path)
        duration = time.time() - start_time

        savings_percent = (1 - (optimized_size / original_size)) * 100 if original_size > 0 else 0

        print(f"  > Original Size: {original_size / (1024 * 1024):.2f} MB")
        print(f"  > Output Size: {optimized_size / (1024 * 1024):.2f} MB")
        print(f"  > Time Taken:  {duration:.2f} seconds")
        print(f"  > Reduction:   **{savings_percent:.2f}%**")

        return original_size, optimized_size, duration

    except subprocess.CalledProcessError as e:
        print(f"\nError processing {os.path.basename(input_path)}: FFmpeg failed with exit code {e.returncode}.")
        print(f"FFmpeg Output (Stderr): {e.stderr}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return 0, 0, 0

    except Exception as e:
        print(f"\nAn unexpected error occurred during execution: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return 0, 0, 0


def _process_single_file(input_path, output_path, codec, crf):

    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
        return 0, 0, 0

    original_size = os.path.getsize(input_path)
    start_time = time.time()

    command = None

    if codec == 'h264':
        command = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx264',
            '-crf', str(crf),
            '-c:a', 'copy',
            '-y', output_path
        ]
        print(f"  > Codec: H.264 (libx264) | CRF: {crf}")
    elif codec == 'hevc':
        command = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx265',
            '-crf', str(crf),
            '-c:a', 'copy',
            '-y', output_path
        ]
        print(f"  > Codec: HEVC (libx265) | CRF: {crf}")
    elif codec == 'av1':
        command = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libaom-av1',
            '-crf', str(crf),
            '-cpu-used', '8',  # Speed preset (0=slowest, 8=fastest)
            '-c:a', 'copy',
            '-y', output_path
        ]
        print(f"  > Codec: AV1 (libaom-av1) | CRF: {crf} | Speed: 8")
    else:
        print(f"Error: Unsupported codec '{codec}'. Supported: 'h264', 'hevc', and 'av1'.")
        return 0, 0, 0

    return _execute_ffmpeg_command(command, input_path, output_path, original_size, start_time)


def process_video_folder(input_dir, output_dir, codec='av1', crf=30):
    print("=" * 70)
    print("Starting Video Batch Compression")
    print("-" * 70)
    print(f"Input Directory: {input_dir}")
    print(f"Output Directory: {output_dir}")
    print(f"Target Codec: {codec.upper()} | Target CRF: {crf}")
    print("=" * 70)

    if not check_ffmpeg():
        return

    if not os.path.isdir(input_dir):
        print(f"Error: Input directory not found at {input_dir}")
        return

    if codec == 'h264':
        output_ext = ".mp4"
    elif codec in ('hevc', 'av1'):
        output_ext = ".mkv"
    else:
        return

    total_original_size = 0
    total_compressed_size = 0
    total_time_spent = 0
    total_files_processed = 0
    total_files_skipped = 0

    start_time_batch = time.time()

    ELIGIBLE_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.ts', '.wmv')

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
            output_path = os.path.join(target_dir, base + output_ext)

            original_size, compressed_size, duration = _process_single_file(
                input_path,
                output_path,
                codec,
                crf
            )

            if original_size > 0:
                total_original_size += original_size
                total_compressed_size += compressed_size
                total_time_spent += duration
                total_files_processed += 1

    total_elapsed_time = time.time() - start_time_batch

    print("\n" + "=" * 70)
    if total_files_processed == 0:
        print("        Batch Video Compression Failed or no Eligible Files Processed")
        print("=" * 70)
        return

    total_savings = total_original_size - total_compressed_size
    total_savings_percent = (total_savings / total_original_size) * 100

    print("        Batch Video Compression Complete")
    print("=" * 70)
    print(f"Total Files Processed: {total_files_processed} | Skipped: {total_files_skipped}")
    print(f"Total Time Taken: {total_elapsed_time:.4f} seconds")
    print("-" * 70)
    print(f"Original Total Size: {total_original_size / (1024 * 1024):.2f} MB")
    print(f"Compressed Total Size: {total_compressed_size / (1024 * 1024):.2f} MB")
    print(f"Overall Space Saved: **{total_savings_percent:.2f}%**")
    print("=" * 70 + "\n")


# --- Test ---
#INPUT_DIR = "input/video/V-3"
#OUTPUT_DIR = "output/video/AV1/V-3"

#TARGET_CODEC = 'av1' # 'h264' (libx264, MP4), 'hevc' (libx265, MKV), or 'av1' (libaom-av1, MKV)
#TARGET_CRF = 30 # 18 (high quality), 30 (high compression)

#process_video_folder(INPUT_DIR, OUTPUT_DIR, TARGET_CODEC, TARGET_CRF)