# Art Generation System

This document explains how to use the automated art generation system for the ZMK Landscape Slideshow project.

## Overview

The art generation system allows you to automatically create the `art.c` gallery from image files. It handles:

- **Image Processing**: Automatically resizes images to 140×68 pixels (nice!view display size)
- **Format Conversion**: Converts images to 1-bit black and white with optimized dithering
- **C Code Generation**: Creates LVGL-compatible C arrays and descriptors
- **Integration**: Updates peripheral_status.c with proper image declarations

## Quick Start

### Using the Makefile (Recommended)

1. **Initial setup**:
   ```bash
   make setup
   ```

2. **Add your images** to the `art/` folder:
   ```bash
   # Copy your images to the art folder
   cp your_images/* art/
   ```

3. **Generate the art gallery**:
   ```bash
   make generate
   ```

4. **Build your ZMK firmware** as usual - the new art gallery will be included!

### Manual Method

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Add your images** to the `art/` folder and run**:
   ```bash
   python generate_art.py
   ```

## Makefile Commands

The included Makefile provides convenient commands for the entire workflow:

| Command | Description |
|---------|-------------|
| `make setup` | Initial setup - installs dependencies and creates directories |
| `make generate` | Generate art gallery from images (auto-rename + backup) |
| `make backup` | Manually backup current art.c and peripheral_status.c |
| `make restore` | Restore from the most recent backup |
| `make info` | Show project status and statistics |
| `make clean` | Clean up generated files and backups |
| `make test` | Test the generation with available images |
| `make watch` | Auto-regenerate when images change (requires `fswatch`) |
| `make check-images` | Verify image files and check naming convention |
| `make rename-images` | Rename all images to standard naming convention |
| `make preview-images` | Generate preview images showing 1-bit conversion |
| `make quality-check` | Analyze image processing quality and reduction ratios |

### Advanced Commands

- `make dev-setup` - Setup development environment with additional tools
- `make format` - Format Python code (requires `black`)
- `make lint` - Check Python syntax

## Supported Image Formats

- PNG (recommended)
- JPEG/JPG  
- BMP
- GIF

## Image Processing Details

### Automatic Resizing  
- All images are resized to **68×140 pixels** to fit the nice!view display (vertical orientation)
- High-quality Lanczos resampling is used for best results
- Aspect ratio is not preserved to ensure consistent display size

### 1-Bit Conversion
- Images are converted to grayscale first
- Floyd-Steinberg dithering is applied for optimal 1-bit conversion
- This produces the classic "1-bit art" aesthetic similar to Hammerbeam's work

### Color Mapping
- **Black pixels** (0) represent dark areas
- **White pixels** (1) represent light areas  
- The display supports both normal and inverted color schemes

## File Structure

```
zmk-landscape-slideshow/
├── art/                          # Your input images go here
│   ├── image1.png
│   ├── image2.jpg
│   └── ...
├── generate_art.py               # Art generation script
├── requirements.txt              # Python dependencies
└── boards/shields/nice_view_custom/widgets/
    ├── art.c                    # Generated art gallery (OUTPUT)
    └── peripheral_status.c      # Updated with declarations
```

## Generated Code Structure

For each image, the script generates:

### 1. Image Data Array
```c
const uint8_t image1_map[] = {
    // Color palette for indexed 1-bit format
    #if CONFIG_NICE_VIEW_WIDGET_INVERTED
        0xff, 0xff, 0xff, 0xff, /*Color of index 0*/
        0x00, 0x00, 0x00, 0xff, /*Color of index 1*/
    #else
        0x00, 0x00, 0x00, 0xff, /*Color of index 0*/
        0xff, 0xff, 0xff, 0xff, /*Color of index 1*/
    #endif
    
    // Pixel data as hexadecimal bytes
    0xf8, 0x00, 0x00, 0x00, 0x00, ...
};
```

