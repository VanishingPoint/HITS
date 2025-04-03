from PIL import Image

def hits_combined_result(base_image_path, overlay_image_path, output_path, position=(2550, 770)):
    # Open the base and overlay images
    base_image = Image.open(base_image_path).convert("RGBA")
    overlay_image = Image.open(overlay_image_path).convert("RGBA")
    
    # Create a new image for the result
    combined = Image.new("RGBA", base_image.size)
    
    scale_factor = 1.2

    # Resize overlay while maintaining aspect ratio
    overlay_width = int(overlay_image.width * scale_factor)
    overlay_height = int(overlay_image.height * scale_factor)
    overlay_image = overlay_image.resize((overlay_width, overlay_height), Image.LANCZOS)

    # Create a new image for the result
    combined = Image.new("RGBA", base_image.size)

    # Paste the base image first
    combined.paste(base_image, (0, 0))
    
    # Paste the overlay image on top, preserving transparency
    combined.paste(overlay_image, position, overlay_image)
    
    # Save the final image
    combined.save(output_path, format="PNG")
    print(f"Overlayed image saved as {output_path}")

# Example usage:
hits_combined_result(r"C:\Users\richy\Documents\Git\HITS\Results images\hits_result_chart.png", r"C:\Users\richy\Documents\Git\HITS\Results images\hits_result_probability.png", r"C:\Users\richy\Documents\Git\HITS\Results images\hits_result_combined.png")
