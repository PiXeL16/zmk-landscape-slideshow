#!/usr/bin/env python3
"""Test aspect ratio preservation."""

from generate_art import *
from pathlib import Path

def test_aspect_ratio():
    """Generate comparison images with and without aspect ratio preservation."""
    files = get_image_files()
    if not files:
        print('No images found!')
        return
    
    comparison_dir = Path('art/aspect_comparison')
    comparison_dir.mkdir(exist_ok=True)
    
    f = files[0]
    print(f'Testing aspect ratio with {f.name}...')
    
    print('Generating with aspect ratio preserved...')
    with_aspect = resize_and_convert_image(f, False, 'content_aware', 'error_diffusion', True)
    if with_aspect: 
        with_aspect.save(comparison_dir / f'{f.stem}_with_aspect.png')
    
    print('Generating without aspect ratio (stretched)...')
    without_aspect = resize_and_convert_image(f, False, 'content_aware', 'error_diffusion', False)  
    if without_aspect: 
        without_aspect.save(comparison_dir / f'{f.stem}_stretched.png')
    
    print(f'Comparison saved to {comparison_dir}/')

if __name__ == "__main__":
    test_aspect_ratio()
