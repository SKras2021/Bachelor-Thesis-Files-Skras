from PIL import Image
import os

inp = "screenshots"
out = "screenshots_new"
size = (500, 375)

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(inp):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        input_path = os.path.join(inp, filename)
        output_path = os.path.join(out, filename)

        try:
            with Image.open(input_path) as img:
                resized_img = img.resize(size, Image.Resampling.LANCZOS)
                resized_img.save(output_path)

        except Exception as e:
            print(e)
