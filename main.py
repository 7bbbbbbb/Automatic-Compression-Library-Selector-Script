import compressor_zlib
import compressor_bz2
import compressor_lz4
import compressor_mozjpeg
import compressor_oxipng
import compressor_pydub_mp3
import compressor_pydub_flac
import compressor_ffmpeg
import comparator_image
import comparator_audio
import comparator_video
import compressor_zip

# Compression Parameters
INPUT_FOLDER = "input_test"
OUTPUT_FOLDER = "output_processed"
COMPRESSION_LEVEL = 3 # Range 1(Min Size Reduction) - 3(Max Size Reduction)
SPEED_LEVEL = 1 # Range 1(Slower) - 3(Faster)
AVOID_DATA_LOSS = False # Prefer libraries with the least amount of data loss
# Extras
DO_CHECK_FIDELITY = True # Compare files to get a fidelity estimate
ZIP_RESULT = True # Turn the result into a zip file

if __name__ == "__main__":
    print("=" * 70)
    print("\n" + "--- AUTOMATIC DATA COMPRESSION TOOL ---")
    print("\n" + "=" * 70)
    compressor_zip.delete_directory_contents(OUTPUT_FOLDER)
    if AVOID_DATA_LOSS:
        compressor_mozjpeg.optimize_folder_batch(INPUT_FOLDER, OUTPUT_FOLDER, 100)
        compressor_oxipng.optimize_folder_with_oxipng(INPUT_FOLDER, OUTPUT_FOLDER, 6, png_only=True)
        compressor_pydub_flac.compress_folder_to_flac(INPUT_FOLDER, OUTPUT_FOLDER, 8)
        compressor_ffmpeg.process_video_folder(INPUT_FOLDER, OUTPUT_FOLDER, "av1", 30)
    if SPEED_LEVEL == 1:
        if COMPRESSION_LEVEL == 1:
            compressor_lz4.compress_folder_streaming(INPUT_FOLDER, OUTPUT_FOLDER)
            if not AVOID_DATA_LOSS:
                compressor_mozjpeg.optimize_folder_batch(INPUT_FOLDER, OUTPUT_FOLDER, 100)
                compressor_oxipng.optimize_folder_with_oxipng(INPUT_FOLDER, OUTPUT_FOLDER, 6, png_only=True)
                compressor_pydub_flac.compress_folder_to_flac(INPUT_FOLDER, OUTPUT_FOLDER, 8)
                compressor_ffmpeg.process_video_folder(INPUT_FOLDER, OUTPUT_FOLDER, "av1", 30)
        elif COMPRESSION_LEVEL == 2:
            compressor_zlib.compress_folder_streaming(INPUT_FOLDER, OUTPUT_FOLDER)
            if not AVOID_DATA_LOSS:
                compressor_mozjpeg.optimize_folder_batch(INPUT_FOLDER, OUTPUT_FOLDER, 90)
                compressor_pydub_mp3.compress_folder_to_mp3(INPUT_FOLDER, OUTPUT_FOLDER, "320k")
                compressor_ffmpeg.process_video_folder(INPUT_FOLDER, OUTPUT_FOLDER, "h264", 30)
        elif COMPRESSION_LEVEL == 3:
            compressor_bz2.compress_folder_streaming(INPUT_FOLDER, OUTPUT_FOLDER)
            if not AVOID_DATA_LOSS:
                compressor_mozjpeg.optimize_folder_batch(INPUT_FOLDER, OUTPUT_FOLDER, 80)
                compressor_pydub_mp3.compress_folder_to_mp3(INPUT_FOLDER, OUTPUT_FOLDER, "192k")
                compressor_ffmpeg.process_video_folder(INPUT_FOLDER, OUTPUT_FOLDER, "hevc", 30)
    elif SPEED_LEVEL == 2:
        if COMPRESSION_LEVEL == 1:
            compressor_lz4.compress_folder_streaming(INPUT_FOLDER, OUTPUT_FOLDER)
            if not AVOID_DATA_LOSS:
                compressor_mozjpeg.optimize_folder_batch(INPUT_FOLDER, OUTPUT_FOLDER, 90)
                compressor_pydub_flac.compress_folder_to_flac(INPUT_FOLDER, OUTPUT_FOLDER, 4)
                compressor_ffmpeg.process_video_folder(INPUT_FOLDER, OUTPUT_FOLDER, "h264", 30)
        elif COMPRESSION_LEVEL == 2:
            compressor_zlib.compress_folder_streaming(INPUT_FOLDER, OUTPUT_FOLDER)
            if not AVOID_DATA_LOSS:
                compressor_mozjpeg.optimize_folder_batch(INPUT_FOLDER, OUTPUT_FOLDER, 80)
                compressor_pydub_flac.compress_folder_to_flac(INPUT_FOLDER, OUTPUT_FOLDER, 6)
                compressor_ffmpeg.process_video_folder(INPUT_FOLDER, OUTPUT_FOLDER, "h264", 30)
        elif COMPRESSION_LEVEL == 3:
            compressor_zlib.compress_folder_streaming(INPUT_FOLDER, OUTPUT_FOLDER)
            if not AVOID_DATA_LOSS:
                compressor_mozjpeg.optimize_folder_batch(INPUT_FOLDER, OUTPUT_FOLDER, 70)
                compressor_pydub_mp3.compress_folder_to_mp3(INPUT_FOLDER, OUTPUT_FOLDER, "320k")
                compressor_ffmpeg.process_video_folder(INPUT_FOLDER, OUTPUT_FOLDER, "hevc", 30)
    elif SPEED_LEVEL == 3:
        if COMPRESSION_LEVEL == 1:
            compressor_lz4.compress_folder_streaming(INPUT_FOLDER, OUTPUT_FOLDER)
            if not AVOID_DATA_LOSS:
                compressor_mozjpeg.optimize_folder_batch(INPUT_FOLDER, OUTPUT_FOLDER, 80)
                compressor_pydub_flac.compress_folder_to_flac(INPUT_FOLDER, OUTPUT_FOLDER, 1)
                compressor_ffmpeg.process_video_folder(INPUT_FOLDER, OUTPUT_FOLDER, "h264", 30)
        elif COMPRESSION_LEVEL == 2:
            compressor_lz4.compress_folder_streaming(INPUT_FOLDER, OUTPUT_FOLDER)
            if not AVOID_DATA_LOSS:
                compressor_mozjpeg.optimize_folder_batch(INPUT_FOLDER, OUTPUT_FOLDER, 70)
                compressor_pydub_flac.compress_folder_to_flac(INPUT_FOLDER, OUTPUT_FOLDER, 2)
                compressor_ffmpeg.process_video_folder(INPUT_FOLDER, OUTPUT_FOLDER, "h264", 30)
        elif COMPRESSION_LEVEL == 3:
            compressor_zlib.compress_folder_streaming(INPUT_FOLDER, OUTPUT_FOLDER)
            if not AVOID_DATA_LOSS:
                compressor_mozjpeg.optimize_folder_batch(INPUT_FOLDER, OUTPUT_FOLDER, 60)
                compressor_pydub_flac.compress_folder_to_flac(INPUT_FOLDER, OUTPUT_FOLDER, 3)
                compressor_ffmpeg.process_video_folder(INPUT_FOLDER, OUTPUT_FOLDER, "h264", 30)

    if DO_CHECK_FIDELITY:
        comparator_image.compare_folders(INPUT_FOLDER, OUTPUT_FOLDER, "_optimized")
        comparator_audio.compare_folders_recursive(INPUT_FOLDER, OUTPUT_FOLDER)
        comparator_video.batch_compare_videos(INPUT_FOLDER, OUTPUT_FOLDER)
    if ZIP_RESULT:
        compressor_zip.compress_directory_to_zip(OUTPUT_FOLDER, "compressed_files.zip")
        print("\n" + "=" * 70)
        print("\n--- FOLDER COMPRESSION COMPLETED ---")
        print("\nCompressed .zip file is located in the root folder.")
        compressor_zip.compare_file_system_sizes(INPUT_FOLDER, "compressed_files.zip")
    else:
        print("\n" + "=" * 70)
        print("\n--- FOLDER COMPRESSION COMPLETED ---")
        print(f"\nCompressed files are located in the {OUTPUT_FOLDER} folder.")
        compressor_zip.compare_file_system_sizes(INPUT_FOLDER, OUTPUT_FOLDER)