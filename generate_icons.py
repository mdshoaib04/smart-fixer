#!/usr/bin/env python3
"""
Script to generate PWA icons for SmartFixer
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_icon(size, filename):
    """Create a simple icon with the SmartFixer logo"""
    # Create a new image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a circle background
    draw.ellipse([0, 0, size, size], fill=(139, 69, 255, 255))  # Purple color
    
    # Draw the "S" letter in white
    # We'll draw a simplified "S" shape
    margin = size // 4
    center = size // 2
    
    # Draw top curve of S
    draw.arc([margin, margin, center, center], 180, 270, fill=(255, 255, 255, 255), width=size//10)
    
    # Draw middle line
    draw.line([margin, center, center + margin//2, center], fill=(255, 255, 255, 255), width=size//10)
    
    # Draw bottom curve of S
    draw.arc([center - margin//2, center, size - margin, size - margin], 0, 90, fill=(255, 255, 255, 255), width=size//10)
    
    # Save the image
    img.save(filename)

def main():
    """Generate all required icon sizes"""
    icon_sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    # Create icons directory if it doesn't exist
    os.makedirs('static/icons', exist_ok=True)
    
    # Generate icons for each size
    for size in icon_sizes:
        filename = f'static/icons/icon-{size}x{size}.png'
        create_icon(size, filename)
        print(f'Created {filename}')

if __name__ == '__main__':
    main()