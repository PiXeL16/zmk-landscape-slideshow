#!/usr/bin/env python3
"""
ZMK Landscape Art Gallery Generator

This script processes images from the /art folder and generates the corresponding
C code for integration into the ZMK nice!view display system.

Features:
- Automatically resizes images to 140x68 pixels (nice!view display size)
- Converts images to 1-bit black and white format
- Generates LVGL-compatible C arrays and descriptors
- Updates peripheral_status.c with proper image declarations
- Maintains proper naming conventions (landscape1, landscape2, etc.)

Usage:
    python generate_art.py

Requirements:
    - PIL (Pillow) for image processing
    - Images should be placed in ./art/ folder
    - Supported formats: PNG, JPG, JPEG, BMP, GIF

Author: Auto-generated for ZMK Landscape Slideshow
"""

import os
import sys
from PIL import Image, ImageOps
import re
from pathlib import Path
import shutil
import numpy as np
from scipy import ndimage

# Constants
DISPLAY_WIDTH = 68
DISPLAY_HEIGHT = 140
ART_FOLDER = "./art"
OUTPUT_FILE = "./boards/shields/nice_view_custom/widgets/art.c"
PERIPHERAL_STATUS_FILE = "./boards/shields/nice_view_custom/widgets/peripheral_status.c"

# Supported image formats
SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}

def calculate_aspect_ratio_size(orig_size, target_size):
    """
    Calculate the best fit size that maintains aspect ratio within target bounds.
    Only applies padding when aspect ratios don't match.
    
    Args:
        orig_size: (width, height) of original image
        target_size: (width, height) of target display
    
    Returns:
        (new_width, new_height, pad_left, pad_top, needs_padding) - size, padding, and whether padding is needed
    """
    orig_width, orig_height = orig_size
    target_width, target_height = target_size
    
    # Calculate aspect ratios
    orig_aspect = orig_width / orig_height
    target_aspect = target_width / target_height
    
    # Check if aspect ratios are close enough (within 1% tolerance)
    aspect_diff = abs(orig_aspect - target_aspect) / target_aspect
    needs_padding = aspect_diff > 0.01
    # Removed debug output
    
    # Calculate scaling factors for both dimensions
    scale_x = target_width / orig_width
    scale_y = target_height / orig_height
    
    # Use the smaller scale to ensure image fits within bounds
    scale = min(scale_x, scale_y)
    
    # Calculate new dimensions maintaining aspect ratio
    new_width = int(orig_width * scale)
    new_height = int(orig_height * scale)
    
    if needs_padding:
        # Calculate padding to position image at bottom of frame (only when needed)
        pad_left = (target_width - new_width) // 2  # Center horizontally
        pad_top = target_height - new_height  # All padding at top (bottom-align)
    else:
        # No padding needed - aspect ratios match closely
        pad_left = pad_top = 0
    
    return new_width, new_height, pad_left, pad_top, needs_padding

