"""
Icon generator for the Ramadan Fasting Schedule app.
Creates dynamic system tray icons showing countdown or moon symbol.
"""
from PIL import Image, ImageDraw, ImageFont
import os
import sys


def get_font(size=12):
    """Get a font, falling back to default if custom font not available."""
    try:
        # Try to use Segoe UI (Windows default)
        return ImageFont.truetype("segoeui.ttf", size)
    except OSError:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except OSError:
            return ImageFont.load_default()


def create_moon_icon(size=64):
    """Create a crescent moon icon for the system tray."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background circle (dark blue)
    bg_color = (25, 42, 86, 255)
    draw.ellipse([2, 2, size - 3, size - 3], fill=bg_color)

    # Crescent moon
    moon_color = (255, 215, 0, 255)  # Gold
    cx, cy = size // 2, size // 2
    r = size // 3

    # Full circle for moon
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=moon_color)

    # Cut out part to make crescent
    cut_offset = r // 2
    cut_r = r - 2
    draw.ellipse(
        [cx - cut_r + cut_offset, cy - cut_r - 2, cx + cut_r + cut_offset, cy + cut_r - 2],
        fill=bg_color,
    )

    # Small star
    star_x, star_y = cx + r - 4, cy - r + 6
    star_size = 4
    draw.ellipse(
        [star_x - star_size, star_y - star_size, star_x + star_size, star_y + star_size],
        fill=moon_color,
    )

    return img


def create_countdown_icon(hours, minutes, size=64):
    """
    Create an icon showing countdown time.
    Shows hours if > 0, otherwise minutes.
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background
    if hours > 0:
        bg_color = (25, 42, 86, 255)       # Dark blue - still time
    elif minutes > 15:
        bg_color = (43, 85, 43, 255)       # Dark green - getting close
    else:
        bg_color = (139, 69, 19, 255)      # Brown - very close

    draw.ellipse([2, 2, size - 3, size - 3], fill=bg_color)

    # Time text
    if hours > 0:
        text = f"{hours}h"
    else:
        text = f"{minutes}m"

    font = get_font(size=22)
    text_color = (255, 255, 255, 255)

    # Center text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 2

    draw.text((x, y), text, fill=text_color, font=font)

    return img


def create_text_icon(text, bg_color=(25, 42, 86, 255), size=64):
    """Create a simple text icon."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.ellipse([2, 2, size - 3, size - 3], fill=bg_color)

    font = get_font(size=16)
    text_color = (255, 255, 255, 255)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 2

    draw.text((x, y), text, fill=text_color, font=font)

    return img
