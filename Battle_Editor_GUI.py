import tkinter as tk
from tkinter import ttk
import os
import struct
import re
from PIL import Image, ImageTk


images_directory = r"ffx_enemy_images"
meta_lines = 0


def parse_meta_sections(file_path):
    try:
        global meta_lines
        with open(file_path, "rb") as f:
            f.seek(0x10)
            
            # Read the 4-byte little endian pointer
            pointer_data = f.read(4)
            if len(pointer_data) < 4:
                raise ValueError("Failed to read pointer at offset 0x10. File might be incomplete.")
            pointer_to_meta = struct.unpack("<I", pointer_data)[0]
            
            f.seek(pointer_to_meta)
            
            # Read the 2nd single byte to get the number of meta sections
            f.seek(pointer_to_meta + 1)
            num_meta_byte = f.read(1)
            if len(num_meta_byte) < 1:
                raise ValueError("Failed to read the number of meta sections.")
            num_meta_sections = struct.unpack("<B", num_meta_byte)[0]
            
            # Store lines 2 and 3 of each section
            meta_lines = []  # Array to store the desired lines
            
            for i in range(num_meta_sections):
                meta_start = pointer_to_meta + (i * (6 * 16))
                
                for j in range(6):
                    f.seek(meta_start + (j * 16))
                    line = f.read(16)
                    if len(line) < 16:
                        raise ValueError(f"Failed to read full line of meta section {i + 1}, line {j + 1}.")
                    
                    # Store lines 2 and 3
                    if j == 1 or j == 2:  # Line 2 and Line 3 correspond to index 1 and 2
                        # Convert line data to a string without spaces and append to the array
                        meta_lines.append("".join(f"{byte:02X}" for byte in line))
            
            # Print or process the array of strings
            print(f"Lines 2 and 3 of each meta section (no spaces): {meta_lines}\n")
            
    except Exception as e:
        print(f"Error: {e}")


def from_little_endian_array(input_array):
    all_results = []
    
    for input_str in input_array:
        if len(input_str) % 8 != 0:
            raise ValueError("Input string length must be a multiple of 8.")
        
        result = []
        
        for i in range(0, len(input_str), 8):
            # Extract 8-character chunk
            chunk = input_str[i:i+8]
            
            # Convert to little-endian bytes
            little_endian_bytes = bytes.fromhex(chunk)
            
            # Interpret as little-endian 4-byte integer
            integer_value = int.from_bytes(little_endian_bytes, byteorder="little")
            
            result.append(integer_value)
        
        all_results.append(result)
    
    return all_results


def to_little_endian_hex_array(array_of_int_arrays):
    hex_strings = []
    
    for int_array in array_of_int_arrays:
        result = ""
        for num in int_array:
            # Convert integer to 4-byte little-endian
            little_endian_bytes = num.to_bytes(4, byteorder="little")
            # Convert bytes to uppercase hex string without spaces
            hex_string = little_endian_bytes.hex().upper()
            result += hex_string
        # Append the resulting hex string for this inner array
        hex_strings.append(result)
    
    return hex_strings


def replace_strings_in_text(array1, array2, large_text):
    # Ensure the arrays are of the same length
    if len(array1) != len(array2):
        raise ValueError("The two arrays must have the same length.")
    
    # Replace strings in the text
    for old_string, new_string in zip(array1, array2):
        large_text = large_text.replace(old_string, new_string)
    
    return large_text


def floats_to_single_float32_string(arr):
    return ''.join(struct.pack('<f', num).hex() for num in arr)

def text_to_array_of_numbers(text):

    global P_str, p_str, A_str, M_str, m_str
    numbers = []
    counts = {"P": 0, "p": 0, "A": 0, "M": 0, "m": 0}

    lines = text.split("\n")
    for line in lines:
        match = re.match(r"([PpAMm])\d+: \(([-\d]+), ([-\d]+), ([-\d]+), ([-\d]+)\)", line)
        if match:
            letter = match.group(1)
            counts[letter] += 1
            for i in range(2, 6):  # Groups 2 to 5 are the numbers
                num = int(match.group(i))
                if (i - 2) % 4 == 0 or (i - 2) % 4 == 2:  # 1st and 3rd of 4 elements
                    num = (num - 200) / 1.5
                numbers.append(num)

    print("Character counts:", counts)

    # Split the array into sub-arrays based on counts
    sub_arrays = []
    start_idx = 0

    for letter in "PpAMm":
        count = counts[letter]
        end_idx = start_idx + count * 4
        sub_arrays.append(numbers[start_idx:end_idx])
        start_idx = end_idx
    
    P_str = floats_to_single_float32_string(sub_arrays[0])
    p_str = floats_to_single_float32_string(sub_arrays[1])
    A_str = floats_to_single_float32_string(sub_arrays[2])
    M_str = floats_to_single_float32_string(sub_arrays[3])
    m_str = floats_to_single_float32_string(sub_arrays[4])

    print(P_str)
    print(p_str)
    print(A_str)
    print(M_str)
    print(m_str)    





def load_image(option_menu, label):
    selected_image = option_menu.get()
    image_path_jpg = os.path.join(images_directory, f"{selected_image}.jpg")
    image_path_png = os.path.join(images_directory, f"{selected_image}.png")

    if os.path.exists(image_path_jpg):
        image_path = image_path_jpg
    elif os.path.exists(image_path_png):
        image_path = image_path_png
    else:
        image_path = None

    if image_path:
        img = Image.open(image_path)
        img = img.resize((100, 100))  # Adjust the size as needed
        img_tk = ImageTk.PhotoImage(img)
        label.config(image=img_tk)
        label.image = img_tk
    else:
        label.config(image='')
        label.image = None

