from image_modifiers import eroziune
import tkinter as tk
from tkinter import filedialog, simpledialog
import struct
from PIL import Image, ImageTk
from image_reader import read_bmp_24bit, read_image
from color_space_modifiers import *
from image_modifiers import *
from models import RGB
import random
import math 

def convert_matrix_to_photo(rgb_matrix):
    height = len(rgb_matrix)
    width = len(rgb_matrix[0])
    img = Image.new("RGB", (width, height))
    for y in range(height):
        for x in range(width):
            pixel = rgb_matrix[y][x]
            img.putpixel((x, y), (pixel.r, pixel.g, pixel.b))
    return ImageTk.PhotoImage(img)

class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Atome PngShop")
        self.root.geometry("800x450")
        
        self.loaded_picture = None
        self.processed_picture = None
        self.photo_original = None
        self.photo_processed = None
        self.converted_photo = None
        
        self.alpha = 100
        
        self.setup_gui()
        
    def setup_gui(self):

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        frame_left = tk.Frame(main_frame, width=400, height=350, bg="white")
        frame_left.pack(side="left", fill="both", expand=True)
        frame_left.pack_propagate(False)
        
        frame_right = tk.Frame(main_frame, width=400, height=350, bg="white")
        frame_right.pack(side="right", fill="both", expand=True)
        frame_right.pack_propagate(False)
        
        self.lbl_original = tk.Label(frame_left, bg="white")
        self.lbl_original.pack(expand=True)
        
        self.lbl_processed = tk.Label(frame_right, bg="white")
        self.lbl_processed.pack(expand=True)
        
        frame_bottom = tk.Frame(self.root)
        frame_bottom.pack(side="bottom", fill="x", pady=10)
        
        self.effect_slider = tk.Scale(frame_bottom, from_=0, to=100, orient="horizontal", label="", command=self.on_slider_release)
        self.effect_slider.set(self.alpha)
        self.effect_slider.pack(expand=True, fill="x", padx=20)
        
        
        menu_bar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=lambda: self.open_image(manual=False))
        file_menu.add_command(label="Open 24bit BMP", command=lambda: self.open_image(manual=True))
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        self.current_operation = None
        operations_menu = tk.Menu(menu_bar, tearoff=0)
        operations_menu.add_command(label="Grayscale", command=lambda: self.execute_per_pixel(grayscale_pixel))
        operations_menu.add_command(label="CMYK", command=lambda: self.execute_per_pixel(cmyk_pixel))
        operations_menu.add_command(label="YUV", command=lambda: self.execute_per_pixel(yuv_pixel))
        operations_menu.add_command(label="YCbCr", command=lambda: self.execute_per_pixel(ycbcr_pixel))
        operations_menu.add_command(label="Inverse", command=lambda: self.execute_per_pixel(inverse))
        operations_menu.add_command(label="Binarize", command=lambda: self.execute_per_pixel(binarize_pixel))
        operations_menu.add_separator()
        operations_menu.add_command(label="Histograma", command=lambda: self.execute_with_graph(calculate_histogram))
        operations_menu.add_command(label="Egalizare Histograma", command=lambda: self.execute_with_display(equalize_histogram))
        operations_menu.add_separator()
        operations_menu.add_command(label="Dilatare", command=lambda: self.execute_repeated(dilatare))
        operations_menu.add_command(label="Eroziune", command=lambda: self.execute_repeated(eroziune))
        operations_menu.add_command(label="Deschidere", command=lambda: self.display(self.chain_execute(dilatare, eroziune)))
        operations_menu.add_command(label="Inchidere", command=lambda: self.display(self.chain_execute(eroziune, dilatare)))
        operations_menu.add_command(label="Moment Ord 1", command=lambda: self.execute_with_display(display_first_order))
        operations_menu.add_command(label="Moment Ord 2", command=lambda: self.execute(compute_second_order))
        operations_menu.add_command(label="Covarianta", command=lambda: self.execute(compute_covariance))
        operations_menu.add_command(label="Proiectii", command=lambda: self.execute(compute_projections))
        operations_menu.add_separator()
        operations_menu.add_command(label="Etichetare (Labeling)", command=lambda: self.execute_with_display(etichetare))
        operations_menu.add_command(label="Selectie & Orientare (0)", command=self.selectie_obiect)
        operations_menu.add_command(label="Selectie & Orientare (1)", command=self.selectie_obiect_global)
        menu_bar.add_cascade(label="Operations", menu=operations_menu)
        
        self.root.config(menu=menu_bar)

    def on_slider_release(self, event):
        if self.current_operation:
            self.current_operation()

    def get_dimensions(self):
        if self.loaded_picture is None:
            raise ValueError("No image provided")

        h = len(self.loaded_picture)
        w = len(self.loaded_picture[0])
        return (h, w)

    def open_image(self, manual = False):
        file_path = filedialog.askopenfilename( 
            title="Open BMP Image", 
            filetypes=[("BMP files", "*.bmp")] 
        ) 
        
        if file_path:
            try:
                if not manual:
                    self.loaded_picture = read_image(file_path)
                else:
                    self.loaded_picture = read_bmp_24bit(file_path)
                self.processed_picture = None
                self.photo_processed = None
                
                self.photo_original = convert_matrix_to_photo(self.loaded_picture)
                self.lbl_original.config(image=self.photo_original)
                self.lbl_processed.config(image='')
            except Exception as e:
                print(f"Error loading image: {e}")

    def execute(self, func, processed = None):
        if processed is None:
            processed = self.loaded_picture
            
        h, w = self.get_dimensions()
        
        return func(processed, h, w)
    
    def chain_execute(self, *funcs):
        h, w = self.get_dimensions()

        image = self.loaded_picture
        for func in funcs:
            image = self.execute(func, processed=image)
        
        return image
        
    def execute_with_graph(self, func):
        result = self.execute(func)
        self.display_bar_chart(result, "Result")

    def execute_with_display(self, func):
        result = self.execute(func)
        self.display(result)

    def execute_repeated(self, func):
        n = simpledialog.askinteger("Repetari", "Numarul de repetari:", parent=self.root, minvalue=1)
        if n is None:
            raise ValueError("Repetari invalide")

        result = self.execute(func)
        for _ in range(n - 1):
            result = self.execute(func, result)

        self.display(result)
        
    def display(self, result):
        self.processed_picture = result
        self.photo_processed = convert_matrix_to_photo(self.processed_picture)
        self.lbl_processed.config(image=self.photo_processed)

    def execute_per_pixel(self, func):
        h, w = self.get_dimensions()
        
        processed_pic = []
        for y in range(h):
            row = []
            for x in range(w):
                rgb = self.loaded_picture[y][x]
                res = func(rgb)
                row.append(res)
            processed_pic.append(row)
            
        self.display(processed_pic)

    def display_bar_chart(self, data, title):
        top = tk.Toplevel(self.root)
        top.title(title)
        canvas = tk.Canvas(top, width=600, height=400, bg="white")
        canvas.pack(fill="both", expand=True)
    
        if not data: return
        max_val = max(data)
        if max_val == 0: max_val = 1
    
        bar_width = 600 / len(data)
        for i, val in enumerate(data):
            x0 = i * bar_width
            y0 = 400
            x1 = x0 + bar_width
            y1 = 400 - (val / max_val * 380)
            canvas.create_rectangle(x0, y0, x1, y1, fill="blue", outline="")


    def calculateObjectOrientation(self, image_matrix, current_label):
        width = len(image_matrix[0])
        height = len(image_matrix)

        gradientX = [[0 for _ in range(height)] for _ in range(width)]
        gradientY = [[0 for _ in range(height)] for _ in range(width)]

        def getRGB_gray(x, y):
            pixel = image_matrix[y][x]
            return pixel.get_intensity()

        for y in range(height):
            for x in range(width):
                if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                    gradientX[x][y] = 0
                    gradientY[x][y] = 0
                    continue
                
                gradientX[x][y] = getRGB_gray(x + 1, y - 1) + (2 * getRGB_gray(x + 1, y)) + getRGB_gray(x + 1, y + 1) - \
                                  getRGB_gray(x - 1, y - 1) - (2 * getRGB_gray(x - 1, y)) - getRGB_gray(x - 1, y + 1)
                
                gradientY[x][y] = getRGB_gray(x - 1, y + 1) + (2 * getRGB_gray(x, y + 1)) + getRGB_gray(x + 1, y + 1) - \
                                  getRGB_gray(x - 1, y - 1) - (2 * getRGB_gray(x, y - 1)) - getRGB_gray(x + 1, y - 1)

        maxGradientMagnitude = 0
        orientation = 0
        
        for y in range(height):
            for x in range(width):
                if self.labels[y][x] == current_label:
                    magnitude = math.sqrt(gradientX[x][y] * gradientX[x][y] + gradientY[x][y] * gradientY[x][y])
                    
                    if magnitude > maxGradientMagnitude:
                        maxGradientMagnitude = magnitude
                        maxGradientMagnitude = magnitude
                        orientation = math.atan2(gradientY[x][y], gradientX[x][y])
        
        return orientation

    def selectie_obiect(self):
        from tkinter import simpledialog
        if not hasattr(self, 'labels'):
            print("Va rog faceti etichetarea prima data.")
            return

        label_id = simpledialog.askinteger("Selectie", "Introduceti eticheta obiectului:", parent=self.root)
        if label_id is None or label_id < 1 or label_id > self.max_label:
            return

        height = len(self.loaded_picture)
        width = len(self.loaded_picture[0])

        self.processed_picture = []
        for i in range(height):
            row = []
            for j in range(width):
                if self.labels[i][j] == label_id:
                    row.append(self.label_colors[label_id])
                else:
                    pixel = self.loaded_picture[i][j]
                    g = pixel.get_intensity()
                    row.append(RGB(g, g, g))
            self.processed_picture.append(row)

        self.photo_processed = convert_matrix_to_photo(self.processed_picture)
        self.lbl_processed.config(image=self.photo_processed)

        orientation = self.calculateObjectOrientation(self.loaded_picture, label_id)
        print(f"Obiectul cu eticheta {label_id} are orientarea: {math.degrees(orientation)} grade")

    def calculateObjectOrientation_Global(self, image_matrix, current_label):
        width = len(image_matrix[0])
        height = len(image_matrix)

        gradientX = [[0 for _ in range(height)] for _ in range(width)]
        gradientY = [[0 for _ in range(height)] for _ in range(width)]

        for y in range(height):
            for x in range(width):
                if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                    gradientX[x][y] = 0
                    gradientY[x][y] = 0
                    continue
                
                # Matricele de vecinatate folosind get_intensity
                p11 = self.get_intensity(image_matrix[y-1][x-1])
                p12 = self.get_intensity(image_matrix[y-1][x])
                p13 = self.get_intensity(image_matrix[y-1][x+1])
                
                p21 = self.get_intensity(image_matrix[y][x-1])
                p23 = self.get_intensity(image_matrix[y][x+1])
                
                p31 = self.get_intensity(image_matrix[y+1][x-1])
                p32 = self.get_intensity(image_matrix[y+1][x])
                p33 = self.get_intensity(image_matrix[y+1][x+1])
                
                # Sobel gradients
                gx = (p13 + 2*p23 + p33) - (p11 + 2*p21 + p31)
                gy = (p31 + 2*p32 + p33) - (p11 + 2*p12 + p13)

                gradientX[x][y] = gx
                gradientY[x][y] = gy

        sum_xx = 0
        sum_yy = 0
        sum_xy = 0
        
        for y in range(height):
            for x in range(width):
                if self.labels[y][x] == current_label:
                    gx = gradientX[x][y]
                    gy = gradientY[x][y]
                    
                    # Tensor de structura pentru orientarea globala (suma)
                    sum_xx += gx * gx
                    sum_yy += gy * gy
                    sum_xy += gx * gy
        
        if sum_xx == 0 and sum_yy == 0:
            return 0
            
        theta = 0.5 * math.atan2(2 * sum_xy, sum_xx - sum_yy)
        orientation = theta + (math.pi / 2)
        
        if orientation > math.pi / 2:
            orientation -= math.pi
            
        return orientation

    def selectie_obiect_global(self):
        if not hasattr(self, 'labels'):
            print("Va rog faceti etichetarea prima data.")
            return

        label_id = simpledialog.askinteger("Selectie", "Introduceti eticheta obiectului:", parent=self.root)
        if label_id is None or label_id < 1 or label_id > self.max_label:
            return

        height = len(self.loaded_picture)
        width = len(self.loaded_picture[0])

        self.processed_picture = []
        for i in range(height):
            row = []
            for j in range(width):
                if self.labels[i][j] == label_id:
                    row.append(self.label_colors[label_id])
                else:
                    pixel = self.loaded_picture[i][j]
                    g = pixel.get_intensity()
                    row.append(RGB(g, g, g))
            self.processed_picture.append(row)

        self.photo_processed = convert_matrix_to_photo(self.processed_picture)
        self.lbl_processed.config(image=self.photo_processed)

        orientation = self.calculateObjectOrientation_Global(self.loaded_picture, label_id)
        print(f"Obiectul cu eticheta {label_id} are orientarea: {math.degrees(orientation):.2f} grade")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()
