# Art Folder

Place your images here to generate the art gallery.

## Supported Formats
- PNG (recommended)
- JPEG/JPG
- BMP
- GIF

## Naming Convention
**Use numbered prefixes for consistent ordering:**
```
01_mountain.png
02_forest.png
03_ocean.png
04_sunset.png
```

## Helpful Commands
- `make generate` - Auto-rename images + generate art gallery (recommended)
- `make rename-images` - Just rename images to standard format
- `make check-images` - Check current naming
- `make info` - Show project status

## Tips
- **Just add images with ANY names** - `make generate` will auto-rename them!
- Images will be resized to 68×140 pixels (vertical orientation)
- High contrast images work best for 1-bit conversion
- The final numbered order determines the slideshow sequence
- Spaces and special characters in filenames are handled automatically

## Current Images
- image1.png (renamed from original)
- Preview images saved to: previews/

## Preview Images
The system automatically generates preview images showing what your 1-bit conversion looks like:
- Check `previews/image1_preview_image1.png` to see the processed result
- These previews help you verify the 1-bit conversion quality before building
