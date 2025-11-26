import subprocess
import os
import re
import sys
import math
import json
from typing import Dict, Optional, Tuple, List

VIDEO_EXTS = ('.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.ts', '.m4v')


def get_video_bit_depth(video_path: str) -> Optional[int]:
    try:
        ffprobe_command = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=bits_per_raw_sample,bits_per_sample',
            '-of', 'json',
            video_path.replace('\\', '/')
        ]

        process = subprocess.run(
            ffprobe_command,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            timeout=10
        )

        data = json.loads(process.stdout)

        if 'streams' in data and len(data['streams']) > 0:
            stream = data['streams'][0]

            if 'bits_per_raw_sample' in stream and stream['bits_per_raw_sample']:
                return int(stream['bits_per_raw_sample'])

            if 'bits_per_sample' in stream and stream['bits_per_sample']:
                return int(stream['bits_per_sample'])

    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        if isinstance(e, FileNotFoundError):
            print(f"WARNING: 'ffprobe' command not found. Cannot determine bit depth. Assuming 8-bit.")
        elif isinstance(e, subprocess.CalledProcessError):
            print(
                f"WARNING: ffprobe failed for {os.path.basename(video_path)}. Assuming 8-bit. Error: {e.stderr.strip()}")
        else:
            print(
                f"WARNING: Could not determine bit depth for {os.path.basename(video_path)}. Assuming 8-bit. Details: {e}")

        return 8

    return 8


def calculate_mse_from_psnr(psnr_db: float, max_pixel_value_sq: float) -> float:
    if psnr_db < 0 or max_pixel_value_sq <= 0:
        return float('inf')

    denominator = math.pow(10, psnr_db / 10.0)
    mse = max_pixel_value_sq / denominator
    return mse


def parse_ffmpeg_output(output: str, max_pixel_value_sq: float) -> Optional[Dict[str, float]]:
    results = {}

    psnr_match = re.search(r'PSNR .* average:(\d+\.\d+)', output)
    if psnr_match:
        psnr_avg = float(psnr_match.group(1))
        results['PSNR_Avg_dB'] = psnr_avg
        results['MSE_Avg'] = calculate_mse_from_psnr(psnr_avg, max_pixel_value_sq)

    ssim_match = re.search(r'SSIM .* All:(\d+\.\d+)', output)
    if not ssim_match:
        ssim_match = re.search(r'SSIM .* average:(\d+\.\d+)', output)

    if ssim_match:
        results['SSIM_Avg'] = float(ssim_match.group(1))

    return results if all(k in results for k in ['PSNR_Avg_dB', 'SSIM_Avg', 'MSE_Avg']) else None


def run_quality_check(original_path: str, compressed_path: str) -> Optional[Dict[str, float]]:
    bit_depth = get_video_bit_depth(original_path)
    max_val = (2 ** bit_depth) - 1
    max_pixel_value_sq = max_val * max_val

    print(f"   Detected Bit Depth: {bit_depth}-bit (MAX^2 = {max_pixel_value_sq:.0f})")

    ffmpeg_original_path = original_path.replace('\\', '/')
    ffmpeg_compressed_path = compressed_path.replace('\\', '/')

    filter_graph = "[0:v][1:v]psnr;[0:v][1:v]ssim"

    ffmpeg_command = [
        'ffmpeg',
        '-i', ffmpeg_original_path,
        '-i', ffmpeg_compressed_path,
        '-map', '0:v',  # Input 1
        '-map', '1:v',  # Input 2
        '-lavfi', filter_graph,
        '-f', 'null',
        '-'
    ]

    try:
        process = subprocess.run(
            ffmpeg_command,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            timeout=300
        )

        return parse_ffmpeg_output(process.stderr, max_pixel_value_sq)

    except subprocess.CalledProcessError as e:
        print(f"\n!!! ERROR: FFmpeg failed for {os.path.basename(original_path)}. !!!")
        print(f"FFmpeg Output (Error Stream):\n{e.stderr.strip()}")
        if "Invalid argument" in e.stderr or "stream 0:1" in e.stderr:
            print("HINT: Ensure videos have matching resolution, color space, and frame count.")
        return None
    except FileNotFoundError:
        print(
            "\nFATAL ERROR: 'ffmpeg' command not found. Please ensure FFmpeg is installed and accessible in your system PATH.")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f"\nFATAL ERROR: FFmpeg command timed out after 300 seconds for {os.path.basename(original_path)}.")
        return None


