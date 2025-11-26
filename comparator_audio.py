# pip install librosa numpy
import numpy as np
import librosa
import os
from typing import Optional, Dict, List, Tuple


def calculate_audio_metrics(original_file_path: str, compressed_file_path: str) -> Tuple[
    Optional[float], Optional[float]]:
    try:
        y_orig, sr_orig = librosa.load(original_file_path, sr=None)
        y_comp, sr_comp = librosa.load(compressed_file_path, sr=None)
    except Exception as e:
        print(f"Error processing {os.path.basename(original_file_path)}: {e}")
        return None, None

    if sr_orig != sr_comp:
        try:
            y_comp = librosa.resample(y_comp, orig_sr=sr_comp, target_sr=sr_orig)
        except Exception as e:
            print(f"Resampling error for {os.path.basename(compressed_file_path)}: {e}")
            return None, None

    min_len = min(len(y_orig), len(y_comp))
    y_orig = y_orig[:min_len]
    y_comp = y_comp[:min_len]

    if min_len == 0:
        print(f"Warning: Audio file {os.path.basename(original_file_path)} is empty after processing.")
        return None, None

    difference = y_orig - y_comp
    squared_difference = difference ** 2
    mse_value = np.mean(squared_difference)

    if mse_value == 0:
        psnr_value = 100.0
    else:
        MAX_I_SQUARED = 1.0
        psnr_value = 10 * np.log10(MAX_I_SQUARED / mse_value)

    return mse_value, psnr_value


def compare_folders_recursive(input_dir: str, output_dir: str):
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    AUDIO_EXTS = ('.wav', '.mp3', '.ogg', '.flac', '.m4a')

    output_files_map: Dict[str, str] = {}

    for root, _, files in os.walk(output_dir):
        relative_dir = os.path.relpath(root, output_dir)

        for filename in files:
            if filename.lower().endswith(AUDIO_EXTS) and not filename.startswith('.'):
                stem = os.path.splitext(filename)[0]
                map_key = os.path.join(relative_dir, stem)
                output_files_map[map_key] = os.path.join(relative_dir, filename)

    input_files_list: List[Tuple[str, str]] = []

    for root, _, files in os.walk(input_dir):
        relative_dir = os.path.relpath(root, input_dir)

        for filename in files:
            if filename.lower().endswith(AUDIO_EXTS) and not filename.startswith('.'):
                stem = os.path.splitext(filename)[0]
                map_key = os.path.join(relative_dir, stem)
                input_files_list.append((map_key, os.path.join(relative_dir, filename)))

    results = []

    for map_key, input_relative_path in sorted(input_files_list):

        input_full_path = os.path.join(input_dir, input_relative_path)
        input_filename_only = os.path.basename(input_relative_path)

        if map_key in output_files_map:
            output_relative_path = output_files_map[map_key]
            output_full_path = os.path.join(output_dir, output_relative_path)
            output_filename_only = os.path.basename(output_relative_path)

            mse, psnr = calculate_audio_metrics(input_full_path, output_full_path)

            results.append({
                'Original Path': input_relative_path,
                'Compressed File': output_filename_only,
                'MSE': f"{mse:.8f}" if mse is not None else 'Error',
                'PSNR (dB)': f"{psnr:.2f}" if psnr is not None else 'Error',
                'Status': 'OK' if mse is not None else 'Error'
            })

        else:
            results.append({
                'Original Path': input_relative_path,
                'Compressed File': 'N/A',
                'MSE': 'N/A', 'PSNR (dB)': 'N/A',
                'Status': 'Missing Corresponding File in Output'
            })

    if not results:
        print(f"\nNo matching audio files found between '{input_dir}' and '{output_dir}' (including subfolders).")
        return

    print("\n--- Audio Quality Comparison Results (MSE/PSNR) ---")
    print(f"Checking directories recursively: {input_dir} vs {output_dir}")

    PATH_WIDTH = 50
    COMP_FN_WIDTH = 25
    MSE_WIDTH = 15
    PSNR_WIDTH = 12
    TOTAL_WIDTH = PATH_WIDTH + COMP_FN_WIDTH + MSE_WIDTH + PSNR_WIDTH + 3

    header = (
        f"{'Original Path':<{PATH_WIDTH}} "
        f"{'Compressed File':<{COMP_FN_WIDTH}} "
        f"{'MSE':>{MSE_WIDTH}} "
        f"{'PSNR (dB)':>{PSNR_WIDTH}}"
    )
    print(header)
    print("-" * TOTAL_WIDTH)

    for r in results:
        display_path = r['Original Path']
        if len(display_path) >= PATH_WIDTH:
            display_path = "..." + display_path[-(PATH_WIDTH - 3):]

        line = (
            f"{display_path:<{PATH_WIDTH}} "
            f"{r['Compressed File'][:COMP_FN_WIDTH - 1]:<{COMP_FN_WIDTH}} "
            f"{r['MSE']:>{MSE_WIDTH}} "
            f"{r['PSNR (dB)']:>{PSNR_WIDTH}}"
        )
        print(line)
        if r['Status'] != 'OK':
            print(f"   -> Status: {r['Status']}")

# --- Test ---
# INPUT_DIR = 'input/audio/A-3'
# OUTPUT_DIR = 'output/audio/FLAC/A-3'
# compare_folders_recursive(INPUT_DIR, OUTPUT_DIR)