def resize_with_1bit_optimization(img, target_size, method="content_aware", maintain_aspect_ratio=True):
    """
    Advanced 1-bit optimized scaling algorithms with optional aspect ratio preservation.
    """
    from PIL import ImageFilter, ImageEnhance, Image
    import numpy as np
    
    target_width, target_height = target_size
    orig_width, orig_height = img.size
    
    if maintain_aspect_ratio:
        # Calculate aspect-ratio preserving dimensions
        new_width, new_height, pad_left, pad_top, needs_padding = calculate_aspect_ratio_size(img.size, target_size)
        if needs_padding:
            print(f"    Aspect ratio preserved: {orig_width}x{orig_height} -> {new_width}x{new_height} (padding: left={pad_left}, top={pad_top} - bottom-aligned)")
        else:
            print(f"    Aspect ratios match: {orig_width}x{orig_height} -> {new_width}x{new_height} (no padding needed)")
        actual_target = (new_width, new_height)
    else:
        actual_target = target_size
        new_width, new_height = target_width, target_height
        pad_left = pad_top = 0
        needs_padding = False
    
    # Remove the duplicate method handling sections with return statements
    # These prevent the padding logic from executing
    
    # Handle adaptive method by analyzing and selecting the best approach
    if method == "adaptive":
        print(f"    Using adaptive scaling (analyzing image characteristics)...")
        
        scale_factor = max(orig_width / actual_target[0], orig_height / actual_target[1])
        
        # Analyze image characteristics
        img_array = np.array(img)
        edge_density = len(np.where(np.abs(np.diff(img_array, axis=0)) > 20)[0]) / img_array.size
        
        if edge_density > 0.1:  # High edge density - use edge preserving
            print(f"      High edge density ({edge_density:.2f}) - using edge-preserving method")
            method = "edge_preserving"
        elif scale_factor > 10:  # Very high reduction - use content aware
            print(f"      High reduction ({scale_factor:.1f}x) - using content-aware method")
            method = "content_aware"
        else:  # Default to area sampling for photographic content
            print(f"      Standard content - using area sampling")
            method = "area_sampling"
    
    # Now execute the selected method
    if method == "edge_preserving":
        # Method 1: Edge-preserving scaling
        print(f"    Using edge-preserving scaling...")
        
        # Detect edges first
        edges = img.filter(ImageFilter.FIND_EDGES)
        
        # Scale original and edges separately
        img_scaled = img.resize(actual_target, Image.Resampling.LANCZOS)
        edges_scaled = edges.resize(actual_target, Image.Resampling.NEAREST)  # Preserve sharp edges
        
        # Combine: use edge info to enhance scaled image
        # Convert to arrays for pixel-wise operations
        img_array = np.array(img_scaled)
        edges_array = np.array(edges_scaled)
        
        # Enhance pixels where edges are detected
        enhanced = img_array.astype(np.float32)
        edge_mask = edges_array > 30  # Threshold for edge detection
        enhanced[edge_mask] = enhanced[edge_mask] * 1.2  # Boost edge pixels
        enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
        
        img = Image.fromarray(enhanced, 'L')
        
    elif method == "content_aware":
        # Method 2: Content-aware scaling with multiple passes
        print(f"    Using content-aware scaling...")
        
        # Calculate reduction factor
        scale_factor = max(orig_width / actual_target[0], orig_height / actual_target[1])
        
        if scale_factor > 8:
            # Very high reduction - use 3-stage scaling
            stage1_w, stage1_h = int(orig_width // 3), int(orig_height // 3)
            stage2_w, stage2_h = int(actual_target[0] * 1.5), int(actual_target[1] * 1.5)
            
            img = img.resize((stage1_w, stage1_h), Image.Resampling.LANCZOS)
            img = img.resize((stage2_w, stage2_h), Image.Resampling.BICUBIC)
            img = img.resize(actual_target, Image.Resampling.LANCZOS)
        elif scale_factor > 4:
            # Medium reduction - use 2-stage scaling  
            intermediate_w, intermediate_h = actual_target[0] * 2, actual_target[1] * 2
            img = img.resize((intermediate_w, intermediate_h), Image.Resampling.LANCZOS)
            img = img.resize(actual_target, Image.Resampling.BICUBIC)
        else:
            # Small reduction - single stage with best quality
            img = img.resize(actual_target, Image.Resampling.LANCZOS)
    
    elif method == "area_sampling":
        # Method 3: Area-based sampling for better detail preservation
        print(f"    Using area-based sampling...")
        
        # Use box filter (area sampling) which averages pixels in regions
        # This preserves more detail than interpolation for large reductions
        img = img.resize(actual_target, Image.Resampling.BOX)
    
    # Apply padding if maintaining aspect ratio AND aspect ratios don't match
    if maintain_aspect_ratio and needs_padding and (pad_left > 0 or pad_top > 0):
        print(f"    Adding padding to bottom-align image: left={pad_left}, top={pad_top}")
        # Create new image with target size and black background
        padded_img = Image.new('L', target_size, 0)  # Black background
        # Paste the resized image at the bottom (with top padding)
        padded_img.paste(img, (pad_left, pad_top))
        return padded_img
        
    return img

def apply_1bit_optimized_preprocessing(img):
    """
    Apply preprocessing specifically optimized for 1-bit conversion.
    """
    from PIL import ImageEnhance, ImageFilter
    import numpy as np
    
    # Convert to numpy for advanced operations
    img_array = np.array(img).astype(np.float32)
    
    # 1. Local contrast enhancement (CLAHE-like effect)
    print(f"      Applying local contrast enhancement...")
    # Simple local contrast: enhance based on local mean
    from scipy import ndimage
    local_mean = ndimage.uniform_filter(img_array, size=5)
    img_array = img_array + 0.3 * (img_array - local_mean)
    img_array = np.clip(img_array, 0, 255)
    
    # Convert back to PIL
    img = Image.fromarray(img_array.astype(np.uint8), 'L')
    
    # 2. Structure-preserving sharpening
    print(f"      Applying structure-preserving sharpening...")
    img = img.filter(ImageFilter.UnsharpMask(radius=0.8, percent=150, threshold=3))
    
    # 3. Adaptive contrast enhancement
    print(f"      Optimizing contrast for 1-bit conversion...")
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.4)  # Higher contrast for better 1-bit separation
    
    return img

