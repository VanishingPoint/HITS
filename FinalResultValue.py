import os
from PIL import Image, ImageDraw, ImageFont

def probability_hits_result(input_number, image_a_path, image_b_path, output_path):
    # Choose the image based on the input number
    if input_number >= 50:
        chosen_image_path = image_a_path
    else:
        chosen_image_path = image_b_path

    # Open the chosen image
    img = Image.open(chosen_image_path)
    
    # Create a drawing context
    draw = ImageDraw.Draw(img)
    
    # Define the text to display
    text = f"{input_number}%"
    
    # Try to load a scalable font
    try:
        # Using the system font available on macOS (Helvetica)
        font = ImageFont.truetype("/Library/Fonts/Helvetica.ttc", 90)
    except IOError:
        print("Font file not found, using default font.")
        font = ImageFont.load_default(90)  # Fallback to default if the font is not found

    # Get text size using textbbox() (for calculating the size of the text)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Set a custom position (x, y) in pixels
    text_position = (270, 250)
    
    # Add text to image (white color)
    draw.text(text_position, text, fill="white", font=font)

    # Save the image to the specified output path
    img.save(output_path)
    print(f"Image saved to {output_path}")

# Example usage
input_number = 46  # You can change this value
image_a_path = r"C:\Users\richy\Documents\Git\HITS\Results images\concussed_result.png"  # Replace with your path to PNG A
image_b_path = r"C:\Users\richy\Documents\Git\HITS\Results images\nonconcussed_result.png"  # Replace with your path to PNG B
output_path = r"C:\Users\richy\Documents\Git\HITS\Results images\hits_result_probability.png"  # Path where you want to save the new image

probability_hits_result(input_number, image_a_path, image_b_path, output_path)