def bytes_to_ints(byte_string):
    byte_string = byte_string.replace(" ", "")
    byte_data = bytes.fromhex(byte_string)
    float_array = struct.unpack('<' + 'f' * (len(byte_data) // 4), byte_data)
    int_array = [int(round(f*1.5)) for f in float_array]                 #####         ########## HELP!!!!!    ######## #######       #########
    modified_array = [val + 200 if i % 2 == 0 else val for i, val in enumerate(int_array)]
    return modified_array

# Function to search for .bin files in subfolders and return their names and full paths
def get_bin_files(directory):
    bin_files = []
    file_names = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".bin"):
                full_path = os.path.join(root, file)
                bin_files.append(full_path)
                file_names.append(file)
    return file_names, bin_files

# Function to handle the dropdown selection
def on_select(event, dropdown_number):
    selected_value = dropdowns[dropdown_number].get()
    hex_labels[dropdown_number].config(text=f"HexCode: {hex_codes.get(selected_value, '')}", font=("Arial", 8), fg="black")

def clear_canvas():
    canvas.delete("all")
    dots.clear()

old_section  = ""
section1 = ""
section2 = ""
section3 = ""
section4 = ""
section5 = ""

new_section  = ""
P_str = ""
p_str = ""
A_str = ""
M_str = ""
m_str = ""

# Function to load the selected file and print 12 bytes from the pointer location and the 16 bytes after
def load_file():
    global old_section, section1, section2, section3, section4, section5
    global new_section, P_str, p_str, A_str, M_str, m_str 
    
    clear_canvas()
    
    selected_file = display_file_dropdown.get()
    if selected_file == "<None>":
        return

    selected_file_path = file_name_to_path.get(selected_file, "")
    with open(selected_file_path, "rb") as f:
        f.seek(0x0C)
        pointer_bytes = f.read(4)
        pointer = struct.unpack("<I", pointer_bytes)[0]  ###Unpacks the 4 byter Indian pointer into a decimal

        f.seek(pointer)
        data_bytes = f.read(12)      ##The 12 preceding bytes before monster
        additional_bytes = f.read(16)    ## The monster's allocated to battle

        chunked_bytes = [additional_bytes[i:i+2] for i in range(0, len(additional_bytes), 2)]

        for i, chunk in enumerate(chunked_bytes):
            hex_str = "".join(f"{byte:02X}" for byte in chunk)
            matching_option = next((option for option, code in hex_codes.items() if code == hex_str), None)

            if matching_option:
                dropdowns[i].set(matching_option)
            else:
                dropdowns[i].set("<None>")

        print("".join(f"{byte:02X}" for byte in data_bytes))
        print("".join(f"{byte:02X}" for byte in additional_bytes))

        f.seek(0x10)
        second_pointer_bytes = f.read(4)        #Grabs the 4 bytes from that point
        second_pointer = struct.unpack("<I", second_pointer_bytes)[0]  #Turns them into a integer pointerUknwn
        print(f"Second Pointer: {second_pointer:08X}")

        f.seek(second_pointer)
        second_pointer_data = f.read(16)
        print(second_pointer_data)
        print("".join(f"{byte:02X}" for byte in second_pointer_data))

        # Calculate section lengths
        f.seek(second_pointer + 4)
        fifth_sixth_seventh_bytes = f.read(3)
        section1_length = fifth_sixth_seventh_bytes[0] * 16
        section2_length = fifth_sixth_seventh_bytes[0] * 16
        section3_length = fifth_sixth_seventh_bytes[1] * 16
        section4_length = fifth_sixth_seventh_bytes[2] * 16
        section5_length = fifth_sixth_seventh_bytes[2] * 16

        f.seek(second_pointer+16)
        dummy = f.read(4)
        dummy = struct.unpack("<I", dummy)[0]

        # Read and store sections
        f.seek(second_pointer + dummy)
        section1 = f.read(section1_length).hex().upper()
        section2 = f.read(section2_length).hex().upper()
        section3 = f.read(section3_length).hex().upper()##Aeons

        
        f.seek(second_pointer+32)
        dummy = f.read(4)
        dummy = struct.unpack("<I", dummy)[0]
        f.seek(second_pointer + dummy)
        section4 = f.read(section4_length).hex().upper()
        section5 = f.read(section5_length).hex().upper()
        
        old_section = fifth_sixth_seventh_bytes
        new_section = old_section
        P_str = section1
        p_str = section2
        A_str = section3
        M_str = section4
        m_str = section5

        # Print the sections
        print("Section 1: " + section1)
        print("Section 2: " + section2)
        print("Section 3: " + section3)
        print("Section 4: " + section4)
        print("Section 5: " + section5)
        process_and_create_dots(canvas, P_str, p_str, A_str, M_str, m_str)
        for i in range(8):
            dropdowns[i].event_generate("<<ComboboxSelected>>")
        

root = tk.Tk()
root.title("Selectable Drop Down Box")
root.geometry("1300x825")  # Increased width
root.resizable(False, False)  # Disable resizing

show_orange_only = tk.BooleanVar(value=False)  # Unchecked by default

def toggle_dots():
    for dot in dots:
        if show_orange_only.get():
            if dot.color == "orange":
                dot.show()
            else:
                dot.hide()
        else:
            if dot.color != "orange":
                dot.show()
            else:
                dot.hide()

    if show_orange_only.get():
        canvas.delete("line")  # Delete all lines when checkbox is checked
    else:
        check_and_draw_lines()  # Call draw lines function when checkbox is unchecked



def save_file():    
    selected_file = display_file_dropdown.get()
    if selected_file == "<None>":
        return

    # Find the full path of the selected file
    selected_file_path = file_name_to_path.get(selected_file, "")
    with open(selected_file_path, "r+b") as f:
        #########################################
        global new_section
        f.seek(0x10)
        pb_ = f.read(4)
        offset = struct.unpack("<I", pb_)[0]   ##### Changes the Position Number amount!
        f.seek(offset)
        f.seek(6, 1)
        f.write(bytes([new_section[2]]))
        #########################################
        f.seek(0x0C)
        pointer_bytes = f.read(4)
        pointer = struct.unpack("<I", pointer_bytes)[0]

        f.seek(pointer)
        section_bytes = bytearray(f.read(28))

        for i, dropdown in enumerate(dropdowns):
            selected_value = dropdown.get()
            if selected_value != "<None>":
                replacement_bytes = bytes.fromhex(hex_codes[selected_value])
                section_bytes[i*2+12:(i*2)+14] = replacement_bytes

        # Write back the modified section
        f.seek(pointer)
        f.write(section_bytes)
    text_to_array_of_numbers(coords_text.get("1.0", tk.END))
    print("File saved successfully!")
    
    global old_section, section1, section2, section3, section4, section5
    global P_str, p_str, A_str, M_str, m_str
    
    with open(selected_file_path, 'rb') as file:
        binary_content = file.read()
    hex_content = binary_content.hex().upper()
    hex_content = hex_content.replace(section1, P_str)
    hex_content = hex_content.replace(section2, p_str)
    hex_content = hex_content.replace(section3, A_str)
    hex_content = hex_content.replace(section4, M_str)
    hex_content = hex_content.replace(section5, m_str)

    parse_meta_sections(selected_file_path)
    k = from_little_endian_array(meta_lines)
    m = len(M_str) - len(section4) ###Note:!!!Set the strings equal all at end
    k = [[num + m if num > k[1][0] else num for num in row] for row in k]
    k[1][1] = int(k[1][1] - m/2)
    k = to_little_endian_hex_array(k)
    hex_content = replace_strings_in_text(meta_lines, k, hex_content)
    hex_content = bytes.fromhex(hex_content)
    
    with open(selected_file_path, 'wb') as file:
        file.write(hex_content)
    
    section1 = P_str
    section2 = p_str
    section3 = A_str
    section4 = M_str
    section5 = m_str




class DraggableDot:
    def __init__(self, canvas, x, y, z, w, color, label, dot_size):
        self.canvas = canvas
        self.dot = canvas.create_oval(x-dot_size, z-dot_size, x+dot_size, z+dot_size, fill=color, outline=color)
        self.label = canvas.create_text(x, z, text=label, fill="white")
        self.label_text = label
        self.x = x
        self.y = y
        self.z = z
        self.w = w
        self.color = color
        self.dot_size = dot_size
        self.canvas.tag_bind(self.dot, "<Button-1>", self.on_click)
        self.canvas.tag_bind(self.dot, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(self.label, "<Button-1>", self.on_click)
        self.canvas.tag_bind(self.label, "<B1-Motion>", self.on_drag)
    
    def hide(self):
        self.canvas.itemconfigure(self.dot, state='hidden')
        self.canvas.itemconfigure(self.label, state='hidden')

    def show(self):
        self.canvas.itemconfigure(self.dot, state='normal')
        self.canvas.itemconfigure(self.label, state='normal')

    def on_click(self, event):
        global last_clicked_dot
        last_clicked_dot = self
        self.x = event.x
        self.z = event.y
        self.update_coordinates()

    def on_drag(self, event):
        dx = event.x - self.x
        dz = event.y - self.z
        self.canvas.move(self.dot, dx, dz)
        self.canvas.move(self.label, dx, dz)
        self.x = event.x
        self.z = event.y
        self.update_coordinates()
        update_coordinates_text()
        if not show_orange_only.get():
            check_and_draw_lines()

    def update_coordinates(self):
        coords_label_var.set(f"{self.color} {self.label_text}: ({self.x}, {self.y}, {self.z}, {self.w})")

class CoordinateManager:
    def __init__(self):
        self.coordinates = {}

    def add_coordinates(self, label, coords):
        self.coordinates[label] = coords

    def get_coordinates(self, label):
        return self.coordinates.get(label, (0, 0, 0, 0))

coordinate_manager = CoordinateManager()

orange_lines = []

def create_dots(canvas, coordinates, color, name_prefix, dot_size):
    for index, (x, y, z, w) in enumerate(zip(*[iter(coordinates)]*4)):
        create_dot(canvas, x, y, z, w, color, f"{name_prefix}{index+1}", dot_size)

def create_dot(canvas, x, y, z, w, color, label, dot_size):
    dot = DraggableDot(canvas, x, y, z, w, color, label, dot_size)
    dots.append(dot)
    coordinate_manager.add_coordinates(label, (x, y, z, w))
    update_coordinates_text()
    
    # Ensure orange dots are hidden initially
    if color == "orange" and not show_orange_only.get():
        dot.hide()

def update_coordinates_text():
    coords_text.delete("1.0", tk.END)
    for dot in dots:
        coords_text.insert(tk.END, f"{dot.label_text}: ({dot.x}, {dot.y}, {dot.z}, {dot.w})\n")

def check_and_draw_lines():
    global orange_lines
    canvas.delete("line")
    orange_lines.clear()  # Clear the list of orange lines

    if coords_text.get("1.0", tk.END).strip():
        lines = coords_text.get("1.0", tk.END).strip().split("\n")
        p_coords, m_coords = [], []

        for line in lines:
            label, coord_str = line.split(": ")
            coords = tuple(map(int, coord_str.strip("()").split(", ")))
            if label.startswith("P") or label.startswith("M"):
                p_coords.append(coords)
            elif label.startswith("p") or label.startswith("m"):
                m_coords.append(coords)

        min_length = min(len(p_coords), len(m_coords))
        for i in range(min_length):
            p_x, p_y, p_z, p_w = p_coords[i]
            m_x, m_y, m_z, m_w = m_coords[i]
            line = canvas.create_line(p_x, p_z, m_x, m_z, fill="grey", dash=(4, 4), tags="line")

            for dot in dots:
                if dot.color == "orange" and (dot.x == m_x and dot.z == m_z):
                    orange_lines.append(line)  # Add to the list of orange lines
                    break

    # Hide orange lines if the checkbox is checked
    if show_orange_only.get():
        for line in orange_lines:
            canvas.itemconfigure(line, state="hidden")

def update_y_from_slider(value):
    if last_clicked_dot is not None:
        last_clicked_dot.y = int(value)
        last_clicked_dot.update_coordinates()
        update_coordinates_text()
        #check_and_draw_lines()

def on_button_click():
    global M_str, m_str, new_section
    text_to_array_of_numbers(coords_text.get("1.0", tk.END))
    clear_canvas()
    M_str += "00000000000000000000000000000000"
    m_str += "00000000000000000000000000000000"
    process_and_create_dots(canvas, P_str, p_str, A_str, M_str, m_str)
    
    byte_list = list(new_section)
    byte_list[2] = (byte_list[2] + 1) % 256
    new_section = bytes(byte_list)

                     
# Create a dropdown in the upper left
display_file_label = tk.Label(root, text="Display File", font=("Arial", 10, "bold"))
display_file_label.pack(anchor="nw", padx=10, pady=10)



# Get all .bin files in the "MonsterBattle_scripts" folder and its subfolders
file_names, file_paths = get_bin_files("MonsterBattle_scripts")
display_file_options = ["<None>"] + file_names



display_file_dropdown = ttk.Combobox(root, values=display_file_options)
display_file_dropdown.set("<None>")  # Set <None> as default
display_file_dropdown.pack(anchor="nw", padx=10)

# Map file names to their full paths
file_name_to_path = dict(zip(file_names, file_paths))

# Add "Load File" button underneath the Display File dropdown with bigger size and bold text
load_file_button = tk.Button(root, text="Load File", font=("Arial", 12), width=15, height=1, command=load_file)
load_file_button.pack(anchor="nw", padx=10, pady=10)

# Add "Save" button to save the modified file
save_button = tk.Button(root, text="SAVE", font=("Arial", 12), width=15, height=1, command=save_file)
save_button.pack(anchor="nw", padx=10, pady=(10, 0))  # Move the Save button closer

# Create a container frame to hold all dropdowns
container = tk.Frame(root)
container.pack()

# Define the list of options
options = ['(None)', 'Monster 0', 'Raldo', 'Bunyip', 'Murussu', 'Mafdet', 'Shred', 'Gandarewa', 'Aerouge', 'Imp', 'Dingo', "Mi'ihen Fang", 'Garm', 'Snow Wolf', 'Sand Wolf', 'Skoll', 'Bandersnatch', 'Water Flan', 'Thunder Flan', 'Snow Flan', 'Ice Flan', 'Flame Flan', 'Dark Flan', 'Dinonix', 'Ipiria', 'Raptor', 'Melusine', 'Iguion', 'Yowie', 'Condor', 'Simurgh', 'Alcyone', 'Killer Bee', 'Bite Bug', 'Wasp', 'Nebiros', 'Floating Eye', 'Buer', 'Evil Eye', 'Ahriman', 'Ragora', 'Ragora 2', 'Sahagin', 'Sahagin 2', 'Sahagin 3', 'Garuda', 'Zu', 'Sand Worm', 'Land Worm', 'Defender', 'Defender Z', 'Ghost', 'Phlegyas', 'Achelous', 'Remora', 'Maelspike', 'Dual Horn', 'Valaha', 'Grendel', 'Octopus', 'Vouivre', 'Lamashtu', 'Kusariqqu', 'Mushussu', 'Nidhogg', 'Malboro', 'Great Malboro', 'Ogre', 'Bashura', 'Piranha', 'Piranha 2', 'Piranha 3', 'Splasher', 'Splasher 2', 'Splasher 3', 'Vepar', 'Vepar 2', 'Vepar 3', 'Yellow Element', 'White Element', 'Red Element', 'Gold Element', 'Blue Element', 'Dark Element', 'Black Element', 'Epaaj', 'Behemoth', 'Behemoth King', 'Chimera', 'Chimera Brain', 'Coeurl', 'Master Coeurl', 'Mech Guard', 'Mech Scouter', 'Mech Scouter 2', 'Mech Leader', 'Demonolith', 'Mech Gunner', 'Mech Hunter', 'Mech Defender', 'Ultima Weapon', 'Omega Weapon', 'Tros', 'Sinspawn Geneaux', "Geneaux's Tentacle", 'Chocobo Eater', 'Neslug', 'Mortiphasm', 'Sinscale', 'Sinscale 2', 'Geosgaeno', 'Oblitzerator', 'Extractor', 'Uknwn', 'Sin', 'Sinspawn Echuilles', 'Sinscale 3', 'Sinscale 4', 'Sinspawn Gui', 'Mortiphasm 2', 'Evrae', 'Evrae Altana', 'Spherimorph', 'Crawler', 'Negator', 'Seymour', 'Anima', 'Seymour Natus', 'Mortibody', 'Sanctuary Keeper', 'Spectral Keeper', 'Yunalesca', 'Seymour Omnis', "Braska's Final Aeon", 'Crane', 'Biran Ronso', 'Yenke Ronso', 'Left Fin', 'Right Fin', 'Sin 2', 'Sinspawn Genais', 'Sin 3', 'Guado Guardian', 'Seymour Flux', 'Mortiorchis', 'Kimahri Weapon', 'Sinscale 5', 'Circle', 'Sinscale 6', 'Sinscale 7', 'Cid', 'Mortiphasm 3', 'Vouivre 2', 'Worker', 'Lord Ochu', 'Mortiphasm 4', 'Sahagin 4', 'Sahagin Chief', 'Garuda 2', 'Klikk', 'Sinspawn Ammes', 'Head', 'Arm', 'Gate Lock', '{PC08:VALEFOR}', '{PC09:IFRIT}', '{PC0A:IXION}', '{PC0B:SHIVA}', '{PC0C:BAHAMUT}', '{PC0D:ANIMA}', '{PC0E:YOJIMBO}', 'Tanker', 'Gate Lock 2', 'Monster 172', 'Yu Pagoda', 'Yu Pagoda 2', 'Tentacle', 'Yu Yevon', 'Mortiphasm 5', 'Cindy', 'Sandy', 'Mindy', 'Iron Giant', 'Gemini', 'Gemini 2', 'Gemini 3', 'Basilisk', 'Anacondaur', 'Adamantoise', 'Varuna', 'Ochu', 'Mandragora', 'YAT-99', 'YAT-97', 'Bomb', 'Grenade', 'YKT-63', 'YKT-11', 'Warrior Monk', 'Fallen Monk', 'Warrior Monk 2', 'Fallen Monk 2', 'PuPu', 'Magic Urn', 'Magic Urn 2', 'Magic Urn 3', 'Magic Urn 4', 'Magic Urn 5', 'Qactuar', 'Cactuar', 'Larva', 'Barbatos', 'Uknwn 2', 'Wendigo', 'Guado Guardian 2', 'Funguar', 'Thorn', 'Exoray', 'Xiphos', 'Puroboros', 'Spirit', 'Wraith', 'Sandragora', 'Guado Guardian 3', 'Tonberry', 'Master Tonberry', 'Evil Eye 2', 'Bomb 2', 'Chimera 2', 'Dual Horn 2', 'Defender X', 'Garuda 3', 'Dingo 2', 'Water Flan 2', 'Condor 2', 'Ragora 2', 'Raldo 2', 'Bunyip 2', 'Uknwn 3', 'Zu 2', 'Zaurus', 'Halma', 'Aqua Flan', 'Floating Death', 'Maze Larva', 'Machea', 'Cave Iguion', 'Swamp Mafdet', 'Bat Eye', 'Isaaru', 'Mira', 'Belgemine', 'Mimic', 'Mimic 2', 'Mimic 3', 'Valefor', 'Dummy', 'Mimic 4', 'Mimic Parts', 'Valefor 2', 'Ifrit', 'Mimic Parts 2', 'Mimic Parts 3', 'Mimic Parts 4', 'Rifle', 'Fire Rifle', 'Anima 2', 'Koma Inu', 'Anima 3', 'Anima 4', 'Katana', 'Kozuka', 'Shuriken', 'Head 2', 'Arm 2', 'Nishida', 'Sword', 'Nemesis', 'Catastrophe', 'None', 'Earth Eater', 'Ultima Buster', 'Greater Sphere', "Th'uban", 'Shinryu', 'Ifrit 2', 'Ixion', 'Shiva', 'Bahamut', 'Yojimbo', 'Sandy 2', 'Cindy 2', 'Mindy 2', 'Tanket', 'Vidatu', 'Fenrir', 'Jumbo Flan', 'Ornitholestes', 'Pteryx', 'Hornet', 'One-Eye', 'Stratoavis', 'Abyss Worm', 'Juggernaut', 'Fafnir', 'Malboro Menace', 'Kottos', 'Nega Elemental', 'Catoblepas', 'Chimerageist', 'Coeurlregina', 'Ironclad', 'Jormungand', 'Abaddon', 'Bomb King', 'Cactuar King', 'Vorban', 'Sleep Sprout', 'Don Tonberry', 'Espada', 'Bomb 3', 'Dual Horn 3', 'Vulture', 'Basilisk 2', 'Ochu 2', 'Larva 2', 'Iron Giant 2', 'Chimera 3', 'Monster 84', 'Qactuar 2', 'Zu 3', 'Sand Worm 2', 'Ghost 2', 'Malboro 2', 'Bashura 2', 'Dark Valefor', 'Dark Ifrit', 'Dark Ixion', 'Dark Shiva', 'Dark Bahamut', 'Dark Anima', 'Dark Yojimbo', 'Dark Cindy', 'Dark Sandy', 'Dark Mindy', 'Penance', 'Right Arm', 'Left Arm', 'Unknown', 'Unknown 2', 'Unknown 3', 'Unknown 4', 'Unknown 5', 'Unknown 6', 'Unknown 7', 'Unknown 8', 'Unknown 9', 'Unknown 10', '-', '- 2', '- 3', '- 4']
# Define the corresponding hex codes
hex_codes = {'(None)': 'FFFF', 'Monster 0': '0010', 'Raldo': '0110', 'Bunyip': '0210', 'Murussu': '0310', 'Mafdet': '0410', 'Shred': '0510', 'Gandarewa': '0610', 'Aerouge': '0710', 'Imp': '0810', 'Dingo': '0910', "Mi'ihen Fang": '0A10', 'Garm': '0B10', 'Snow Wolf': '0C10', 'Sand Wolf': '0D10', 'Skoll': '0E10', 'Bandersnatch': '0F10', 'Water Flan': '1010', 'Thunder Flan': '1110', 'Snow Flan': '1210', 'Ice Flan': '1310', 'Flame Flan': '1410', 'Dark Flan': '1510', 'Dinonix': '1610', 'Ipiria': '1710', 'Raptor': '1810', 'Melusine': '1910', 'Iguion': '1A10', 'Yowie': '1B10', 'Condor': '1C10', 'Simurgh': '1D10', 'Alcyone': '1E10', 'Killer Bee': '1F10', 'Bite Bug': '2010', 'Wasp': '2110', 'Nebiros': '2210', 'Floating Eye': '2310', 'Buer': '2410', 'Evil Eye': '2510', 'Ahriman': '2610', 'Ragora': '2710', 'Ragora 2': '2810', 'Sahagin': '2910', 'Sahagin 2': '2A10', 'Sahagin 3': '2B10', 'Garuda': '2C10', 'Zu': '2D10', 'Sand Worm': '2E10', 'Land Worm': '2F10', 'Defender': '3010', 'Defender Z': '3110', 'Ghost': '3210', 'Phlegyas': '3310', 'Achelous': '3410', 'Remora': '3510', 'Maelspike': '3610', 'Dual Horn': '3710', 'Valaha': '3810', 'Grendel': '3910', 'Octopus': '3A10', 'Vouivre': '3B10', 'Lamashtu': '3C10', 'Kusariqqu': '3D10', 'Mushussu': '3E10', 'Nidhogg': '3F10', 'Malboro': '4010', 'Great Malboro': '4110', 'Ogre': '4210', 'Bashura': '4310', 'Piranha': '4410', 'Piranha 2': '4510', 'Piranha 3': '4610', 'Splasher': '4710', 'Splasher 2': '4810', 'Splasher 3': '4910', 'Vepar': '4A10', 'Vepar 2': '4B10', 'Vepar 3': '4C10', 'Yellow Element': '4D10', 'White Element': '4E10', 'Red Element': '4F10', 'Gold Element': '5010', 'Blue Element': '5110', 'Dark Element': '5210', 'Black Element': '5310', 'Epaaj': '5410', 'Behemoth': '5510', 'Behemoth King': '5610', 'Chimera': '5710', 'Chimera Brain': '5810', 'Coeurl': '5910', 'Master Coeurl': '5A10', 'Mech Guard': '5B10', 'Mech Scouter': '5C10', 'Mech Scouter 2': '5D10', 'Mech Leader': '5E10', 'Demonolith': '5F10', 'Mech Gunner': '6010', 'Mech Hunter': '6110', 'Mech Defender': '6210', 'Ultima Weapon': '6310', 'Omega Weapon': '6410', 'Tros': '6510', 'Sinspawn Geneaux': '6610', "Geneaux's Tentacle": '6710', 'Chocobo Eater': '6810', 'Neslug': '6910', 'Mortiphasm': '6A10', 'Sinscale': '6B10', 'Sinscale 2': '6C10', 'Geosgaeno': '6D10', 'Oblitzerator': '6E10', 'Extractor': '6F10', 'Uknwn': '7010', 'Sin': '7110', 'Sinspawn Echuilles': '7210', 'Sinscale 3': '7310', 'Sinscale 4': '7410', 'Sinspawn Gui': '7510', 'Mortiphasm 2': '7610', 'Evrae': '7710', 'Evrae Altana': '7810', 'Spherimorph': '7910', 'Crawler': '7A10', 'Negator': '7B10', 'Seymour': '7C10', 'Anima': '7D10', 'Seymour Natus': '7E10', 'Mortibody': '7F10', 'Sanctuary Keeper': '8010', 'Spectral Keeper': '8110', 'Yunalesca': '8210', 'Seymour Omnis': '8310', "Braska's Final Aeon": '8410', 'Crane': '8510', 'Biran Ronso': '8610', 'Yenke Ronso': '8710', 'Left Fin': '8810', 'Right Fin': '8910', 'Sin 2': '8A10', 'Sinspawn Genais': '8B10', 'Sin 3': '8C10', 'Guado Guardian': '8D10', 'Seymour Flux': '8E10', 'Mortiorchis': '8F10', 'Kimahri Weapon': '9010', 'Sinscale 5': '9110', 'Circle': '9210', 'Sinscale 6': '9310', 'Sinscale 7': '9410', 'Cid': '9510', 'Mortiphasm 3': '9610', 'Vouivre 2': '9710', 'Worker': '9810', 'Lord Ochu': '9910', 'Mortiphasm 4': '9A10', 'Sahagin 4': '9B10', 'Sahagin Chief': '9C10', 'Garuda 2': '9D10', 'Klikk': '9E10', 'Sinspawn Ammes': '9F10', 'Head': 'A010', 'Arm': 'A110', 'Gate Lock': 'A210', '{PC08:VALEFOR}': 'A310', '{PC09:IFRIT}': 'A410', '{PC0A:IXION}': 'A510', '{PC0B:SHIVA}': 'A610', '{PC0C:BAHAMUT}': 'A710', '{PC0D:ANIMA}': 'A810', '{PC0E:YOJIMBO}': 'A910', 'Tanker': 'AA10', 'Gate Lock 2': 'AB10', 'Monster 172': 'AC10', 'Yu Pagoda': 'AD10', 'Yu Pagoda 2': 'AE10', 'Tentacle': 'AF10', 'Yu Yevon': 'B010', 'Mortiphasm 5': 'B110', 'Cindy': 'B210', 'Sandy': 'B310', 'Mindy': 'B410', 'Iron Giant': 'B510', 'Gemini': 'B610', 'Gemini 2': 'B710', 'Gemini 3': 'B810', 'Basilisk': 'B910', 'Anacondaur': 'BA10', 'Adamantoise': 'BB10', 'Varuna': 'BC10', 'Ochu': 'BD10', 'Mandragora': 'BE10', 'YAT-99': 'BF10', 'YAT-97': 'C010', 'Bomb': 'C110', 'Grenade': 'C210', 'YKT-63': 'C310', 'YKT-11': 'C410', 'Warrior Monk': 'C510', 'Fallen Monk': 'C610', 'Warrior Monk 2': 'C710', 'Fallen Monk 2': 'C810', 'PuPu': 'C910', 'Magic Urn': 'CA10', 'Magic Urn 2': 'CB10', 'Magic Urn 3': 'CC10', 'Magic Urn 4': 'CD10', 'Magic Urn 5': 'CE10', 'Qactuar': 'CF10', 'Cactuar': 'D010', 'Larva': 'D110', 'Barbatos': 'D210', 'Uknwn 2': 'D310', 'Wendigo': 'D410', 'Guado Guardian 2': 'D510', 'Funguar': 'D610', 'Thorn': 'D710', 'Exoray': 'D810', 'Xiphos': 'D910', 'Puroboros': 'DA10', 'Spirit': 'DB10', 'Wraith': 'DC10', 'Sandragora': 'DD10', 'Guado Guardian 3': 'DE10', 'Tonberry': 'DF10', 'Master Tonberry': 'E010', 'Evil Eye 2': 'E110', 'Bomb 2': 'E210', 'Chimera 2': 'E310', 'Dual Horn 2': 'E410', 'Defender X': 'E510', 'Garuda 3': 'E610', 'Dingo 2': 'E710', 'Water Flan 2': 'E810', 'Condor 2': 'E910', 'Ragora 2': 'EA10', 'Raldo 2': 'EB10', 'Bunyip 2': 'EC10', 'Uknwn 3': 'ED10', 'Zu 2': 'EE10', 'Zaurus': 'EF10', 'Halma': 'F010', 'Aqua Flan': 'F110', 'Floating Death': 'F210', 'Maze Larva': 'F310', 'Machea': 'F410', 'Cave Iguion': 'F510', 'Swamp Mafdet': 'F610', 'Bat Eye': 'F710', 'Isaaru': 'F810', 'Mira': 'F910', 'Belgemine': 'FA10', 'Mimic': 'FB10', 'Mimic 2': 'FC10', 'Mimic 3': 'FD10', 'Valefor': 'FE10', 'Dummy': 'FF10', 'Mimic 4': '0011', 'Mimic Parts': '0111', 'Valefor 2': '0211', 'Ifrit': '0311', 'Mimic Parts 2': '0411', 'Mimic Parts 3': '0511', 'Mimic Parts 4': '0611', 'Rifle': '0711', 'Fire Rifle': '0811', 'Anima 2': '0911', 'Koma Inu': '0A11', 'Anima 3': '0B11', 'Anima 4': '0C11', 'Katana': '0D11', 'Kozuka': '0E11', 'Shuriken': '0F11', 'Head 2': '1011', 'Arm 2': '1111', 'Nishida': '1211', 'Sword': '1311', 'Nemesis': '1411', 'Catastrophe': '1511', 'None': '1611', 'Earth Eater': '1711', 'Ultima Buster': '1811', 'Greater Sphere': '1911', "Th'uban": '1A11', 'Shinryu': '1B11', 'Ifrit 2': '1C11', 'Ixion': '1D11', 'Shiva': '1E11', 'Bahamut': '1F11', 'Yojimbo': '2011', 'Sandy 2': '2111', 'Cindy 2': '2211', 'Mindy 2': '2311', 'Tanket': '2411', 'Vidatu': '2511', 'Fenrir': '2611', 'Jumbo Flan': '2711', 'Ornitholestes': '2811', 'Pteryx': '2911', 'Hornet': '2A11', 'One-Eye': '2B11', 'Stratoavis': '2C11', 'Abyss Worm': '2D11', 'Juggernaut': '2E11', 'Fafnir': '2F11', 'Malboro Menace': '3011', 'Kottos': '3111', 'Nega Elemental': '3211', 'Catoblepas': '3311', 'Chimerageist': '3411', 'Coeurlregina': '3511', 'Ironclad': '3611', 'Jormungand': '3711', 'Abaddon': '3811', 'Bomb King': '3911', 'Cactuar King': '3A11', 'Vorban': '3B11', 'Sleep Sprout': '3C11', 'Don Tonberry': '3D11', 'Espada': '3E11', 'Bomb 3': '3F11', 'Dual Horn 3': '4011', 'Vulture': '4111', 'Basilisk 2': '4211', 'Ochu 2': '4311', 'Larva 2': '4411', 'Iron Giant 2': '4511', 'Chimera 3': '4611', 'Monster 84': '4711', 'Qactuar 2': '4811', 'Zu 3': '4911', 'Sand Worm 2': '4A11', 'Ghost 2': '4B11', 'Malboro 2': '4C11', 'Bashura 2': '4D11', 'Dark Valefor': '4E11', 'Dark Ifrit': '4F11', 'Dark Ixion': '5011', 'Dark Shiva': '5111', 'Dark Bahamut': '5211', 'Dark Anima': '5311', 'Dark Yojimbo': '5411', 'Dark Cindy': '5511', 'Dark Sandy': '5611', 'Dark Mindy': '5711', 'Penance': '5811', 'Right Arm': '5911', 'Left Arm': '5A11', 'Unknown': '5B11', 'Unknown 2': '5C11', 'Unknown 3': '5D11', 'Unknown 4': '5E11', 'Unknown 5': '5F11', 'Unknown 6': '6011', 'Unknown 7': '6111', 'Unknown 8': '6211', 'Unknown 9': '6311', 'Unknown 10': '6411', '-': '6511', '- 2': '6611', '- 3': '6711', '- 4': '6811'}


dropdowns = []
hex_labels = []
image_labels = []

# Create an empty spacer frame for spacing purposes
spacer_frame = tk.Frame(root, height=0)  # Adjust the height as needed
spacer_frame.pack(side=tk.LEFT, expand=False, padx=75, pady=0)  # Span across both columns

# 
# Create canvas
canvas = tk.Canvas(root, width=400, height=400, bg="white")
canvas.pack(side=tk.LEFT, expand=False, padx=0, pady=0)

checkbox = tk.Checkbutton(root, text="Aeon Positions", variable=show_orange_only, command=toggle_dots)
checkbox.pack(side=tk.LEFT, padx=0)

coords_label_var = tk.StringVar()
coords_label = tk.Label(root, textvariable=coords_label_var)
coords_label.pack()

result_label_var = tk.StringVar()
result_label = tk.Label(root, textvariable=result_label_var)
result_label.pack(side=tk.LEFT, padx=0)

coords_text = tk.Text(root, width=30, height=24)
coords_text.pack(side=tk.LEFT, padx=10)
coords_text.bind("<KeyRelease>", lambda event: check_and_draw_lines())

slider = tk.Scale(root, from_=50, to=0, orient='vertical', command=update_y_from_slider)
slider.pack(side=tk.LEFT, padx=0)
label = tk.Label(root, text="Height")
label.pack(side=tk.LEFT, padx=0)



adPOS = tk.Button(root, text="ADD POSITION",  font=("Arial", 11, "bold"), command=on_button_click)
adPOS.config(width=18, height=2)
adPOS.place(x=1050, y=625)

dots = []

# Create 8 dropdowns with titles
for i in range(8):
    frame = tk.Frame(container)
    frame.grid(row=0, column=i, padx=5)

    # Add PictureBox above the dropdown
    image_label = tk.Label(frame)
    image_label.pack()

    title = tk.Label(frame, text=f"Monster#{i+1}", font=("Arial", 10, "bold"))
    title.pack()

    dropdown = ttk.Combobox(frame, values=options, width=int(0.75 * 20))  # Adjusted width to 75% of the default
    dropdown.set("(None)")  # Set <None> as default
    dropdown.pack()
    dropdown.bind("<<ComboboxSelected>>", lambda event, dropdown=dropdown, label=image_label: load_image(dropdown, label))

    hex_label = tk.Label(frame, text="", font=("Arial", 8), fg="black")
    hex_label.pack(pady=5)

    dropdowns.append(dropdown)
    hex_labels.append(hex_label)
    image_labels.append(image_label)

def process_and_create_dots(canvas, P_str, p_str, A_str, M_str, m_str):
    # Initial coordinates
    P_cords = bytes_to_ints(P_str)
    p_cords = bytes_to_ints(p_str)
    A_cords = bytes_to_ints(A_str)
    M_cords = bytes_to_ints(M_str)
    m_cords = bytes_to_ints(m_str)


    # Create dots
    create_dots(canvas, P_cords, "navy", "P", 12)
    create_dots(canvas, p_cords, "aqua", "p", 8)
    create_dots(canvas, A_cords, "orange", "A", 10)
    create_dots(canvas, M_cords, "crimson", "M", 12)
    create_dots(canvas, m_cords, "red", "m", 8)


# Manually triggering the event for dropdowns 1 to 7
for i in range(8):
    dropdowns[i].event_generate("<<ComboboxSelected>>")

# Call toggle_dots once to set the initial state
toggle_dots()

root.mainloop()
                          
