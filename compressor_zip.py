import zipfile
import os
import time
import shutil


def _get_dir_size(start_path: str) -> int:
    total_size = 0
    if not os.path.isdir(start_path):
        return 0

    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                try:
                    total_size += os.path.getsize(fp)
                except OSError:
                    pass
    return total_size


def _get_size_and_type(path: str) -> tuple[int, str]:
    if not os.path.exists(path):
        return 0, "Missing"

    if os.path.isdir(path):
        size = _get_dir_size(path)
        return size, "Folder"

    if os.path.isfile(path):
        size = os.path.getsize(path)
        file_ext = os.path.splitext(path)[1].lower()
        if file_ext == '.zip':
            return size, "ZIP File"
        else:
            return size, "File"

    return 0, "Other"


def compare_file_system_sizes(path1: str, path2: str):
    print("=" * 60)
    print(f"Comparing Sizes:\n1. '{path1}'\n2. '{path2}'")
    print("=" * 60)

    size1_bytes, type1 = _get_size_and_type(path1)
    size1_mb = size1_bytes / (1024 * 1024)

    size2_bytes, type2 = _get_size_and_type(path2)
    size2_mb = size2_bytes / (1024 * 1024)

    print("\n--- Size Details ---")
    print(f"Path 1 ({type1}): {path1}")
    print(f"Total Size: {size1_mb:.2f} MB ({size1_bytes} bytes)")

    print(f"\nPath 2 ({type2}): {path2}")
    print(f"Total Size: {size2_mb:.2f} MB ({size2_bytes} bytes)")

    if type1 == "Missing" or type2 == "Missing":
        print("\nERROR: One or both paths were not found. Comparison aborted.")
        print("=" * 60 + "\n")
        return

    if size1_bytes == 0 and size2_bytes == 0:
        print("\nINFO: Both paths exist but contain zero measurable data.")
        print("=" * 60 + "\n")
        return

    print("\n--- FOLDER COMPRESSION RESULTS ---")
    size_diff_bytes = abs(size1_bytes - size2_bytes)
    size_ratio = (size_diff_bytes / size1_bytes) * 100

    print(f"Original Input Size: {size1_bytes / (1024 * 1024):.2f} MB")
    print(f"Compressed Output Size: {size2_bytes / (1024 * 1024):.2f} MB")
    print(f"Overall Total Space Saved: **{size_ratio:.2f}%**")

    print("=" * 60 + "\n")


def delete_directory_contents(target_dir: str):
    if os.path.isdir(target_dir):
        try:
            shutil.rmtree(target_dir)
            print(f"\nSUCCESS: Source directory deleted: '{target_dir}'")
        except OSError as e:
            print(f"\nERROR: Could not delete directory '{target_dir}'. Details: {e}")


def compress_directory_to_zip(source_dir: str, output_zip_path: str):
    if not os.path.isdir(source_dir):
        print(f"Error: Source directory not found at '{source_dir}'")
        return

    start_time = time.time()
    total_files = 0
    compression_successful = False

    print(f"Starting compression of '{source_dir}' to '{output_zip_path}'...")

    try:
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            source_parent = os.path.abspath(os.path.join(source_dir, os.pardir))

            for root, dirs, files in os.walk(source_dir):
                archive_base = os.path.relpath(root, source_parent)

                for file in files:
                    file_path = os.path.join(root, file)
                    archive_name = os.path.join(archive_base, file)

                    zipf.write(file_path, archive_name)
                    total_files += 1

        end_time = time.time()
        duration = end_time - start_time

        zip_size_bytes = os.path.getsize(output_zip_path)
        zip_size_kb = zip_size_bytes / 1024
        compression_successful = True

        print("\n--- ZIP Compression Report ---")
        print(f"Compression successful: {output_zip_path}")
        print(f"Source Directory: {source_dir}")
        print(f"Files Compressed: {total_files}")
        print(f"Output Size: {zip_size_kb:.2f} KB")
        print(f"Time Taken: {duration:.2f} seconds")

    except Exception as e:
        print(f"An unexpected error occurred during zipping: {e}")
        print("Source directory retained.")
        return

    if compression_successful:
        print("\n--- Attempting Source Deletion ---")
        delete_directory_contents(source_dir)

# --- Test ---
# SOURCE_FOLDER = "./input/test_files_to_delete"
# OUTPUT_ZIP_FILE = "my_compressed_archive.zip"

# compress_directory_to_zip(SOURCE_FOLDER, OUTPUT_ZIP_FILE)
# compare_file_system_sizes(SOURCE_FOLDER, OUTPUT_ZIP_FILE)