def convert_to_1bit_advanced(img, method="error_diffusion"):
    """
    Advanced 1-bit conversion with multiple dithering options.
    """
    print(f"      Converting to 1-bit using {method} dithering...")
    
    if method == "error_diffusion":
        # Custom error diffusion (Atkinson-like)
        import numpy as np
        
        img_array = np.array(img).astype(np.float32)
        height, width = img_array.shape
        
        for y in range(height):
            for x in range(width):
                old_pixel = img_array[y, x]
                new_pixel = 255 if old_pixel > 128 else 0
                img_array[y, x] = new_pixel
                
                error = old_pixel - new_pixel
                
                # Distribute error (Atkinson dithering pattern)
                if x + 1 < width: img_array[y, x + 1] += error * 1/8
                if x + 2 < width: img_array[y, x + 2] += error * 1/8
                if y + 1 < height:
                    if x - 1 >= 0: img_array[y + 1, x - 1] += error * 1/8
                    if x < width: img_array[y + 1, x] += error * 1/8
                    if x + 1 < width: img_array[y + 1, x + 1] += error * 1/8
                if y + 2 < height and x < width: img_array[y + 2, x] += error * 1/8
        
        return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8), 'L').convert('1')
    
    elif method == "floyd_steinberg":
        try:
            return img.convert('1', dither=Image.FLOYDSTEINBERG)
        except AttributeError:
            try:
                return img.convert('1', dither=Image.Dither.FLOYD_STEINBERG) 
            except AttributeError:
                return img.convert('1', dither=0)
    
    elif method == "threshold_adaptive":
        # Adaptive threshold based on local statistics
        import numpy as np
        from scipy import ndimage
        
        img_array = np.array(img).astype(np.float32)
        
        # Calculate local threshold using local mean
        local_threshold = ndimage.uniform_filter(img_array, size=11)
        
        # Apply threshold with slight bias
        result = (img_array > local_threshold - 5).astype(np.uint8) * 255
        
        return Image.fromarray(result, 'L').convert('1')
    
    elif method == "threshold_adaptive":
        # Adaptive threshold based on local statistics
        import numpy as np
        from scipy import ndimage
        
        img_array = np.array(img).astype(np.float32)
        
        # Calculate local threshold using local mean
        local_threshold = ndimage.uniform_filter(img_array, size=11)
        
        # Apply threshold with slight bias
        result = (img_array > local_threshold - 5).astype(np.uint8) * 255
        
        return Image.fromarray(result, 'L').convert('1')
    
    else:  # fallback
        return img.convert('1')

