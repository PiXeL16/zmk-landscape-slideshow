#!/usr/bin/env python3
"""
Compare different scaling methods and dithering techniques side-by-side.
"""

from generate_art import *
from PIL import Image
from pathlib import Path

def compare_methods():
    """Generate comparison images using different processing methods."""
    files = get_image_files()
    if not files:
        print('No images found!')
        return
    
    methods = ['adaptive', 'edge_preserving', 'content_aware', 'area_sampling']
    dither_methods = ['floyd_steinberg', 'threshold_adaptive', 'error_diffusion']
    
    preview_dir = Path(ART_FOLDER) / 'method_comparison'
    preview_dir.mkdir(exist_ok=True)
    
    print(f'Generating method comparison previews in {preview_dir}...')
    
    # Test first image with all method combinations
    img_file = files[0]
    print(f'Testing methods for {img_file.name}:')
    
    successful = 0
    total = len(methods) * len(dither_methods)
    
    for method in methods:
        for dither in dither_methods:
            try:
                print(f'  Processing: {method} + {dither}...', end=' ')
                processed = resize_and_convert_image(
                    img_file, 
                    save_preview=False, 
                    scaling_method=method, 
                    dither_method=dither,
                    maintain_aspect_ratio=True
                )
                if processed:
                    preview_name = f'{img_file.stem}_{method}_{dither}.png'
                    processed.save(preview_dir / preview_name)
                    print('✓')
                    successful += 1
                else:
                    print('✗ (processing failed)')
            except Exception as e:
                print(f'✗ ({str(e)[:50]}...)')
    
    print(f'\nGenerated {successful}/{total} comparison images in {preview_dir}/')
    print('\nComparison matrix:')
    print('Scaling Methods: adaptive, edge_preserving, content_aware, area_sampling')
    print('Dithering: floyd_steinberg, threshold_adaptive, error_diffusion')

if __name__ == "__main__":
    compare_methods()
