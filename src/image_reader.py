from PIL import Image
from models import RGB
import struct

def read_image(file_path): 
    img = Image.open(file_path)
    img = img.convert('RGB')
    
    width, height = img.size
    pixels = []
    
    pixel_data = list(img.getdata())
    for y in range(height):
        row_pixels = []
        for x in range(width):
            rgb = RGB(*pixel_data[y * width + x])
            row_pixels.append(rgb)
        pixels.append(row_pixels)
        
    return pixels

def read_bmp_24bit(file_path): 
    with open(file_path, 'rb') as f: 
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
            raise ValueError(f"Only 24‑bit BMP supported, got {bit_count}‑bit") 
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
                rgb = RGB(row_data[x * 3], row_data[x*3 + 1], row_data[x*3 + 2])
                row_pixels.append(rgb) 

            pixels.append(row_pixels) 

        if bottom_up: 
            pixels.reverse() 

        return pixels  
    