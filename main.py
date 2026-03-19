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
        operations_menu.add_command(label="YUV", command=self.apply_yuv)
        operations_menu.add_command(label="YCbCr", command=self.apply_ycbcr)
        operations_menu.add_command(label="Inverse", command=self.apply_inverse)
        operations_menu.add_command(label="Binarize", command=self.apply_binarize)
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

    def apply_yuv(self):
        if self.loaded_picture is None:
            return
            
        height = len(self.loaded_picture)
        width = len(self.loaded_picture[0])
        
        self.processed_picture = []
        for y_coord in range(height):
            row = []
            for x in range(width):
                r, g, b = self.loaded_picture[y_coord][x]
                
                y_val = 0.3 * r + 0.6 * g + 0.1 * b
                u_val = 0.74 * (r - y_val) + 0.27 * (b - y_val)
                v_val = 0.48 * (r - y_val) + 0.41 * (b - y_val)
                
                y_pixel = max(0, min(255, int(y_val)))
                u_pixel = max(0, min(255, int(u_val + 128))) 
                v_pixel = max(0, min(255, int(v_val + 128)))
                
                row.append([y_pixel, u_pixel, v_pixel])
                
            self.processed_picture.append(row)
            
        self.photo_processed = convert_matrix_to_photo(self.processed_picture)
        self.lbl_processed.config(image=self.photo_processed)

    def apply_ycbcr(self):
        if self.loaded_picture is None:
            return
            
        height = len(self.loaded_picture)
        width = len(self.loaded_picture[0])
        
        self.processed_picture = []
        for y_coord in range(height):
            row = []
            for x in range(width):
                r, g, b = self.loaded_picture[y_coord][x]
                
                y_val = 0.299 * r + 0.587 * g + 0.114 * b
                cb_val = -0.1687 * r - 0.3313 * g + 0.498 * b + 128
                cr_val = 0.498 * r - 0.4187 * g - 0.0813 * b + 128
                
                y_pixel = max(0, min(255, int(y_val)))
                cb_pixel = max(0, min(255, int(cb_val)))
                cr_pixel = max(0, min(255, int(cr_val)))
                
                row.append([y_pixel, cb_pixel, cr_pixel])
                
            self.processed_picture.append(row)
            
        self.photo_processed = convert_matrix_to_photo(self.processed_picture)
        self.lbl_processed.config(image=self.photo_processed)

    def apply_inverse(self):
        if self.loaded_picture is None:
            return
            
        height = len(self.loaded_picture)
        width = len(self.loaded_picture[0])
        
        self.processed_picture = []
        inv_r_matrix = []
        inv_g_matrix = []
        inv_b_matrix = []
        
        for y_coord in range(height):
            row_inv = []
            row_r = []
            row_g = []
            row_b = []
            for x in range(width):
                r, g, b = self.loaded_picture[y_coord][x]
                
                # Inverse
                ir = 255 - r
                ig = 255 - g
                ib = 255 - b
                
                row_inv.append([ir, ig, ib])
                row_r.append([ir, 0, 0])
                row_g.append([0, ig, 0])
                row_b.append([0, 0, ib])
                
            self.processed_picture.append(row_inv)
            inv_r_matrix.append(row_r)
            inv_g_matrix.append(row_g)
            inv_b_matrix.append(row_b)
            
        self.photo_processed = convert_matrix_to_photo(self.processed_picture)
        self.lbl_processed.config(image=self.photo_processed)
        
        # Display the 3 channels in a new window
        channels_window = tk.Toplevel(self.root)
        channels_window.title("Inverse Image Channels (R, G, B)")
        
        lbl_r = tk.Label(channels_window)
        lbl_r.pack(side="left", padx=5, pady=5)
        self.photo_inv_r = convert_matrix_to_photo(inv_r_matrix)
        lbl_r.config(image=self.photo_inv_r)
        
        lbl_g = tk.Label(channels_window)
        lbl_g.pack(side="left", padx=5, pady=5)
        self.photo_inv_g = convert_matrix_to_photo(inv_g_matrix)
        lbl_g.config(image=self.photo_inv_g)
        
        lbl_b = tk.Label(channels_window)
        lbl_b.pack(side="left", padx=5, pady=5)
        self.photo_inv_b = convert_matrix_to_photo(inv_b_matrix)
        lbl_b.config(image=self.photo_inv_b)

    def apply_binarize(self):
        if self.loaded_picture is None:
            return
            
        height = len(self.loaded_picture)
        width = len(self.loaded_picture[0])
        
        self.processed_picture = []
        threshold = 127
        
        for y_coord in range(height):
            row = []
            for x in range(width):
                r, g, b = self.loaded_picture[y_coord][x]
                
                luma = 0.3 * r + 0.6 * g + 0.1 * b
                bin_val = 255 if luma > threshold else 0
                
                row.append([bin_val, bin_val, bin_val])
                
            self.processed_picture.append(row)
            
        self.photo_processed = convert_matrix_to_photo(self.processed_picture)
        self.lbl_processed.config(image=self.photo_processed)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()
