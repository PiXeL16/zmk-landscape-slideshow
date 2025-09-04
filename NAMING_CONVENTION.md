# Image Naming Convention

This document explains the standardized naming convention for images in the art generation system.

## Standard Format

```
01_descriptive_name.png
02_another_image.jpg
03_final_image.png
```

**Format Rules:**
- **2-digit number prefix**: `01`, `02`, `03`, etc. (not `1`, `2`, `3`)
- **Separator**: Use underscore `_` or dash `-`
- **Descriptive name**: Brief description of the image
- **File extension**: `.png`, `.jpg`, `.jpeg`, `.bmp`, or `.gif`

## Why This Matters

**Processing Order:**
1. Images with numeric prefixes are processed first, in numerical order
2. Images without prefixes are processed second, in alphabetical order
3. This determines the final `image1`, `image2`, `image3`... sequence

**Examples:**

| Filename | Becomes | Display Order |
|----------|---------|---------------|
| `01_mountain.png` | `image1` | First (10s) |
| `02_forest.jpg` | `image2` | Second (10s) |  
| `03_ocean.png` | `image3` | Third (10s) |
| `sunset.jpg` | `image4` | Fourth (10s) |
| `valley.png` | `image5` | Fifth (10s) |

## Tools for Naming

### Check Current Naming
```bash
make check-images
```
Shows current files and suggests improvements.

### Get Rename Commands
```bash
make rename-images
```
Shows exact `mv` commands to rename your files.

### Auto-Rename Everything
```bash
make rename-images-auto  
```
Automatically renames all images to follow the convention.

## Best Practices

**Good Names:**
- `01_mountain_peak.png`
- `02_forest_sunset.jpg`
- `03_ocean_waves.png`
- `04_city_skyline.jpg`

**Avoid:**
- `1_image.png` (single digit)
- `mountain peak.png` (spaces)
- `IMG_001.JPG` (not descriptive)
- `photo.png` (not numbered)

## Common Scenarios

### Mixed Naming
If you have both numbered and non-numbered files:
```
01_mountain.png    -> image1
02_forest.jpg      -> image2
sunset.png         -> image3 (processed after numbered)
valley.jpg         -> image4 (processed after numbered)
```

### All Alphabetical  
If no files have numeric prefixes:
```
forest.jpg         -> image1 (first alphabetically)
mountain.png       -> image2
ocean.png          -> image3  
sunset.jpg         -> image4 (last alphabetically)
```

### Renumbering
To reorder images, just rename with new numbers:
```bash
mv art/03_ocean.png art/01_ocean.png
mv art/01_mountain.png art/03_mountain.png
```

## Integration with Workflow

The naming convention integrates seamlessly with the build process:

1. **Add images** with proper naming to `art/` folder
2. **Check naming** with `make check-images`
3. **Auto-fix** with `make rename-images-auto` if needed  
4. **Generate** with `make generate`
5. **Build** your ZMK firmware as usual

The slideshow will display images in the exact order you specified with your numbering!
