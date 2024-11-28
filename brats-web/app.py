from flask import Flask, request, render_template, send_file, jsonify
from math import pi, cos
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
from io import BytesIO

app = Flask(__name__)

# Function to apply mosaic effect (existing code)
def apply_mosaic(image, pixel_size):
    small = image.resize((image.size[0] // pixel_size, image.size[1] // pixel_size), Image.BILINEAR)
    mosaic_image = small.resize(image.size, Image.NEAREST)
    return mosaic_image

# Function to generate frames (existing code)
def generate_mosaic_frames_non_linear(image, start_pixel_size, end_pixel_size, num_frames):
    frames = []
    pixel_sizes = start_pixel_size + (end_pixel_size - start_pixel_size) * (
        0.5 * (1 - np.cos(np.linspace(0, pi, num_frames))))
    for pixel_size in pixel_sizes:
        pixel_size = max(1, int(pixel_size))
        frame = apply_mosaic(image, pixel_size)
        frames.append(frame)
    return frames

# Function to add reverse and loop (existing code)
def add_reverse_and_loop(frames):
    reversed_frames = list(reversed(frames))
    return frames + reversed_frames

# Main function to create GIF (existing code with small changes)
def Brat(text, start_pixel_size, end_pixel_size, fps, seconds, bg_color, text_color):
    num_frames = fps * seconds
    image_size = (500, 500)
    image = Image.new("RGB", image_size, bg_color)

    draw = ImageDraw.Draw(image)
    font_size = 120

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    text_position = ((image_size[0] - text_width) // 2, (image_size[1] - text_height) // 2)
    draw.text(text_position, text, fill=text_color, font=font)

    stretched_image = image.resize((500, 700))
    short_edge = min(stretched_image.size)
    left = (stretched_image.width - short_edge) // 2
    top = (stretched_image.height - short_edge) // 2
    right = left + short_edge
    bottom = top + short_edge
    square_image = stretched_image.crop((left, top, right, bottom))

    frames_non_linear = generate_mosaic_frames_non_linear(square_image, start_pixel_size, end_pixel_size, num_frames)
    loop_frames = add_reverse_and_loop(frames_non_linear)

    # Save GIF in memory
    gif_io = BytesIO()
    loop_frames[0].save(
        gif_io, format="GIF", save_all=True, append_images=loop_frames[1:], duration=1000 // fps, loop=0
    )
    gif_io.seek(0)
    return gif_io

# Flask route for the form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        start_pixel_size = int(request.form['start_pixel_size'])
        end_pixel_size = int(request.form['end_pixel_size'])
        fps = int(request.form['fps'])
        seconds = int(request.form['seconds'])
        bg_color = request.form['bg_color']
        text_color = request.form['text_color']

        gif = Brat(text, start_pixel_size, end_pixel_size, fps, seconds, bg_color, text_color)

        return send_file(gif, mimetype='image/gif', as_attachment=True,
                         download_name=f'{text}_{start_pixel_size}_{end_pixel_size}_{fps}_{bg_color}_{text_color}.gif')
    return render_template('index.html')

# Flask route for generating a GIF preview
@app.route('/preview_gif', methods=['GET'])
def preview_gif():
    text = request.args.get('text', 'brat')
    start_pixel_size = int(request.args.get('start_pixel_size', 1))
    end_pixel_size = int(request.args.get('end_pixel_size', 22))
    fps = int(request.args.get('fps', 120))
    seconds = int(request.args.get('seconds', 2))
    bg_color = request.args.get('bg_color', '#89CC04')
    text_color = request.args.get('text_color', 'black')

    gif = Brat(text, start_pixel_size, end_pixel_size, fps, seconds, bg_color, text_color)

    # Send the GIF as a response
    return send_file(gif, mimetype='image/gif')

if __name__ == '__main__':
    app.run(debug=True)