def get_video_files(directory: str) -> Dict[str, Tuple[str, str]]:
    video_files = {}
    if not os.path.exists(directory):
        return video_files

    for root, _, files in os.walk(directory):
        relative_dir = os.path.relpath(root, directory)

        for filename in files:
            if filename.startswith('.'): continue

            if not filename.lower().endswith(VIDEO_EXTS): continue

            stem, _ = os.path.splitext(filename)

            map_key = os.path.normpath(os.path.join(relative_dir, stem))

            relative_path_and_filename = os.path.normpath(os.path.join(relative_dir, filename))

            full_path = os.path.join(root, filename)

            video_files[map_key] = (relative_path_and_filename, full_path)

    return video_files


def batch_compare_videos(original_dir: str, compressed_dir: str):
    original_map = get_video_files(original_dir)
    compressed_map = get_video_files(compressed_dir)

    common_keys = original_map.keys() & compressed_map.keys()

    comparison_results: List[Dict] = []

    if not common_keys:
        print("No matching video files found in both directories (including subfolders).")
        return

    print(f"--- Starting Recursive Batch Comparison ({len(common_keys)} pairs) ---")
    print(f"Original Root Dir: {original_dir}")
    print(f"Compressed Root Dir: {compressed_dir}")
    print("-" * 70)

    for map_key in sorted(list(common_keys)):
        original_rel_filename, original_path = original_map[map_key]
        compressed_rel_filename, compressed_path = compressed_map[map_key]

        print(f"\n-> Comparing {original_rel_filename}")

        metrics = run_quality_check(original_path, compressed_path)

        result_row = {
            'Path/Filename': original_rel_filename,
            'MSE_Avg': 'N/A',
            'PSNR_Avg_dB': 'N/A',
            'SSIM_Avg': 'N/A',
            'Status': 'FAILED'
        }

        if metrics:
            result_row.update({
                'MSE_Avg': f"{metrics['MSE_Avg']:.4f}",
                'PSNR_Avg_dB': f"{metrics['PSNR_Avg_dB']:.4f}",
                'SSIM_Avg': f"{metrics['SSIM_Avg']:.4f}",
                'Status': 'OK'
            })
            print(
                f"   RESULTS: MSE: {result_row['MSE_Avg']}, PSNR (dB): {result_row['PSNR_Avg_dB']}, SSIM: {result_row['SSIM_Avg']}")
        else:
            print("   STATUS: Failed to retrieve metrics. Check FFmpeg output for stream errors.")

        comparison_results.append(result_row)

    print("\n\n--- Video Quality Comparison Results  (MSE/PSNR/SSIM) ---")
    if not comparison_results:
        print("No comparisons were completed.")
        return

    PATH_WIDTH = 70
    MSE_WIDTH = 15
    PSNR_WIDTH = 15
    SSIM_WIDTH = 10
    STATUS_WIDTH = 10
    TOTAL_WIDTH = PATH_WIDTH + MSE_WIDTH + PSNR_WIDTH + SSIM_WIDTH + STATUS_WIDTH + 4

    header = (
        f"{'Path/Filename':<{PATH_WIDTH}} "
        f"{'MSE':>{MSE_WIDTH}} "
        f"{'PSNR (dB)':>{PSNR_WIDTH}} "
        f"{'SSIM':>{SSIM_WIDTH}} "
        f"{'Status':<{STATUS_WIDTH}}"
    )
    print(header)
    print("-" * TOTAL_WIDTH)

    for r in comparison_results:
        display_path = r['Path/Filename']
        if len(display_path) > PATH_WIDTH:
            display_path = "..." + display_path[-(PATH_WIDTH - 3):]

        line = (
            f"{display_path:<{PATH_WIDTH}} "
            f"{r['MSE_Avg']:>{MSE_WIDTH}} "
            f"{r['PSNR_Avg_dB']:>{PSNR_WIDTH}} "
            f"{r['SSIM_Avg']:>{SSIM_WIDTH}} "
            f"{r['Status']:<{STATUS_WIDTH}}"
        )
        print(line)

    print("\n--- Batch Comparison Complete ---")

# --- Test ---
# ORIGINAL_DIR = 'input/video/V-3'
# COMPRESSED_DIR = 'output/video/AV1/V-3'
# batch_compare_videos(ORIGINAL_DIR, COMPRESSED_DIR)