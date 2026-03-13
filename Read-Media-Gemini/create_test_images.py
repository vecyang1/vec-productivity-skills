from PIL import Image
import os

def create_dummy_image(filename, color):
    img = Image.new('RGB', (100, 100), color=color)
    img.save(filename)
    print(f"Created {filename}")

create_dummy_image("test_image_1.jpg", "red")
create_dummy_image("test_image_2.jpg", "blue")
