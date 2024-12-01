import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

data_path = r"..\animate.csv"
output = "./animation/anim_{:05d}.png"

df = pd.read_csv(data_path)

before = -20
after = 20

fps = 120

font_hmd_name = ImageFont.truetype("arial.ttf", 50)
font_timestamp = ImageFont.truetype("arial.ttf", 50)
font_time_to_red = ImageFont.truetype("arial.ttf", 50)
font_contact = ImageFont.truetype("arial.ttf", 50)

position_HMD = (50, 50)  # Coordinates where the text will be placed
font_color = (0, 0, 0)  # White color (RGB)
font_color_red = (255, 0, 0)  # White color (RGB)
font_color_contact = (255, 255, 255)

position_hmd = (50, 0)  # Coordinates where the text will be placed
position_timestamp = (50, 50)  # Coordinates where the text will be placed
position_red = (50, 100)  # Coordinates where the text will be placed
position_contact = (50, 150)  # Coordinates where the text will be placed



full_length = -before + (df["frame end"] - df["frame start"]).max() + after

timestamps = np.arange(before, before + full_length, 1) / 120

videos = []

for i, row in df.iterrows():
    frame_start = row["frame start"] + before
    time_contact = row["frame start"]
    time_red = row["frame end"]
    frame_end = frame_start + full_length
    hmd = row['HMD']
    path = row['filename'].strip('"')

    video = []
    for i, frame_index in enumerate( range(frame_start, frame_end)):
        image = Image.open(path.format(frame_index))
        draw = ImageDraw.Draw(image)
        draw.text(position_hmd, hmd, fill=font_color, font=font_hmd_name)
        ts_text = "Time: {:0.3f}".format(timestamps[i] * 1000)
        draw.text(position_timestamp, ts_text, fill=font_color, font=font_timestamp)

        if frame_index == time_red:
            timestamp_red = timestamps[i]

        if frame_index >= time_red:
            red_text = "MtP: {:0.3f}".format(timestamp_red * 1000)
            draw.text(position_red, red_text, fill=font_color_red, font=font_time_to_red)

        if frame_index >= time_contact:
            contact_text = "Contact!"
            draw.text(position_contact, contact_text, fill=font_color_contact, font=font_contact)
        video.append(image)
    videos.append(video)



rows = 2
columns = 3


widths, heights = image.size

width = widths * columns
height = heights * rows


final_video = []
for i in range(len(videos[0])):
    composite = Image.new("RGB", (width, height))
    final_video.append(composite)

for vid, video in enumerate(videos):
    for fid, frame in enumerate(video):
        row = vid // columns
        col = vid % columns
        y_offset = row * heights
        x_offset = col * widths
        final_video[fid].paste(frame, (x_offset, y_offset))

for vid, frame in enumerate(tqdm(final_video)):
    frame.save(output.format(vid))

# ffmpeg -framerate 2 -i anim_%05d.png -c:v libvpx -crf 10 -b:v 1M output.webm








