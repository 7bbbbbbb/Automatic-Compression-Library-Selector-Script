import zlib
import os
import time

TEXT_EXTENSIONS = (
    '.txt', '.csv', '.md', '.log', '.json', '.xml', '.py', '.html',
    '.css', '.js', '.ts', '.jsx', '.yaml', '.yml', '.cpp', '.json5', '.toml'
)
COMPRESSED_EXTENSION = ".zlib"


def _stream_compress_file(input_path, output_path, compressor, chunk_size=65536):
    try:
        with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            while True:
                chunk = f_in.read(chunk_size)

                if not chunk:
                    break

                compressed_chunk = compressor.compress(chunk)
                f_out.write(compressed_chunk)

            remaining_data = compressor.flush()
            f_out.write(remaining_data)

        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)
        return original_size, compressed_size

    except Exception as e:
        print(f"Error compressing {input_path}: {e}")
        return 0, 0


def _stream_decompress_file(input_path, output_path, decompressor, chunk_size=65536):
    try:
        with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            while True:
                chunk = f_in.read(chunk_size)

                if not chunk:
                    break

                decompressed_chunk = decompressor.decompress(chunk)
                f_out.write(decompressed_chunk)

            remaining_data = decompressor.flush()
            f_out.write(remaining_data)

        compressed_size = os.path.getsize(input_path)
        restored_size = os.path.getsize(output_path)
        return compressed_size, restored_size

    except Exception as e:
        print(f"Error decompressing {input_path}: {e}")
        return 0, 0


def compress_folder_streaming(input_dir, output_dir, level=zlib.Z_BEST_COMPRESSION, chunk_size=65536):
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory not found at {input_dir}")
        return

    total_original_size = 0
    total_compressed_size = 0
    total_files_processed = 0
    total_files_skipped = 0

    start_time = time.time()

    print("-" * 75)
    print(f"Starting Zlib TEXT Compression of Folder: {input_dir}")
    print(f"Output Directory: {output_dir}")
    print("-" * 75)
    print("File Path                             | Original Size | Compressed Size | Ratio")
    print("-" * 75)

    for root, _, files in os.walk(input_dir):
        relative_dir = os.path.relpath(root, input_dir)

        target_dir = os.path.join(output_dir, relative_dir)
        os.makedirs(target_dir, exist_ok=True)

        for filename in files:
            _, ext = os.path.splitext(filename)
            if ext.lower() not in TEXT_EXTENSIONS:
                total_files_skipped += 1
                continue

            input_path = os.path.join(root, filename)

            output_filename = filename + COMPRESSED_EXTENSION
            output_path = os.path.join(target_dir, output_filename)

            compressor = zlib.compressobj(level=level)

            original_size, compressed_size = _stream_compress_file(
                input_path,
                output_path,
                compressor,
                chunk_size
            )

            if original_size > 0:
                total_original_size += original_size
                total_compressed_size += compressed_size
                total_files_processed += 1

                compression_ratio = 1.0
                if compressed_size > 0:
                    compression_ratio = original_size / compressed_size

                file_info = os.path.join(relative_dir, filename)

                print(f"{file_info:40.40} | {original_size:13,} B | {compressed_size:15,} B | {compression_ratio:5.2f}:1")

    end_time = time.time()
    duration = end_time - start_time

    if total_files_processed == 0:
        print("No eligible text files found to compress.")
        return

    total_size_mb = total_original_size / (1024 * 1024)
    speed_mbps = total_size_mb / duration if duration > 0 else float('inf')

    savings = total_original_size - total_compressed_size
    savings_percent_total = (savings / total_original_size) * 100

    print("\n" + "=" * 75)
    print("           FOLDER COMPRESSION COMPLETE")
    print("=" * 75)
    print(f"Total Files Processed: {total_files_processed} | Skipped: {total_files_skipped}")
    print(f"Total Time Taken: {duration:.4f} seconds")
    print("-" * 75)
    print(f"Original Total Size: {total_original_size:,} bytes ({total_size_mb:.2f} MB)")
    print(f"Compressed Total Size: {total_compressed_size:,} bytes")
    print(f"Total Reduction: **{savings_percent_total:.2f}%** ({savings / (1024 * 1024):.2f} MB)")
    print(f"Average Speed: **{speed_mbps:.2f} MB/s**")
    print("=" * 75 + "\n")


def decompress_folder_streaming(input_dir, output_dir, chunk_size=65536):
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory not found at {input_dir}")
        return

    total_compressed_size = 0
    total_restored_size = 0
    total_files = 0
    start_time = time.time()

    print("-" * 60)
    print(f"Starting Zlib Decompression of Folder: {input_dir}")
    print(f"Output Directory: {output_dir}")
    print("-" * 60)

    for root, _, files in os.walk(input_dir):
        relative_dir = os.path.relpath(root, input_dir)

        target_dir = os.path.join(output_dir, relative_dir)
        os.makedirs(target_dir, exist_ok=True)

        for filename in files:
            if not filename.endswith(COMPRESSED_EXTENSION):
                continue

            input_path = os.path.join(root, filename)

            restored_filename = filename[:-len(COMPRESSED_EXTENSION)]
            output_path = os.path.join(target_dir, restored_filename)

            print(f"  [DECOMPRESS]: {os.path.join(relative_dir, filename)}...")

            decompressor = zlib.decompressobj()

            compressed_size, restored_size = _stream_decompress_file(
                input_path,
                output_path,
                decompressor,
                chunk_size
            )

            if restored_size > 0:
                total_compressed_size += compressed_size
                total_restored_size += restored_size
                total_files += 1

    end_time = time.time()
    duration = end_time - start_time

    if total_files == 0:
        print("No .zlib files found to decompress.")
        return

    total_size_mb = total_restored_size / (1024 * 1024)
    speed_mbps = total_size_mb / duration if duration > 0 else float('inf')

    print("\n" + "=" * 60)
    print("        FOLDER DECOMPRESSION COMPLETE")
    print("=" * 60)
    print(f"Total Files Processed: {total_files}")
    print(f"Total Time Taken: {duration:.4f} seconds")
    print("-" * 60)
    print(f"Input Total Size (Compressed): {total_compressed_size:,} bytes")
    print(f"Output Total Size (Restored): {total_restored_size:,} bytes ({total_size_mb:.2f} MB)")
    print(f"Average Decompression Speed: **{speed_mbps:.2f} MB/s**")
    print("=" * 60 + "\n")


# --- Test ---
#INPUT_DIR = "input/text/T-1"
#OUTPUT_COMPRESSED_DIR = "output/text/ZLIB/T-1"
#OUTPUT_RESTORED_DIR = "restored"

# compress_folder_streaming(INPUT_DIR, OUTPUT_COMPRESSED_DIR)
# decompress_folder_streaming(OUTPUT_COMPRESSED_DIR, OUTPUT_RESTORED_DIR)