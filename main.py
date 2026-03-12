import tkinter as tk
from tkinter import filedialog
import struct
from PIL import Image, ImageTk

LOADED_PICTURE = None
GRAYSCALE_PICTURE = None
PHOTO_ORIGINAL = None
PHOTO_GRAYSCALE = None

def read_bmp_24bit(file_path): 
    with open(file_path, 'rb') as f: 
        file_header = f.read(14) 
        if len(file_header) < 14 or file_header[0:2] != b'BM': 
            raise ValueError("Not a valid BMP file") 
  
        data_offset = struct.unpack('<I', file_header[10:14])[0] 
        info_header = f.read(40) 
        
        width = struct.unpack('<i', info_header[4:8])[0] 
        height = struct.unpack('<i', info_header[8:12])[0] 
        bit_count = struct.unpack('<H', info_header[14:16])[0] 
        
        if bit_count != 24: 
            raise ValueError("Only 24-bit BMP supported") 
            
        bottom_up = height > 0 
        abs_height = abs(height) 
        row_size = ((width * 3 + 3) // 4) * 4 
        f.seek(data_offset) 
  
        pixels = [] 
        for _ in range(abs_height): 
            row_data = f.read(row_size) 
            row_pixels = [] 
            for x in range(width): 
                b = row_data[x*3] 
                g = row_data[x*3 + 1] 
                r = row_data[x*3 + 2] 
                row_pixels.append([r, g, b]) 
            pixels.append(row_pixels) 
            
        if bottom_up: 
            pixels.reverse() 
  
        return pixels

def convert_matrix_to_photo(rgb_matrix):
    height = len(rgb_matrix)
    width = len(rgb_matrix[0])
    img = Image.new("RGB", (width, height))
    for y in range(height):
        for x in range(width):
            r, g, b = rgb_matrix[y][x]
            img.putpixel((x, y), (r, g, b))
    return ImageTk.PhotoImage(img)

def open_image(lbl_original, lbl_grayscale):
    global LOADED_PICTURE, GRAYSCALE_PICTURE, PHOTO_ORIGINAL, PHOTO_GRAYSCALE
    
    file_path = filedialog.askopenfilename( 
        title="Open BMP Image", 
        filetypes=[("BMP files", "*.bmp")] 
    ) 
    
    if file_path:
        try:
            LOADED_PICTURE = read_bmp_24bit(file_path)
            GRAYSCALE_PICTURE = None
            PHOTO_GRAYSCALE = None
            
            PHOTO_ORIGINAL = convert_matrix_to_photo(LOADED_PICTURE)
            lbl_original.config(image=PHOTO_ORIGINAL)
            lbl_grayscale.config(image='')
        except Exception as e:
            print(f"Error loading image: {e}")

def apply_grayscale(lbl_grayscale):
    global LOADED_PICTURE, GRAYSCALE_PICTURE, PHOTO_GRAYSCALE
    
    if LOADED_PICTURE is None:
        return
        
    height = len(LOADED_PICTURE)
    width = len(LOADED_PICTURE[0])
    
    GRAYSCALE_PICTURE = []
    for y in range(height):
        row = []
        for x in range(width):
            r, g, b = LOADED_PICTURE[y][x]
            gray = int((r + g + b) / 3)
            row.append([gray, gray, gray])
        GRAYSCALE_PICTURE.append(row)
        
    PHOTO_GRAYSCALE = convert_matrix_to_photo(GRAYSCALE_PICTURE)
    lbl_grayscale.config(image=PHOTO_GRAYSCALE)

def setup_gui():
    root = tk.Tk()
    root.title("Image Processing App")
    root.geometry("800x400")
    
    frame_left = tk.Frame(root, width=400, height=400, bg="white")
    frame_left.pack(side="left", fill="both", expand=True)
    frame_left.pack_propagate(False)
    
    frame_right = tk.Frame(root, width=400, height=400, bg="white")
    frame_right.pack(side="right", fill="both", expand=True)
    frame_right.pack_propagate(False)
    
    lbl_original = tk.Label(frame_left, bg="white")
    lbl_original.pack(expand=True)
    
    lbl_grayscale = tk.Label(frame_right, bg="white")
    lbl_grayscale.pack(expand=True)
    
    menu_bar = tk.Menu(root)
    
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Open", command=lambda: open_image(lbl_original, lbl_grayscale))
    menu_bar.add_cascade(label="File", menu=file_menu)
    
    operations_menu = tk.Menu(menu_bar, tearoff=0)
    operations_menu.add_command(label="Grayscale", command=lambda: apply_grayscale(lbl_grayscale))
    menu_bar.add_cascade(label="Operations", menu=operations_menu)
    
    root.config(menu=menu_bar)
    root.mainloop()

if __name__ == "__main__":
    setup_gui()
