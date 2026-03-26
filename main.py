import tkinter as tk
from tkinter import filedialog
import struct
from PIL import Image, ImageTk

def read_image(file_path): 


    img = Image.open(file_path)
    
    img = img.convert('RGB')
    
    width, height = img.size
    pixels = []
    
    pixel_data = list(img.getdata())
    for y in range(height):
        row_pixels = []
        for x in range(width):
            r, g, b = pixel_data[y * width + x]
            row_pixels.append([r, g, b])
        pixels.append(row_pixels)
        
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
        self.root.geometry("800x450")
        
        self.loaded_picture = None
        self.processed_picture = None
        self.photo_original = None
        self.photo_processed = None
        
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
        
        self.effect_slider = tk.Scale(frame_bottom, from_=0, to=100, orient="horizontal", label="")
        self.effect_slider.set(100)
        self.effect_slider.pack(expand=True, fill="x", padx=20)
        self.effect_slider.bind("<ButtonRelease-1>", self.on_slider_release)
        
        self.current_operation = None
        
        menu_bar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_image)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        operations_menu = tk.Menu(menu_bar, tearoff=0)
        operations_menu.add_command(label="Grayscale", command=lambda: self.process_pixels(self.grayscale_pixel))
        operations_menu.add_command(label="CMYK", command=lambda: self.process_pixels(self.cmyk_pixel))
        operations_menu.add_command(label="YUV", command=lambda: self.process_pixels(self.yuv_pixel))
        operations_menu.add_command(label="YCbCr", command=lambda: self.process_pixels(self.ycbcr_pixel))
        operations_menu.add_command(label="inverse", command=self.apply_inverse)
        operations_menu.add_command(label="binarize", command=lambda: self.process_pixels(self.binarize_pixel))
        operations_menu.add_command(label="HSV", command=lambda: self.process_pixels(self.hsv_pixel))
        operations_menu.add_separator()
        operations_menu.add_command(label="Histograma", command=self.calculate_histogram)
        operations_menu.add_command(label="Moment Ord 1", command=lambda: self.compute_moments(1))
        operations_menu.add_command(label="Moment Ord 2", command=lambda: self.compute_moments(2))
        operations_menu.add_command(label="Covarianta", command=self.compute_covariance)
        operations_menu.add_command(label="Proiectii", command=self.compute_projections)
        menu_bar.add_cascade(label="Operations", menu=operations_menu)
        
        self.root.config(menu=menu_bar)

    def on_slider_release(self, event):
        if self.current_operation:
            self.current_operation()

    def open_image(self):
        file_path = filedialog.askopenfilename( 
            title="Open BMP Image", 
            filetypes=[("BMP files", "*.bmp")] 
        ) 
        
        if file_path:
            try:
                self.loaded_picture = read_image(file_path)
                self.processed_picture = None
                self.photo_processed = None
                
                self.photo_original = convert_matrix_to_photo(self.loaded_picture)
                self.lbl_original.config(image=self.photo_original)
                self.lbl_processed.config(image='')
            except Exception as e:
                print(f"Error loading image: {e}")

    def process_pixels(self, pixel_func):
        if self.loaded_picture is None:
            return
            
        self.current_operation = lambda: self.process_pixels(pixel_func)
        alpha = self.effect_slider.get() / 100.0
        
        height = len(self.loaded_picture)
        width = len(self.loaded_picture[0])
        
        self.processed_picture = []
        for y_coord in range(height):
            row = []
            for x in range(width):
                r, g, b = self.loaded_picture[y_coord][x]
                res_r, res_g, res_b = pixel_func(r, g, b, alpha)
                row.append([res_r, res_g, res_b])
            self.processed_picture.append(row)
            
        self.photo_processed = convert_matrix_to_photo(self.processed_picture)
        self.lbl_processed.config(image=self.photo_processed)

    def grayscale_pixel(self, r, g, b, alpha):
        gray = int((r + g + b) / 3)
        return [
            int(r * (1 - alpha) + gray * alpha),
            int(g * (1 - alpha) + gray * alpha),
            int(b * (1 - alpha) + gray * alpha)
        ]

    def cmyk_pixel(self, r, g, b, alpha):
        c_val = 1 - (r / 255)
        m_val = 1 - (g / 255)
        y_val = 1 - (b / 255)
        
        tr = int(c_val * 255)
        tg = int(m_val * 255)
        tb = int(y_val * 255)
        return [
            int(r * (1 - alpha) + tr * alpha),
            int(g * (1 - alpha) + tg * alpha),
            int(b * (1 - alpha) + tb * alpha)
        ]

    def yuv_pixel(self, r, g, b, alpha):
        y_val = 0.3 * r + 0.6 * g + 0.1 * b
        u_val = 0.74 * (r - y_val) + 0.27 * (b - y_val)
        v_val = 0.48 * (r - y_val) + 0.41 * (b - y_val)
        
        tr = max(0, min(255, int(y_val)))
        tg = max(0, min(255, int(u_val + 128)))
        tb = max(0, min(255, int(v_val + 128)))
        return [
            int(r * (1 - alpha) + tr * alpha),
            int(g * (1 - alpha) + tg * alpha),
            int(b * (1 - alpha) + tb * alpha)
        ]

    def ycbcr_pixel(self, r, g, b, alpha):
        y_val = 0.299 * r + 0.587 * g + 0.114 * b
        cb_val = -0.1687 * r - 0.3313 * g + 0.498 * b + 128
        cr_val = 0.498 * r - 0.4187 * g - 0.0813 * b + 128
        
        tr = max(0, min(255, int(y_val)))
        tg = max(0, min(255, int(cb_val)))
        tb = max(0, min(255, int(cr_val)))
        return [
            int(r * (1 - alpha) + tr * alpha),
            int(g * (1 - alpha) + tg * alpha),
            int(b * (1 - alpha) + tb * alpha)
        ]

    def binarize_pixel(self, r, g, b, alpha):
        threshold = alpha * 255
        p = int((r + g + b) / 3)
        bin_val = 255 if p > threshold else 0
        return [bin_val, bin_val, bin_val]

    def apply_inverse(self):
        if self.loaded_picture is None:
            return
            
        self.current_operation = self.apply_inverse
        alpha = self.effect_slider.get() / 100.0
            
        height = len(self.loaded_picture)
        width = len(self.loaded_picture[0])
        
        self.processed_picture = []
        inv_r_matrix, inv_g_matrix, inv_b_matrix = [], [], []
        
        for y_coord in range(height):
            row_inv, row_r, row_g, row_b = [], [], [], []
            for x in range(width):
                r, g, b = self.loaded_picture[y_coord][x]
                
                tr, tg, tb = 255 - r, 255 - g, 255 - b
                ir = int(r * (1 - alpha) + tr * alpha)
                ig = int(g * (1 - alpha) + tg * alpha)
                ib = int(b * (1 - alpha) + tb * alpha)
                
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
        
        if not hasattr(self, 'channels_window') or not self.channels_window.winfo_exists():
            self.channels_window = tk.Toplevel(self.root)
            self.channels_window.title("Inverse Image Channels (R, G, B)")
            
            self.lbl_r = tk.Label(self.channels_window)
            self.lbl_r.pack(side="left", padx=5, pady=5)
            self.lbl_g = tk.Label(self.channels_window)
            self.lbl_g.pack(side="left", padx=5, pady=5)
            self.lbl_b = tk.Label(self.channels_window)
            self.lbl_b.pack(side="left", padx=5, pady=5)
            
        self.photo_inv_r = convert_matrix_to_photo(inv_r_matrix)
        self.lbl_r.config(image=self.photo_inv_r)
        self.photo_inv_g = convert_matrix_to_photo(inv_g_matrix)
        self.lbl_g.config(image=self.photo_inv_g)
        self.photo_inv_b = convert_matrix_to_photo(inv_b_matrix)
        self.lbl_b.config(image=self.photo_inv_b)

    def hsv_pixel(self, r, g, b, alpha):
        r_, g_, b_ = r/255.0, g/255.0, b/255.0
        cmax = max(r_, g_, b_)
        cmin = min(r_, g_, b_)
        diff = cmax - cmin
        
        if cmax == cmin:
            h = 0
        elif cmax == r_:
            h = (60 * ((g_ - b_) / diff) + 360) % 360
        elif cmax == g_:
            h = (60 * ((b_ - r_) / diff) + 120) % 360
        else:
            h = (60 * ((r_ - g_) / diff) + 240) % 360
            
        s = 0 if cmax == 0 else (diff / cmax) * 100
        v = cmax * 100
        
        h_vis = int((h / 360) * 255)
        s_vis = int((s / 100) * 255)
        v_vis = int((v / 100) * 255)
        
        return [
            int(r * (1 - alpha) + h_vis * alpha),
            int(g * (1 - alpha) + s_vis * alpha),
            int(b * (1 - alpha) + v_vis * alpha)
        ]

    def get_intensity(self, r, g, b):
        return int((r + g + b) / 3)

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

    def calculate_histogram(self):
        if self.loaded_picture is None: return
        h = len(self.loaded_picture)
        w = len(self.loaded_picture[0])
            
        v = [0] * h
        for i in range(h):
            s = 0
            for j in range(w):
                s = s + self.get_intensity(*self.loaded_picture[i][j])
            v[i] = s
            
        self.display_bar_chart(v, "Histograma Conform Pseudocod")

    def compute_moments(self, order):
        if self.loaded_picture is None: return
        h = len(self.loaded_picture)
        w = len(self.loaded_picture[0])
            
        m00 = m10 = m01 = 0
        for y in range(h):
            for x in range(w):
                I = self.get_intensity(*self.loaded_picture[y][x])
                m00 += I
                m10 += x * I
                m01 += y * I
                
        if m00 == 0: 
            print("Imaginea nu contine informatie (M00 = 0).")
            return
            
        xc, yc = m10 / m00, m01 / m00
        
        if order == 1:
            print(f"Moment Ord 1: M10={m10}, M01={m01}")
            print(f"Centru de masa: ({xc:.2f}, {yc:.2f})")
        elif order == 2:
            m20 = m02 = m11 = 0
            for y in range(h):
                for x in range(w):
                    I = self.get_intensity(*self.loaded_picture[y][x])
                    m20 += (x ** 2) * I
                    m02 += (y ** 2) * I
                    m11 += (x * y) * I
            print(f"Moment Ord 2: M20={m20}, M02={m02}, M11={m11}")

    def compute_covariance(self):
        if self.loaded_picture is None: return
        h = len(self.loaded_picture)
        w = len(self.loaded_picture[0])
            
        m00 = m10 = m01 = 0
        for y in range(h):
            for x in range(w):
                I = self.get_intensity(*self.loaded_picture[y][x])
                m00 += I
                m10 += x * I
                m01 += y * I
                
        if m00 == 0: return
        xc, yc = m10 / m00, m01 / m00
        
        mu20 = mu02 = mu11 = 0
        for y in range(h):
            for x in range(w):
                I = self.get_intensity(*self.loaded_picture[y][x])
                mu20 += ((x - xc)**2) * I
                mu02 += ((y - yc)**2) * I
                mu11 += ((x - xc) * (y - yc)) * I
                
        cov20, cov02, cov11 = mu20 / m00, mu02 / m00, mu11 / m00
        print(f"Matricea de Covarianta:\n[{cov20:.2f}, {cov11:.2f}]\n[{cov11:.2f}, {cov02:.2f}]")

    def compute_projections(self):
        if self.loaded_picture is None: return
        h = len(self.loaded_picture)
        w = len(self.loaded_picture[0])
        
        proj_h = [0] * h
        proj_v = [0] * w
        
        for y in range(h):
            for x in range(w):
                I = self.get_intensity(*self.loaded_picture[y][x])
                proj_h[y] += I
                proj_v[x] += I
                
        self.display_bar_chart(proj_h, "Proiectie Orizontala")
        self.display_bar_chart(proj_v, "Proiectie Verticala")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()