### 2. Image Descriptor
```c
const lv_img_dsc_t image1 = {
    .header.cf = LV_IMG_CF_INDEXED_1BIT,
    .header.w = 140,
    .header.h = 68,
    .data_size = 1240,  // Including 8-byte color palette
    .data = image1_map,
};
```

### 3. Declaration Updates
The script automatically updates `peripheral_status.c` with:
```c
LV_IMG_DECLARE(image1);
LV_IMG_DECLARE(image2);
// ... etc

const lv_img_dsc_t *anim_imgs[] = {
    &image1,
    &image2,
    // ... etc
};
```

## Safety Features

The system includes several safety features to protect your work:

### Automatic Backups
- `make generate` automatically backs up your current files before generating new ones
- Backups are timestamped: `art.c.backup.20241215_143022`
- Use `make restore` to revert to the most recent backup
- Use `make backup` to manually create backups anytime

### Validation
- The script validates image formats and sizes before processing
- `make check-images` shows what images will be processed
- `make info` displays current project status
- Error handling prevents partial file corruption

### File Watch Mode
- `make watch` automatically regenerates when you add/change images
- Requires `fswatch` (install with `brew install fswatch` on macOS)
- Perfect for iterative design work

## Tips for Best Results

### Image Selection
- **High contrast** images work best for 1-bit conversion
- **Simple compositions** translate better to the small display size
- **Line art** and **illustrations** often work better than photographs

### Image Preparation
- You can pre-process images in your favorite editor before running the script
- Consider adjusting contrast and brightness for better 1-bit conversion
- The script handles resizing, so don't worry about exact dimensions

### Naming Convention and Order

**Final Format:**
```
image1.png    # Becomes image1 in C code
image2.jpg    # Becomes image2 in C code
image3.png    # Becomes image3 in C code
image4.gif    # Becomes image4 in C code
```

**Key Points:**
- Images are **automatically renamed** to `image1`, `image2`, etc. during generation
- Processing order is **alphabetical**, then by existing numeric prefixes
- **Any original filenames work** - the system handles renaming automatically
- Final names in art folder **match the C code** (`image1`, `image2`, etc.)

**Preview and Checking:**
- `make check-images` - Shows current files and their processing order
- `make preview-images` - Generates preview images showing 1-bit conversion
- `make generate` - Automatically renames, processes, and generates (recommended)

**How It Works:**
1. Add images with **any names** to `art/` folder
2. Run `make generate` 
3. Images are renamed to `image1.ext`, `image2.ext`, etc.
4. 1-bit preview images are saved to `art/previews/`
5. C code is generated with `image1`, `image2`, etc.

## Troubleshooting

### Script Issues
- **"No supported image files found"**: Check that your images are in the `art/` folder and have supported extensions
- **"Error processing image"**: The image file may be corrupted or in an unsupported format
- **Permission errors**: Ensure the script has write access to the widgets folder

### Display Issues
- **Images appear inverted**: This is normal - the nice!view can display in both normal and inverted modes
- **Images look blocky**: This is expected for 1-bit conversion - try images with higher contrast

### Build Issues
- **Compiler errors**: Ensure you rebuild completely after running the art generation script
- **Missing declarations**: The script should automatically update `peripheral_status.c`, but check this file if you encounter undefined references

## Advanced Usage

### Custom Display Size
If you need to change the display size, edit these constants in `generate_art.py`:
```python
DISPLAY_WIDTH = 140   # Change as needed
DISPLAY_HEIGHT = 68   # Change as needed
```

### Manual C File Editing
The generated `art.c` file is standard C code and can be manually edited if needed. However, re-running the script will overwrite manual changes.

### Custom Image Processing
The script uses PIL (Pillow) for image processing. You can modify the `resize_and_convert_image()` function to implement custom processing steps.

## Contributing

If you improve the art generation script or find issues, please contribute back to the project! The system is designed to be extensible and maintainable.

---

*This art generation system was created to make it easy to add custom 1-bit artwork to your ZMK keyboards while maintaining the same high-quality aesthetic as Hammerbeam's original work.*
