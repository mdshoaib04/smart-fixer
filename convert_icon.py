from PIL import Image
import os

def convert_png_to_ico(png_path, ico_path):
    """Convert a PNG image to ICO format"""
    try:
        # Open the PNG image
        img = Image.open(png_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Resize to standard icon sizes
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        resized_images = []
        
        for size in icon_sizes:
            resized_img = img.resize(size, Image.Resampling.LANCZOS)
            resized_images.append(resized_img)
        
        # Save as ICO
        resized_images[0].save(
            ico_path,
            format='ICO',
            sizes=[(size[0], size[1]) for size in icon_sizes]
        )
        
        print(f"Successfully converted {png_path} to {ico_path}")
        return True
    except Exception as e:
        print(f"Error converting icon: {e}")
        return False

if __name__ == "__main__":
    # Paths
    png_path = "static/downloads/icon.png"
    ico_path = "icon.ico"
    
    # Convert the icon
    if os.path.exists(png_path):
        convert_png_to_ico(png_path, ico_path)
    else:
        print(f"PNG file not found: {png_path}")