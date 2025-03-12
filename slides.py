#!/usr/bin/env python3
from pathlib import Path
from nicegui import app, ui
from nicegui.events import KeyEventArguments

ui.query('.nicegui-content').classes('p-0')  # remove padding from the main content

folder = Path(r"C:\Users\chane\Downloads\slides").parent / 'slides'  # image source: https://pixabay.com/
files = sorted(f.name for f in folder.glob('*.jpg'))
state = {'index': 0}

# Function to handle key events
def handle_key(event: KeyEventArguments) -> None:
    if event.action.keydown:
        if event.key.arrow_right:
            state['index'] += 1
        if event.key.arrow_left:
            state['index'] -= 1
        state['index'] %= len(files)
        slide.set_source(f'slides/{files[state["index"]]}')
        update_buttons_position()

# Function to update button positions (example positions)
def update_buttons_position():
    button_1.style('position: absolute; top: 10%; left: 20%;')  # button 1 position
    button_2.style('position: absolute; top: 60%; left: 30%;')  # button 2 position

app.add_static_files('/slides', folder)  # serve all files in this folder

# Initial image display
slide = ui.image(f'slides/{files[state["index"]]}')

# Add buttons with specific positions
button_1 = ui.button('Button 1', on_click=lambda: print("Button 1 clicked"))
button_2 = ui.button('Button 2', on_click=lambda: print("Button 2 clicked"))

# Apply initial positions
update_buttons_position()

# Keyboard event handling
ui.keyboard(on_key=handle_key)

# Run the app
ui.run()
