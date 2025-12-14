import sys
from PIL import Image

def img_to_ansi(image_path, width=80):
    img = Image.open(image_path)
    # Convert to RGB (remove alpha)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    w, h = img.size
    aspect_ratio = h / w
    
    # Terminal font aspect ratio correction (~0.5)
    # We want final height in chars.
    # Each char is 2 vertical sub-pixels.
    
    target_height = int(width * aspect_ratio * 0.5)
    
    # Resize image to (width, target_height * 2)
    img = img.resize((width, target_height * 2), Image.Resampling.LANCZOS)
    
    pixels = img.load()
    output = ""
    
    for y in range(0, img.height, 2):
        line = ""
        for x in range(img.width):
            # Top pixel
            r1, g1, b1 = pixels[x, y]
            # Bottom pixel
            if y + 1 < img.height:
                r2, g2, b2 = pixels[x, y+1]
            else:
                r2, g2, b2 = 0, 0, 0 # Black default
            
            # ANSI: Foreground (Text) = Top Pixel, Background = Bottom Pixel
            # Char: ▀ (Upper Half Block)
            line += f"\x1b[38;2;{r1};{g1};{b1}m\x1b[48;2;{r2};{g2};{b2}m▀\x1b[0m"
        output += line + "\n"
    
    return output

if __name__ == "__main__":
    import os
    # Use uv python to ensure pillow is found
    # Assume script is run with python that has pillow
    print(img_to_ansi(sys.argv[1], width=int(sys.argv[2]) if len(sys.argv) > 2 else 60))
