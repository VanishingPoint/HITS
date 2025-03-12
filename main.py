from nicegui import ui
import csv

# Store the current page in a container
content = ui.column().classes('p-4')

# Function to load a new page
def load_page(page_function):
    """Clear current content and load a new page."""
    content.clear()
    with content:
        page_function()

# Save user info to CSV
def save_user_info(name, gender, filename="user_data.csv"):
    """Append user information to a CSV file."""
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, gender])

# ====================== MAIN MENU ======================
def main_menu():
    """Main menu page."""
    ui.label("Welcome to HITS Testing Suite").classes('text-2xl font-bold')
    ui.image("assets/main_menu.png").classes("w-64 h-auto")  # Replace with actual image path

    ui.button("Enter User Info", on_click=lambda: load_page(user_info)).classes("text-lg")
    ui.button("Start Tests", on_click=lambda: load_page(test_1)).classes("text-lg")

# ====================== USER INFO PAGE ======================
def user_info():
    """User information entry page."""
    ui.label("Enter Your Information").classes('text-2xl font-bold')

    name = ui.input("Participant's Full Name").classes("w-64")
    sex = ui.radio(["Male", "Female", "Other"], value="Other").classes("w-64")
    age = ui.input("Participant's Age").classes("w-64")
    height = ui.input("Participant's Height [cm]").classes("w-64")
    with ui.dropdown_button('Sport', auto_close=True):
        ui.item('Soccer', on_click=lambda: ui.notify('You selected Soccer'))
        ui.item('Hockey', on_click=lambda: ui.notify('You selected Hockey'))
        ui.item('Football', on_click=lambda: ui.notify('You selected Football'))
        ui.item('Rugby', on_click=lambda: ui.notify('Rugby'))

    def submit():
        save_user_info(name.value, sex.value, age.value, height.value)
        ui.notify("User Info Saved!", color="green")
        load_page(test_1)  # Automatically go to the first test after saving

    ui.button("Save and Continue", on_click=submit).classes("text-lg bg-blue-500 text-white p-2 rounded-lg")
    ui.button("Back to Main Menu", on_click=lambda: load_page(main_menu)).classes("text-lg")


# ====================== TEST PAGES ======================
def test_1():
    """Test 1: Stroop Test"""
    ui.label("Test 1: Stroop Test").classes("text-2xl font-bold")
    ui.image("assets/test1.png").classes("w-64 h-auto")  # Replace with actual image
    ui.label("Read the color, not the word!").classes("text-lg")

    ui.button("Next Test", on_click=lambda: load_page(test_2)).classes("text-lg")
    ui.button("Back to Main Menu", on_click=lambda: load_page(main_menu)).classes("text-lg")

def test_2():
    """Test 2: Reaction Time"""
    ui.label("Test 2: Reaction Time Test").classes("text-2xl font-bold")
    ui.image("assets/test2.png").classes("w-64 h-auto")  # Replace with actual image
    ui.label("Press the button as fast as possible when the color changes!").classes("text-lg")

    ui.button("Next Test", on_click=lambda: load_page(test_3)).classes("text-lg")
    ui.button("Back to Test 1", on_click=lambda: load_page(test_1)).classes("text-lg")

def test_3():
    """Test 3: Memory Test"""
    ui.label("Test 3: Memory Test").classes("text-2xl font-bold")
    ui.image("assets/test3.png").classes("w-64 h-auto")  # Replace with actual image
    ui.label("Remember the sequence of numbers!").classes("text-lg")

    ui.button("Next Test", on_click=lambda: load_page(test_4)).classes("text-lg")
    ui.button("Back to Test 2", on_click=lambda: load_page(test_2)).classes("text-lg")

def test_4():
    """Test 4: Spatial Awareness Test"""
    ui.label("Test 4: Spatial Awareness Test").classes("text-2xl font-bold")
    ui.image("assets/test4.png").classes("w-64 h-auto")  # Replace with actual image
    ui.label("Click the correct position based on the prompt!").classes("text-lg")

    ui.button("Finish & Return to Main Menu", on_click=lambda: load_page(main_menu)).classes("text-lg")
    ui.button("Back to Test 3", on_click=lambda: load_page(test_3)).classes("text-lg")

# ====================== RUNNING THE APP ======================
load_page(main_menu)  # Start with the main menu
ui.run()
