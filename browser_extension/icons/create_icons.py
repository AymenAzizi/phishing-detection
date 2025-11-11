#!/usr/bin/env python3
"""
Create simple placeholder icons for the browser extension
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple shield icon"""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw shield shape
    shield_color = (59, 130, 246)  # Blue color
    margin = size // 8
    
    # Shield outline
    points = [
        (size//2, margin),  # Top center
        (size - margin, margin + size//4),  # Top right
        (size - margin, size - margin - size//4),  # Bottom right
        (size//2, size - margin),  # Bottom center
        (margin, size - margin - size//4),  # Bottom left
        (margin, margin + size//4),  # Top left
    ]
    
    draw.polygon(points, fill=shield_color, outline=(255, 255, 255), width=2)
    
    # Add checkmark or shield symbol
    if size >= 32:
        # Draw checkmark
        check_color = (255, 255, 255)
        cx, cy = size//2, size//2
        check_size = size//4
        
        # Checkmark lines
        draw.line([
            (cx - check_size//2, cy),
            (cx - check_size//4, cy + check_size//2)
        ], fill=check_color, width=max(2, size//16))
        
        draw.line([
            (cx - check_size//4, cy + check_size//2),
            (cx + check_size//2, cy - check_size//2)
        ], fill=check_color, width=max(2, size//16))
    
    # Save the image
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

def create_warning_icon(size, filename):
    """Create a warning version of the icon"""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw shield shape in red
    shield_color = (239, 68, 68)  # Red color
    margin = size // 8
    
    # Shield outline
    points = [
        (size//2, margin),  # Top center
        (size - margin, margin + size//4),  # Top right
        (size - margin, size - margin - size//4),  # Bottom right
        (size//2, size - margin),  # Bottom center
        (margin, size - margin - size//4),  # Bottom left
        (margin, margin + size//4),  # Top left
    ]
    
    draw.polygon(points, fill=shield_color, outline=(255, 255, 255), width=2)
    
    # Add warning symbol
    if size >= 32:
        # Draw exclamation mark
        warning_color = (255, 255, 255)
        cx, cy = size//2, size//2
        
        # Exclamation line
        draw.line([
            (cx, cy - size//4),
            (cx, cy + size//8)
        ], fill=warning_color, width=max(3, size//12))
        
        # Exclamation dot
        dot_size = max(2, size//16)
        draw.ellipse([
            (cx - dot_size, cy + size//4 - dot_size),
            (cx + dot_size, cy + size//4 + dot_size)
        ], fill=warning_color)
    
    # Save the image
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

def main():
    """Create all required icons"""
    # Create icons directory if it doesn't exist
    os.makedirs('icons', exist_ok=True)
    
    # Standard icon sizes
    sizes = [16, 32, 48, 128]
    
    # Create normal icons
    for size in sizes:
        create_icon(size, f'icons/icon{size}.png')
    
    # Create warning icons
    for size in sizes:
        create_warning_icon(size, f'icons/warning{size}.png')
    
    print("\n✅ All icons created successfully!")
    print("📁 Icons saved in the 'icons' directory")

if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print("❌ PIL (Pillow) not installed. Installing...")
        import subprocess
        subprocess.run(['pip', 'install', 'Pillow'])
        main()
    except Exception as e:
        print(f"❌ Error creating icons: {e}")
        print("Creating simple text-based icons as fallback...")
        
        # Fallback: create simple colored squares
        os.makedirs('icons', exist_ok=True)
        for size in [16, 32, 48, 128]:
            # Normal icon (blue)
            img = Image.new('RGBA', (size, size), (59, 130, 246, 255))
            img.save(f'icons/icon{size}.png', 'PNG')
            
            # Warning icon (red)
            img = Image.new('RGBA', (size, size), (239, 68, 68, 255))
            img.save(f'icons/warning{size}.png', 'PNG')
        
        print("✅ Fallback icons created!")