def resize_and_convert_image(image_path, save_preview=False, scaling_method="content_aware", dither_method="error_diffusion", maintain_aspect_ratio=True):
    """
    Advanced 1-bit optimized image processing with multiple scaling and dithering options.
    
    Args:
        image_path: Path to the input image
        save_preview: If True, save the processed image as a preview
        scaling_method: "content_aware", "edge_preserving", "adaptive", "area_sampling" (default: content_aware)
        dither_method: "error_diffusion", "floyd_steinberg", "threshold_adaptive" (default: error_diffusion)
        maintain_aspect_ratio: If True, preserve original aspect ratio (default: True)
    
    Returns:
        PIL Image object in 1-bit mode, or None if processing failed
    """
    try:
        with Image.open(image_path) as img:
            print(f"    Original size: {img.size}")
            
            # Convert to grayscale first
            img = img.convert('L')
            
            # Step 1: Advanced 1-bit optimized scaling
            target_size = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
            orig_aspect = img.size[0] / img.size[1]
            target_aspect = DISPLAY_WIDTH / DISPLAY_HEIGHT
            print(f"    Aspect ratios - Original: {orig_aspect:.2f}, Target: {target_aspect:.2f}")
            
            img = resize_with_1bit_optimization(img, target_size, method=scaling_method, maintain_aspect_ratio=maintain_aspect_ratio)
            
            # Step 2: 1-bit optimized preprocessing
            img = apply_1bit_optimized_preprocessing(img)
            
            # Step 3: Advanced 1-bit conversion
            img_1bit = convert_to_1bit_advanced(img, method=dither_method)
            
            print(f"    Processing complete: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT} 1-bit")
            
            # Save preview if requested
            if save_preview:
                preview_path = image_path.parent / f"preview_{image_path.stem}.png"
                img_1bit.save(preview_path)
                print(f"    Saved preview: {preview_path}")
            
            return img_1bit
            
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_processed_previews(image_files):
    """
    Save byte-accurate preview images showing exactly what the nice!view will display.
    Reconstructs from actual LVGL byte data for 100% accuracy.
    """
    preview_dir = Path(ART_FOLDER) / "previews"
    preview_dir.mkdir(exist_ok=True)
    
    print(f"Saving byte-accurate conversion previews to {preview_dir}/...")
    
    for i, img_file in enumerate(image_files, 1):
        print(f"  Creating byte-accurate preview for {img_file.name}...")
        
        # Process the image using optimal methods
        processed_img = resize_and_convert_image(img_file, save_preview=False, scaling_method="content_aware", dither_method="error_diffusion", maintain_aspect_ratio=True)
        if processed_img is None:
            continue
        
        # Convert to LVGL byte data (same as what goes to the device)
        try:
            img_data, data_size = image_to_lvgl_data(processed_img)
            print(f"    Generated {data_size} bytes of LVGL data")
            
            # Reconstruct image from actual byte data
            reconstructed_img = lvgl_data_to_image(img_data, DISPLAY_WIDTH, DISPLAY_HEIGHT)
            
            # Save preview with descriptive name
            preview_name = f"image{i}_preview_{img_file.stem}.png"
            preview_path = preview_dir / preview_name
            
            # Convert to RGB for better preview visibility (but data is byte-accurate)
            preview_img = reconstructed_img.convert('RGB')
            preview_img.save(preview_path)
            
            print(f"    Saved byte-accurate preview: {preview_name}")
            
        except Exception as e:
            print(f"    Error creating preview for {img_file.name}: {e}")
            continue
    
    print(f"All byte-accurate previews saved to {preview_dir}/")
    return preview_dir

def image_to_lvgl_data(img):
    """
    Convert PIL 1-bit image to LVGL 1-bit indexed format data.
    """
    if img.mode != '1':
        raise ValueError("Image must be in 1-bit mode")
    
    # Get image data as bytes
    width, height = img.size
    
    # LVGL 1-bit indexed format: 8 pixels per byte
    # Each row must be aligned to byte boundary
    bytes_per_row = (width + 7) // 8
    
    data = []
    pixels = list(img.getdata())
    
    for y in range(height):
        row_bytes = []
        for byte_x in range(bytes_per_row):
            byte_val = 0
            for bit in range(8):
                pixel_x = byte_x * 8 + bit
                if pixel_x < width:
                    pixel_idx = y * width + pixel_x
                    # In PIL 1-bit mode: 0 = black, 255 = white
                    # In our format: 0 = black (index 0), 1 = white (index 1)
                    if pixels[pixel_idx] == 255:  # White pixel
                        byte_val |= (1 << (7 - bit))
            row_bytes.append(byte_val)
        data.extend(row_bytes)
    
    return data, len(data)

