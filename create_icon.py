from PIL import Image, ImageDraw, ImageFont
import os

def create_smartfixer_icon():
    """Create a simple SmartFixer icon"""
    # Create a new image with transparent background
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a circle background with purple color (similar to the website theme)
    draw.ellipse([0, 0, size, size], fill=(139, 69, 255, 255))  # Purple color
    
    # Draw the "S" letter in white
    # We'll draw a simplified "S" shape
    margin = size // 4
    center = size // 2
    
    # Draw top curve of S
    draw.arc([margin, margin, center, center], 180, 270, fill=(255, 255, 255, 255), width=size//16)
    
    # Draw middle line
    draw.line([margin, center, center + margin//2, center], fill=(255, 255, 255, 255), width=size//16)
    
    # Draw bottom curve of S
    draw.arc([center - margin//2, center, size - margin, size - margin], 0, 90, fill=(255, 255, 255, 255), width=size//16)
    
    # Draw a small rocket icon to represent "SmartFixer"
    # Rocket body
    rocket_width = size // 8
    rocket_height = size // 4
    rocket_x = size - margin - rocket_width
    rocket_y = margin
    
    # Draw rocket body
    draw.rectangle([rocket_x, rocket_y, rocket_x + rocket_width, rocket_y + rocket_height], 
                   fill=(255, 255, 255, 255))
    
    # Draw rocket tip
    draw.polygon([
        (rocket_x + rocket_width // 2, rocket_y - size // 16),
        (rocket_x, rocket_y),
        (rocket_x + rocket_width, rocket_y)
    ], fill=(255, 215, 0, 255))  # Gold color
    
    # Draw flames
    draw.polygon([
        (rocket_x + rocket_width // 2, rocket_y + rocket_height),
        (rocket_x + rocket_width // 4, rocket_y + rocket_height + size // 16),
        (rocket_x + 3 * rocket_width // 4, rocket_y + rocket_height + size // 16)
    ], fill=(255, 140, 0, 255))  # Orange color
    
    # Save as ICO with multiple sizes
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    resized_images = []
    
    for size in icon_sizes:
        resized_img = img.resize(size, Image.Resampling.LANCZOS)
        resized_images.append(resized_img)
    
    # Save as ICO
    ico_path = "icon.ico"
    resized_images[0].save(
        ico_path,
        format='ICO',
        sizes=[(size[0], size[1]) for size in icon_sizes]
    )
    
    print(f"Successfully created icon.ico")
    return ico_path

if __name__ == "__main__":
    create_smartfixer_icon()