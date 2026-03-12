import tkinter as tk
from tkinter import filedialog
import struct
import os
import cv2
from PIL import Image
import matplotlib.pyplot as plt

LOADED_PICTURE = ""


def read_bmp_24bit(file_path): 
    """ 
    Reads a 24-bit uncompressed BMP file and returns a 3D list of RGB values. 
    The list has the structure: matrix[y][x] = [R, G, B]  (top-to-bottom, left-to-right). 
    Raises ValueError if the BMP format is not supported. 
    """ 
    with open(file_path, 'rb') as f: 
        # Read BITMAPFILEHEADER (14 bytes) 
        file_header = f.read(14) 
        if len(file_header) < 14: 
            raise ValueError("File too small to be a BMP") 
        signature = file_header[0:2] 
        if signature != b'BM': 
            raise ValueError("Not a BMP file (invalid signature)") 
  
        file_size = struct.unpack('<I', file_header[2:6])[0] 
        data_offset = struct.unpack('<I', file_header[10:14])[0] 
        info_header = f.read(40) 
        if len(info_header) < 40: 
            raise ValueError("Incomplete BMP info header") 

        header_size = struct.unpack('<I', info_header[0:4])[0] 
        width = struct.unpack('<i', info_header[4:8])[0] 
        height = struct.unpack('<i', info_header[8:12])[0] 
        planes = struct.unpack('<H', info_header[12:14])[0] 
        bit_count = struct.unpack('<H', info_header[14:16])[0] 
        compression = struct.unpack('<I', info_header[16:20])[0] 
        image_size = struct.unpack('<I', info_header[20:24])[0] 
  
        if bit_count != 24: 
            raise ValueError(f"Only 24-bit BMP supported, got {bit_count}-bit") 
        if compression != 0:  # BI_RGB 
            raise ValueError("Only uncompressed BMP supported") 
  
        bottom_up = height > 0 
        abs_height = abs(height) 
        row_size = ((width * 3 + 3) // 4) * 4 

        f.seek(data_offset) 
  
        pixels = [] 
        for _ in range(abs_height): 
            row_data = f.read(row_size) 
            if len(row_data) < row_size: 
                raise ValueError("Unexpected end of file") 

            row_pixels = [] 
            for x in range(width): 
                b = row_data[x*3] 
                g = row_data[x*3 + 1] 
                r = row_data[x*3 + 2] 
                row_pixels.append([r, g, b]) 

            pixels.append(row_pixels) 

        if bottom_up: 
            pixels.reverse() 
  
        return pixels  # matrix[y][x] = [R,G,B] 

def open_image_and_create_matrix(): 
    global LOADED_PICTURE

    file_path = filedialog.askopenfilename( 
        title="Open BMP Image", 
        filetypes=[("BMP files", "*.bmp"), ("All files", "*.*")] 
    ) 
  
    if not file_path: 
        print("No file selected.") 
        return None 
  
    try: 
        LOADED_PICTURE = read_bmp_24bit(file_path) 
        print(f"Image loaded from: {file_path}") 
        print(f"Matrix dimensions: {len(LOADED_PICTURE)} rows x {len(LOADED_PICTURE[0])} columns") 
        print(f"Example pixel at (0,0): R={LOADED_PICTURE[0][0][0]}, G={LOADED_PICTURE[0][0][1]}, B={LOADED_PICTURE[0][0][2]}") 
    except Exception as e: 
        print(f"Error reading BMP: {e}") 
        return None 

def open_image_cv2():
    global LOADED_PICTURE
    file_path = filedialog.askopenfilename( 
        title="Open Image", 
        filetypes=[("Image files", "*.bmp *.png *.jpg *.jpeg"), ("All files", "*.*")] 
    ) 
    if file_path:  
        LOADED_PICTURE = cv2.imread(file_path)  
        if LOADED_PICTURE is None:  
            print("Error: Could not read the image.")  
            return None  
        print(f"Image loaded from: {file_path}")  
        print(f"Matrix shape (height, width, channels): {LOADED_PICTURE.shape}")  
    else:  
        print("No file selected.")  
        return None  


def open_image():
    global LOADED_PICTURE
    if LOADED_PICTURE is not None: 
        plt.imshow(LOADED_PICTURE)
        plt.axis("off")
        plt.show()

def main():
    root = tk.Tk()
    root.title("Image Processing App")
    root.geometry("350x260")

    # The 4 buttons request
    btn_original = tk.Button(root, text="Deschide original", command=open_image_and_create_matrix, width=25)
    btn_original.pack(pady=10)

    btn_cv2 = tk.Button(root, text="Deschide cu cv2", command=open_image_cv2, width=25)
    btn_cv2.pack(pady=10)

    btn_save = tk.Button(root, text="Deschide imaginea", command=open_image, width=25)
    btn_save.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