def lvgl_data_to_image(data, width, height):
    """
    Convert LVGL byte data back to PIL image for accurate preview generation.
    This shows exactly what the nice!view display will render.
    """
    from PIL import Image
    
    bytes_per_row = (width + 7) // 8
    pixels = []
    
    for y in range(height):
        for x in range(width):
            byte_idx = y * bytes_per_row + (x // 8)
            bit_pos = 7 - (x % 8)
            
            if byte_idx < len(data):
                # Extract bit from byte
                pixel_value = (data[byte_idx] >> bit_pos) & 1
                # Convert to PIL format: 1 = white (255), 0 = black (0)
                pixels.append(255 if pixel_value else 0)
            else:
                pixels.append(0)  # Default to black
    
    # Create new PIL image from reconstructed pixels
    img = Image.new('L', (width, height))
    img.putdata(pixels)
    
    return img

def format_hex_data(data, bytes_per_line=18):
    """
    Format byte data as C hex array with proper formatting.
    """
    lines = []
    for i in range(0, len(data), bytes_per_line):
        chunk = data[i:i + bytes_per_line]
        hex_values = [f"0x{byte:02x}" for byte in chunk]
        line = "  " + ", ".join(hex_values) + ", "
        lines.append(line)
    
    # Remove trailing comma from last line
    if lines:
        lines[-1] = lines[-1].rstrip(", ") + " "
    
    return "\n".join(lines)

def generate_c_code_for_image(img_data, data_size, image_number):
    """
    Generate C code for a single image (array and descriptor).
    """
    hex_data = format_hex_data(img_data)
    
    c_code = f"""
#ifndef LV_ATTRIBUTE_IMG_IMAGE{image_number}
#define LV_ATTRIBUTE_IMG_IMAGE{image_number}
#endif

const LV_ATTRIBUTE_MEM_ALIGN LV_ATTRIBUTE_LARGE_CONST LV_ATTRIBUTE_IMG_IMAGE{image_number} uint8_t image{image_number}_map[] = {{
#if CONFIG_NICE_VIEW_WIDGET_INVERTED
        0xff, 0xff, 0xff, 0xff, /*Color of index 0*/
        0x00, 0x00, 0x00, 0xff, /*Color of index 1*/
#else
        0x00, 0x00, 0x00, 0xff, /*Color of index 0*/
        0xff, 0xff, 0xff, 0xff, /*Color of index 1*/
#endif

{hex_data}
}};

const lv_img_dsc_t image{image_number} = {{
  .header.cf = LV_IMG_CF_INDEXED_1BIT,
  .header.always_zero = 0,
  .header.reserved = 0,
  .header.w = {DISPLAY_WIDTH},
  .header.h = {DISPLAY_HEIGHT},
  .data_size = {data_size + 8},  // +8 for color palette
  .data = image{image_number}_map,
}};
"""
    return c_code

def rename_images_to_final_format():
    """
    Rename all images in the art folder to match the final generated format (image1.ext, image2.ext, etc.).
    Returns the number of files renamed.
    """
    if not os.path.exists(ART_FOLDER):
        print(f"Art folder '{ART_FOLDER}' not found!")
        return 0
    
    # Find all image files
    image_files = []
    for file_path in Path(ART_FOLDER).iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_FORMATS:
            image_files.append(file_path)
    
    if not image_files:
        return 0
    
    # Sort files for consistent numbering (same logic as get_image_files)
    def sort_key(path):
        name = path.name
        # Check if filename starts with digits followed by underscore or dash
        match = re.match(r'^(\d+)[_-]', name)
        if match:
            # Sort by numeric prefix, then by name
            return (0, int(match.group(1)), name.lower())
        else:
            # No numeric prefix, sort alphabetically after numbered files
            return (1, 0, name.lower())
    
    sorted_files = sorted(image_files, key=sort_key)
    
    renamed_count = 0
    
    for counter, img_path in enumerate(sorted_files, 1):
        name = img_path.name
        ext = img_path.suffix
        
        # Create new name matching the final format
        new_name = f"image{counter}{ext}"
        
        # Skip if already named correctly
        if name == new_name:
            print(f"  Skipped: \"{name}\" (already matches final format)")
            continue
        
        new_path = img_path.parent / new_name
        
        # Handle name conflicts
        if new_path.exists():
            temp_name = f"temp_image{counter}_{os.getpid()}{ext}"
            temp_path = img_path.parent / temp_name
            try:
                new_path.rename(temp_path)
            except OSError:
                pass  # If temp rename fails, try direct rename
        
        # Rename the file
        try:
            img_path.rename(new_path)
            print(f"  Renamed: \"{name}\" -> \"{new_name}\"")
            renamed_count += 1
        except OSError as e:
            print(f"  Failed to rename \"{name}\": {e}")
    
    if renamed_count > 0:
        print(f"Renamed {renamed_count} image(s) to final format (image1, image2, etc.).")
    
    return renamed_count

def get_image_files():
    """
    Get all supported image files from the art folder, sorted by naming convention.
    Files should already be renamed to standard format at this point.
    """
    if not os.path.exists(ART_FOLDER):
        print(f"Art folder '{ART_FOLDER}' not found!")
        return []
    
    image_files = []
    for file_path in Path(ART_FOLDER).iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_FORMATS:
            image_files.append(file_path)
    
    # Sort by numeric prefix if present, otherwise alphabetically
    def sort_key(path):
        name = path.name
        # Check if filename starts with digits followed by underscore or dash
        match = re.match(r'^(\d+)[_-]', name)
        if match:
            # Sort by numeric prefix, then by name
            return (0, int(match.group(1)), name.lower())
        else:
            # No numeric prefix, sort alphabetically after numbered files
            return (1, 0, name.lower())
    
    return sorted(image_files, key=sort_key)

def generate_art_c_file(save_previews=True):
    """
    Generate the complete art.c file from images in the art folder.
    
    Args:
        save_previews: If True, save preview images showing 1-bit conversion
    """
    image_files = get_image_files()
    
    if not image_files:
        print("No supported image files found in the art folder!")
        print(f"Supported formats: {', '.join(SUPPORTED_FORMATS)}")
        return False
    
    print(f"Found {len(image_files)} image files:")
    for i, img_file in enumerate(image_files, 1):
        print(f"  {i:2d}. {img_file.name}")
    
    # Save processed previews if requested
    if save_previews:
        print()
        preview_dir = save_processed_previews(image_files)
        print()
    
    # Generate C file header
    c_content = """/*
 *
 *
 */

#include <lvgl.h>

#ifndef LV_ATTRIBUTE_MEM_ALIGN
#define LV_ATTRIBUTE_MEM_ALIGN
#endif
"""
    
    # Process each image
    successful_images = []
    for i, img_file in enumerate(image_files, 1):
        print(f"Processing {img_file.name}...")
        
        # Resize and convert image using optimal methods
        img = resize_and_convert_image(img_file, save_preview=False, scaling_method="content_aware", dither_method="error_diffusion", maintain_aspect_ratio=True)
        if img is None:
            continue
        
        # Convert to LVGL data
        try:
            img_data, data_size = image_to_lvgl_data(img)
            
            # Generate C code
            c_code = generate_c_code_for_image(img_data, data_size, i)
            c_content += c_code
            
            successful_images.append(i)
            print(f"  Generated image{i} ({data_size + 8} bytes)")
            
        except Exception as e:
            print(f"  Error generating code for {img_file.name}: {e}")
            continue
    
    if not successful_images:
        print("No images were successfully processed!")
        return False
    
    # Write the art.c file
    try:
        with open(OUTPUT_FILE, 'w') as f:
            f.write(c_content)
        print(f"\nGenerated {OUTPUT_FILE} with {len(successful_images)} images")
        
        if save_previews and 'preview_dir' in locals():
            print(f"Preview images saved to: {preview_dir}")
        
        return successful_images
    except Exception as e:
        print(f"Error writing {OUTPUT_FILE}: {e}")
        return False

def update_peripheral_status_declarations(image_count):
    """
    Update the peripheral_status.c file with proper LV_IMG_DECLARE statements.
    """
    if not os.path.exists(PERIPHERAL_STATUS_FILE):
        print(f"Warning: {PERIPHERAL_STATUS_FILE} not found - skipping update")
        return
    
    try:
        # Read the current file
        with open(PERIPHERAL_STATUS_FILE, 'r') as f:
            content = f.read()
        
        # Generate new declarations
        declarations = []
        for i in range(1, image_count + 1):
            declarations.append(f"LV_IMG_DECLARE(image{i});")
        
        # Generate new anim_imgs array
        anim_imgs = ["const lv_img_dsc_t *anim_imgs[] = {"]
        for i in range(1, image_count + 1):
            anim_imgs.append(f"    &image{i},")
        anim_imgs.append("};")
        
        # Replace the declarations section
        # Find the start and end of LV_IMG_DECLARE block (check for both landscape and image naming)
        declare_start = content.find("LV_IMG_DECLARE(landscape")
        if declare_start == -1:
            declare_start = content.find("LV_IMG_DECLARE(image")
        
        if declare_start != -1:
            # Find the end of declarations (before anim_imgs array)
            declare_end = content.find("const lv_img_dsc_t *anim_imgs[]")
            if declare_end != -1:
                # Find the end of the anim_imgs array
                anim_end = content.find("};", declare_end) + 2
                
                # Replace the entire section
                new_content = (
                    content[:declare_start] + 
                    "\n".join(declarations) + "\n\n" +
                    "\n".join(anim_imgs) + "\n" +
                    content[anim_end:]
                )
                
                # Write back the file
                with open(PERIPHERAL_STATUS_FILE, 'w') as f:
                    f.write(new_content)
                
                print(f"Updated {PERIPHERAL_STATUS_FILE} with {image_count} image declarations")
                return True
        
        print(f"Warning: Could not find LV_IMG_DECLARE section in {PERIPHERAL_STATUS_FILE}")
        return False
        
    except Exception as e:
        print(f"Error updating {PERIPHERAL_STATUS_FILE}: {e}")
        return False

def main():
    """
    Main function to generate art gallery.
    """
    print("ZMK Landscape Art Gallery Generator")
    print("=" * 40)
    
    # Check if art folder exists
    if not os.path.exists(ART_FOLDER):
        print(f"Creating art folder: {ART_FOLDER}")
        os.makedirs(ART_FOLDER)
        print(f"Please place your images in the {ART_FOLDER} folder and run this script again.")
        return
    
    # Rename images to final format (image1, image2, etc.)
    print("Renaming images to final format (image1, image2, etc.)...")
    renamed_count = rename_images_to_final_format()
    if renamed_count > 0:
        print()  # Add blank line after rename output
    
    # Generate the art.c file with enhanced processing
    successful_images = generate_art_c_file(save_previews=True)
    if not successful_images:
        return
    
    # Update peripheral_status.c
    update_peripheral_status_declarations(len(successful_images))
    
    print("\n" + "=" * 40)
    print(f"Successfully generated art gallery with {len(successful_images)} images!")
    print(f"All images resized to {DISPLAY_WIDTH}x{DISPLAY_HEIGHT} pixels")
    print(f"Enhanced processing: multi-stage scaling + contrast/sharpness optimization")
    print(f"Converted to 1-bit format for nice!view display")
    print("\nYour ZMK landscape slideshow is ready to build!")

if __name__ == "__main__":
    main()
