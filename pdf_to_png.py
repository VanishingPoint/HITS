from pdf2image import convert_from_path

# Specify the path to your PDF and Poppler's bin folder
# pdf_path = r"C:\Users\chane\Documents\UI\Balance Proctor UI\ProctorUI_Balance.pdf"
# pdf_path = r"C:\Users\chane\Documents\UI\Cognitive Proctor UI\ProctorUI_Cognitive.pdf"
pdf_path = r"C:\Users\chane\Documents\UI\Main Menu Proctor UI\ProctorUI_Main.pdf"
poppler_path = r"C:\Users\chane\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"

# Convert PDF to images
images = convert_from_path(pdf_path, dpi=500, poppler_path=poppler_path)

# Save each page as a separate PNG file
# output_folder = r'C:\Users\chane\Documents\UI\Balance Proctor UI'
# output_folder = r'C:\Users\chane\Documents\UI\Cognitive Proctor UI'
output_folder = r'C:\Users\chane\Documents\UI\Main Menu Proctor UI'
for i, image in enumerate(images, start=0):
    image.save(f'{output_folder}/main_menu_{i}.png', 'PNG')

print("Conversion complete!")