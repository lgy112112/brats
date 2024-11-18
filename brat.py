from math import pi, cos
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Function to apply mosaic effect
def apply_mosaic(image, pixel_size):
    # Reduce resolution
    small = image.resize((image.size[0] // pixel_size, image.size[1] // pixel_size), Image.BILINEAR)
    # Scale back to original size
    mosaic_image = small.resize(image.size, Image.NEAREST)
    return mosaic_image

# Function to generate frames for the GIF with non-linear speed
def generate_mosaic_frames_non_linear(image, start_pixel_size, end_pixel_size, num_frames):
    frames = []
    # Generate non-linear interpolation using a sine function
    pixel_sizes = start_pixel_size + (end_pixel_size - start_pixel_size) * (
        0.5 * (1 - np.cos(np.linspace(0, pi, num_frames)))  # Ease-in and ease-out
    )
    for pixel_size in pixel_sizes:
        pixel_size = max(1, int(pixel_size))  # Ensure pixel_size is at least 1
        frame = apply_mosaic(image, pixel_size)
        frames.append(frame)
    return frames

# Function to add reverse and loop for the GIF
def add_reverse_and_loop(frames):
    reversed_frames = list(reversed(frames))  # Create reversed frames
    full_frames = frames + reversed_frames  # Combine original and reversed frames
    return full_frames

# Main function to create the GIF
def Brat(text, start_pixel_size, end_pixel_size, fps, seconds, bg_color, text_color, output_path="mosaic_animation.gif"):
    # Parameters for the GIF
    num_frames = fps * seconds

    # Create the base image
    image_size = (500, 500)
    image = Image.new("RGB", image_size, bg_color)  # Use input background color

    # Prepare to draw text
    draw = ImageDraw.Draw(image)
    font_size = 120

    try:
        # Use a common Arial font (system dependent)
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        # Default to a PIL internal font if Arial is unavailable
        font = ImageFont.load_default()

    # Determine text bounding box and position
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    text_position = ((image_size[0] - text_width) // 2, (image_size[1] - text_height) // 2)

    # Draw the text on the image
    draw.text(text_position, text, fill=text_color, font=font)  # Use input text color

    # Stretch the image to create the "stretched" effect
    stretched_image = image.resize((500, 700))  # Stretch horizontally

    # Crop the stretched image to make it a square with the short edge as the size
    short_edge = min(stretched_image.size)  # Find the shortest side
    left = (stretched_image.width - short_edge) // 2
    top = (stretched_image.height - short_edge) // 2
    right = left + short_edge
    bottom = top + short_edge
    square_image = stretched_image.crop((left, top, right, bottom))

    # Generate non-linear frames
    frames_non_linear = generate_mosaic_frames_non_linear(square_image, start_pixel_size, end_pixel_size, num_frames)

    # Add reverse and loop
    loop_frames = add_reverse_and_loop(frames_non_linear)

    # Save the looped animation as a GIF
    loop_frames[0].save(
        output_path,
        save_all=True,
        append_images=loop_frames[1:],
        duration=1000 // fps,  # Frame duration in milliseconds
        loop=0  # Infinite loop
    )

    print(f"GIF saved at {output_path}")


if __name__ == "__main__":
    # The text to display on the GIF
    text = "fuck"  # Input text (e.g., emoji, words, etc.)

    # Parameters for the animation
    start_pixel_size = 1  # The starting size of the mosaic pixels
    end_pixel_size = 22  # The ending size of the mosaic pixels
    fps = 120  # Frames per second for the GIF
    seconds = 2  # Total duration of the animation in seconds

    # Colors for background and text
    bg_color = "#89CC04"  # Background color (hex code or RGB tuple)
    text_color = "black"  # Text color (hex code or RGB tuple)

    # Clean the input text to make it a valid filename
    # Replace any invalid characters (like ':', '?', etc.) with an underscore '_'
    valid_text = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in text)
    
    # Call the Brat function to generate the GIF
    # The output path will use the cleaned filename (e.g., "GIF/__.gif" for ":)")
    Brat(
        text,  # The text to display
        start_pixel_size,  # Starting pixel size for the mosaic effect
        end_pixel_size,  # Ending pixel size for the mosaic effect
        fps,  # Frames per second for the animation
        seconds,  # Duration of the animation in seconds
        bg_color,  # Background color
        text_color,  # Text color
        output_path=f"GIF/{valid_text}.gif"  # Path to save the resulting GIF
    )
