from pathlib import Path
from nicegui import app, ui
from nicegui.events import KeyEventArguments

# Set up the folder containing images
folder = Path(r"C:\Users\chane\Desktop\HITS\HITS\Main Menu Proctor Images")
files = sorted(f.name for f in folder.glob('menu_*.png'))

# Set initial state
state = {'index': 0}

# Create a container to hold the dynamically updated UI
main_frame = ui.row().classes("w-full justify-center items-center")

# Function to update UI when image changes
def update_image():
    main_frame.clear()  # Clears everything inside the frame

    with main_frame:
        with ui.card().classes("p-4"):
            ui.image(f'/images/{files[state["index"]]}').classes("max-w-full").style("max-width: 500px; max-height: 500px;")

            # Reset user input fields
            name_input = ui.input("Name").classes('w-full')
            email_input = ui.input("Email").classes('w-full')

            # Navigation buttons
            with ui.row().classes("justify-between w-full"):
                ui.button("Back", on_click=previous_image).classes('w-1/3 sm:w-auto')
                ui.button("Next", on_click=next_image).classes('w-1/3 sm:w-auto')

            # Test message
            test_label = ui.label("").classes("text-center text-lg font-bold")
            trigger_test(test_label)

# Navigation functions
def next_image():
    if state['index'] < len(files) - 1:
        state['index'] += 1
        update_image()

def previous_image():
    if state['index'] > 0:
        state['index'] -= 1
        update_image()

# Run the corresponding test based on the image index
def trigger_test(label):
    tests = {
        1: "Running Test 1 (COGNITIVE)...",
        2: "Running Test 2...",
        3: "Running Test 3...",
        4: "Running Test 4..."
    }
    if state['index'] in tests:
        label.set_text(tests[state['index']])
        ui.notify(tests[state['index']])

# Serve images from the 'images' folder
app.add_static_files('/images', folder)

# Set up keyboard navigation
def handle_key(event: KeyEventArguments) -> None:
    if event.action.keydown:
        if event.key.arrow_right:
            next_image()
        elif event.key.arrow_left:
            previous_image()

ui.keyboard(on_key=handle_key)

# Initialize UI
update_image()

# Start the app
ui.run()
