import tkinter as tk
from tkinter import filedialog
import struct
from PIL import Image, ImageTk

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

class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing App")
        self.root.geometry("800x400")
        
        self.loaded_picture = None
        self.processed_picture = None
        self.photo_original = None
        self.photo_processed = None
        
        self.setup_gui()
        
    def setup_gui(self):
        frame_left = tk.Frame(self.root, width=400, height=400, bg="white")
        frame_left.pack(side="left", fill="both", expand=True)
        frame_left.pack_propagate(False)
        
        frame_right = tk.Frame(self.root, width=400, height=400, bg="white")
        frame_right.pack(side="right", fill="both", expand=True)
        frame_right.pack_propagate(False)
        
        self.lbl_original = tk.Label(frame_left, bg="white")
        self.lbl_original.pack(expand=True)
        
        self.lbl_processed = tk.Label(frame_right, bg="white")
        self.lbl_processed.pack(expand=True)
        
        menu_bar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_image)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        operations_menu = tk.Menu(menu_bar, tearoff=0)
        operations_menu.add_command(label="Grayscale", command=self.apply_grayscale)
        operations_menu.add_command(label="CMYK", command=self.apply_cmyk)
        menu_bar.add_cascade(label="Operations", menu=operations_menu)
        
        self.root.config(menu=menu_bar)

    def open_image(self):
        file_path = filedialog.askopenfilename( 
            title="Open BMP Image", 
            filetypes=[("BMP files", "*.bmp")] 
        ) 
        
        if file_path:
            try:
                self.loaded_picture = read_bmp_24bit(file_path)
                self.processed_picture = None
                self.photo_processed = None
                
                self.photo_original = convert_matrix_to_photo(self.loaded_picture)
                self.lbl_original.config(image=self.photo_original)
                self.lbl_processed.config(image='')
            except Exception as e:
                print(f"Error loading image: {e}")

    def apply_grayscale(self):
        if self.loaded_picture is None:
            return
            
        height = len(self.loaded_picture)
        width = len(self.loaded_picture[0])
        
        self.processed_picture = []
        for y in range(height):
            row = []
            for x in range(width):
                r, g, b = self.loaded_picture[y][x]
                gray = int((r + g + b) / 3)
                row.append([gray, gray, gray])
            self.processed_picture.append(row)
            
        self.photo_processed = convert_matrix_to_photo(self.processed_picture)
        self.lbl_processed.config(image=self.photo_processed)

    def apply_cmyk(self):
        if self.loaded_picture is None:
            return
            
        height = len(self.loaded_picture)
        width = len(self.loaded_picture[0])
        
        self.processed_picture = []
        for y in range(height):
            row = []
            for x in range(width):
                r, g, b = self.loaded_picture[y][x]
                
                c_val = 1 - (r / 255)
                m_val = 1 - (g / 255)
                y_val = 1 - (b / 255)
                
                c_pixel = int(c_val * 255)
                m_pixel = int(m_val * 255)
                y_pixel = int(y_val * 255)
                
                row.append([c_pixel, m_pixel, y_pixel])
                
            self.processed_picture.append(row)
            
        self.photo_processed = convert_matrix_to_photo(self.processed_picture)
        self.lbl_processed.config(image=self.photo_processed)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()
