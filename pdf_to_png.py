from pdf2image import convert_from_path

# Naming conventions: 
# Cognitive Proctor Images = cognitive_page_#.png
# Cognitive Participant Images = page_#.png
# Balance Proctor Images = balance_page_#.png
# Eye Tracking Proctor Images = eyetrackingproctor_#.png
# Eye Tracking Participant Images = eyetracking_page#.png
# Main Menu Proctor Images = menu_#.png

# Specify the path to your PDF and Poppler's bin folder

pdf_path = r"C:\Users\chane\Downloads\Balance Proctor Images.pdf"

poppler_path = r"C:\Users\chane\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"

# Convert PDF to images
images = convert_from_path(pdf_path, dpi=500, poppler_path=poppler_path)

# Save each page as a separate PNG file

output_folder = r'C:\Users\chane\Desktop\HITS\HITS\Balance Proctor Images'
for i, image in enumerate(images, start=0):
    image.save(f'{output_folder}/balance_page_{i}.png', 'PNG')

print("Conversion complete!")