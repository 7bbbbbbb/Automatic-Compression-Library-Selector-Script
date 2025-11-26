# pip install pillow
from PIL import Image
import os

input_jpg = "image.jpg"
output_jpg = "compressed_image.jpg"

try:
    img = Image.open(input_jpg)

    # Compress the JPEG file to a quality of 80 (Good balance)
    img.save(output_jpg, quality=80, optimize=True)

    print(f"Compressed {input_jpg} to {output_jpg} with quality 80.")

except FileNotFoundError:
    print(f"Error: Input file '{input_jpg}' not found.")


input_png = "image.png"
output_png = "quantized_image.png"

img = Image.open(input_png)

# Convert the image to a palletized (P) mode with a maximum of 256 colors.
# This reduces the number of bits needed to store each pixel's color.
img_quantized = img.quantize(colors=256)

# Save the reduced image
img_quantized.save(output_png, optimize=True, compress_level=9)


input_file = "my_original_image.png"
output_file = "my_converted_image.jpg"  # Or .jpeg

# --- Example Setup: Create a dummy PNG file if it doesn't exist ---
# (You can skip this block if your input_file already exists)
try:
    if not os.path.exists(input_file):
        # Creates a simple red 100x100 pixel image and saves it as PNG
        img = Image.new('RGB', (100, 100), color='red')
        img.save(input_file, 'PNG')
        print(f"Created dummy file: {input_file}")
except Exception as e:
    print(f"Could not create dummy file. Ensure Pillow is installed: {e}")
# -------------------------------------------------------------------


# --- Conversion Process ---
try:
    # 1. Open/Decode the PNG image
    img = Image.open(input_file)

    # 2. Convert to RGB (Crucial Step!)
    # JPEG does not support the transparent alpha channel (RGBA) used by PNG.
    # We must convert the image to the standard three-channel RGB mode before saving as JPEG.
    if img.mode == 'RGBA':
        # Create a white background
        background = Image.new('RGB', img.size, (255, 255, 255))
        # Paste the image on the background. Alpha is automatically handled.
        background.paste(img, mask=img.split()[3])
        img = background

    # 3. Save/Encode the image in JPEG format
    # Pillow infers the output format from the .jpg extension.
    # The 'quality' parameter (0-95) controls compression (optional)
    img.save(output_file, 'JPEG', quality=90)

    print(f"\nSuccessfully converted {input_file} to {output_file}.")
    print(f"Original size: {os.path.getsize(input_file)} bytes")
    print(f"Converted size: {os.path.getsize(output_file)} bytes (Lossy compression)")

except FileNotFoundError:
    print(f"\nError: Input file '{input_file}' not found.")
except Exception as e:
    print(f"\nAn error occurred during conversion: {e}")
