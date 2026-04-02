import tkinter as tk
from tkinter import filedialog
import struct
from PIL import Image, ImageTk
import random
import math 

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
        self.root.title("Atome PngShop")
        self.root.geometry("800x450")
        
        self.loaded_picture = None
        self.processed_picture = None
        self.photo_original = None
        self.photo_processed = None
        
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
        
        self.current_operation = None
        
        menu_bar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=lambda: self.open_image(manual=False))
        file_menu.add_command(label="Open 24bit BMP", command=lambda: self.open_image(manual=True))
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        operations_menu = tk.Menu(menu_bar, tearoff=0)
        operations_menu.add_command(label="Grayscale", command=lambda: self.process_pixels(self.grayscale_pixel))
        operations_menu.add_command(label="CMYK", command=lambda: self.process_pixels(self.cmyk_pixel))
        operations_menu.add_command(label="YUV", command=lambda: self.process_pixels(self.yuv_pixel))
        operations_menu.add_command(label="YCbCr", command=lambda: self.process_pixels(self.ycbcr_pixel))
        operations_menu.add_command(label="inverse", command=self.apply_inverse_with_channels)
        operations_menu.add_command(label="binarize", command=lambda: self.process_pixels(self.binarize_pixel))
        operations_menu.add_command(label="HSV", command=lambda: self.process_pixels(self.hsv_pixel))
        operations_menu.add_separator()
        operations_menu.add_command(label="Histograma", command=self.real_histogram)
        operations_menu.add_command(label="Moment Ord 1", command=lambda: self.compute_moments(1))
        operations_menu.add_command(label="Moment Ord 2", command=lambda: self.compute_moments(2))
        operations_menu.add_command(label="Covarianta", command=self.compute_covariance)
        operations_menu.add_command(label="Proiectii", command=self.compute_projections)
        operations_menu.add_separator()
        operations_menu.add_command(label="Etichetare (Labeling)", command=self.etichetare)
        operations_menu.add_command(label="Selectie & Orientare (0)", command=self.selectie_obiect)
        operations_menu.add_command(label="Selectie & Orientare (1)", command=self.selectie_obiect_global)
        menu_bar.add_cascade(label="Operations", menu=operations_menu)
        
        self.root.config(menu=menu_bar)

    def on_slider_release(self, event):
        if self.current_operation:
            self.current_operation()

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

    def alpha_blending(self, r, g, b, tr, tg, tb, alpha):
        inverse_alpha = 1 - alpha
        return [
            int(r * inverse_alpha + tr * alpha),
            int(g * inverse_alpha + tg * alpha),
            int(b * inverse_alpha + tb * alpha)
        ]
    def process_pixels(self, pixel_func):
        if self.loaded_picture is None:
            return
            
        self.current_operation = lambda: self.process_pixels(pixel_func)
        self.alpha = self.effect_slider.get() / 100.0
        
        height = len(self.loaded_picture)
        width = len(self.loaded_picture[0])
        
        self.processed_picture = []
        for y_coord in range(height):
            row = []
            for x in range(width):
                r, g, b = self.loaded_picture[y_coord][x]
                res_r, res_g, res_b = pixel_func(r, g, b)
                if not pixel_func == self.binarize_pixel:
                    blended_rgb = self.alpha_blending(r, g, b, res_r, res_g, res_b, self.alpha)
                    row.append(blended_rgb)
                else:
                    row.append([res_r, res_g, res_b])
            self.processed_picture.append(row)
            
        self.photo_processed = convert_matrix_to_photo(self.processed_picture)
        self.lbl_processed.config(image=self.photo_processed)

    def grayscale_pixel(self, r, g, b):
        gray = int((r + g + b) / 3)
        return [gray, gray, gray]

    def cmyk_pixel(self, r, g, b):
        c_val = 1 - (r / 255)
        m_val = 1 - (g / 255)
        y_val = 1 - (b / 255)
        
        tr = int(c_val * 255)
        tg = int(m_val * 255)
        tb = int(y_val * 255)
        return [tr, tg, tb]

    def yuv_pixel(self, r, g, b):
        y_val = 0.3 * r + 0.6 * g + 0.1 * b
        u_val = 0.74 * (r - y_val) + 0.27 * (b - y_val)
        v_val = 0.48 * (r - y_val) + 0.41 * (b - y_val)
        
        tr = max(0, min(255, int(y_val)))
        tg = max(0, min(255, int(u_val + 128)))
        tb = max(0, min(255, int(v_val + 128)))
        return [tr, tg, tb]

    def ycbcr_pixel(self, r, g, b):
        y_val = 0.299 * r + 0.587 * g + 0.114 * b
        cb_val = -0.1687 * r - 0.3313 * g + 0.498 * b + 128
        cr_val = 0.498 * r - 0.4187 * g - 0.0813 * b + 128
        
        tr = max(0, min(255, int(y_val)))
        tg = max(0, min(255, int(cb_val)))
        tb = max(0, min(255, int(cr_val)))
        return [tr, tg, tb]

    def binarize_pixel(self, r, g, b):
        threshold = self.alpha * 255
        p = int((r + g + b) / 3)
        bin_val = 255 if p > threshold else 0
        return [bin_val, bin_val, bin_val]

    def inverse(self, r, g, b):

        tr, tg, tb = 255 - r, 255 - g, 255 - b
        return [tr, tg, tb] 

    def apply_inverse_with_channels(self):
        self.process_pixels(self.inverse)
        
        self.current_operation = self.apply_inverse_with_channels
        
        inv_r_matrix, inv_g_matrix, inv_b_matrix = [], [], []
        
        for row in self.processed_picture:
            row_r, row_g, row_b = [], [], []
            for r, g, b in row:
                row_r.append([r, 0, 0])
                row_g.append([0, g, 0])
                row_b.append([0, 0, b])
            inv_r_matrix.append(row_r)
            inv_g_matrix.append(row_g)
            inv_b_matrix.append(row_b)

        if not hasattr(self, 'channels_window') or not self.channels_window.winfo_exists():
            self.channels_window = tk.Toplevel(self.root)
            self.channels_window.title("Inverse Channels")
            
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

    def real_histogram(self):
        hist = [0] * 256 
        h = len(self.loaded_picture)
        w = len(self.loaded_picture[0])
    
        for y in range(h):
            for x in range(w):
                intensity = self.get_intensity(*self.loaded_picture[y][x])
                hist[intensity] += 1 
            
        self.display_bar_chart(hist, "Histograma Reala")

    def compute_moments(self, order):
        if self.loaded_picture is None: return
        h = len(self.loaded_picture)
        w = len(self.loaded_picture[0])
            
        m00 = m10 = m01 = 0
        threshold = 127
        for y in range(h):
            for x in range(w):
                intensity = self.get_intensity(*self.loaded_picture[y][x])
                if intensity < threshold:
                    m00 += 1
                    m10 += x
                    m01 += y
                
        if m00 == 0: 
            print("Imaginea nu contine informatie obiectuala (M00 = 0).")
            return
            
        xc, yc = m10 / m00, m01 / m00
        
        if order == 1:
            print(f"Moment Ord 1: Aria(M00)={m00}, M10={m10}, M01={m01}")
            print(f"Centru de masa: ({xc:.2f}, {yc:.2f})")
        elif order == 2:
            m20 = m02 = m11 = 0
            for y in range(h):
                for x in range(w):
                    intensity = self.get_intensity(*self.loaded_picture[y][x])
                    if intensity < threshold:
                        m20 += x * x
                        m02 += y * y
                        m11 += x * y
            print(f"Moment Ord 2: M20={m20}, M02={m02}, M11={m11}")

    def compute_covariance(self):
        if self.loaded_picture is None: return
        h = len(self.loaded_picture)
        w = len(self.loaded_picture[0])
            
        m00 = m10 = m01 = 0
        threshold = 127
        for y in range(h):
            for x in range(w):
                intensity = self.get_intensity(*self.loaded_picture[y][x])
                if intensity > threshold:
                    m00 += 1
                    m10 += x
                    m01 += y
                
        if m00 == 0: return
        xc, yc = m10 / m00, m01 / m00
        
        mu20 = mu02 = mu11 = 0
        for y in range(h):
            for x in range(w):
                intensity = self.get_intensity(*self.loaded_picture[y][x])
                if intensity > threshold:
                    mu20 += (x - xc)**2
                    mu02 += (y - yc)**2
                    mu11 += (x - xc) * (y - yc)
                
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

    def get_binary_matrix(self, threshold=127):
        height = len(self.loaded_picture)
        width = len(self.loaded_picture[0])
        src_bin = []
        
        for i in range(height):
            row = []
            for j in range(width):
                r, g, b = self.loaded_picture[i][j]
                intensity = self.get_intensity(r, g, b)
                if intensity < threshold:
                    row.append(0)
                else:
                    row.append(255)
            src_bin.append(row)
            
        return src_bin

    def etichetare(self):
        if self.loaded_picture is None:
            return


        height = len(self.loaded_picture)
        width = len(self.loaded_picture[0])
        
        src_bin = self.get_binary_matrix()

        label = 0
        labels = [[0 for j in range(width)] for i in range(height)]

        for i in range(height):
            for j in range(width):
                
                col = src_bin[i][j]
                
                if col == 0 and labels[i][j] == 0:
                    label += 1
                    queue = []
                    labels[i][j] = label
                    queue.append([i, j])
                    
                    while len(queue) > 0:
                        q = queue.pop(0)
                        q0 = q[0]
                        q1 = q[1]
                        
                        for k in range(-1, 2):
                            for m in range(-1, 2):
                                if (q0 + k >= 0 and q0 + k < height) and (q1 + m >= 0 and q1 + m < width):
                                    try:
                                        ncol = src_bin[q0 + k][q1 + m]
                                        if ncol == 0 and labels[q0 + k][q1 + m] == 0:
                                            labels[q0 + k][q1 + m] = label
                                            queue.append([q0 + k, q1 + m])
                                    except Exception as ex:
                                        pass

        self.label_colors = {0: [255, 255, 255]} # fundal
        for l in range(1, label + 1):
            self.label_colors[l] = [random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)]

        self.labels = labels
        self.max_label = label

        self.processed_picture = []
        for i in range(height):
            row = []
            for j in range(width):
                row.append(self.label_colors[labels[i][j]])
            self.processed_picture.append(row)

        self.photo_processed = convert_matrix_to_photo(self.processed_picture)
        self.lbl_processed.config(image=self.photo_processed)
        print("Etichetare finalizata!")

    def calculateObjectOrientation(self, image_matrix, current_label):
        width = len(image_matrix[0])
        height = len(image_matrix)

        gradientX = [[0 for _ in range(height)] for _ in range(width)]
        gradientY = [[0 for _ in range(height)] for _ in range(width)]

        def getRGB_gray(x, y):
            r, g, b = image_matrix[y][x]
            return int((r + g + b) / 3)

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
                    g = int(sum(self.loaded_picture[i][j]) / 3)
                    row.append([g, g, g])
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
                p11 = self.get_intensity(*image_matrix[y-1][x-1])
                p12 = self.get_intensity(*image_matrix[y-1][x])
                p13 = self.get_intensity(*image_matrix[y-1][x+1])
                
                p21 = self.get_intensity(*image_matrix[y][x-1])
                p23 = self.get_intensity(*image_matrix[y][x+1])
                
                p31 = self.get_intensity(*image_matrix[y+1][x-1])
                p32 = self.get_intensity(*image_matrix[y+1][x])
                p33 = self.get_intensity(*image_matrix[y+1][x+1])
                
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
                    g = int(sum(self.loaded_picture[i][j]) / 3)
                    row.append([g, g, g])
            self.processed_picture.append(row)

        self.photo_processed = convert_matrix_to_photo(self.processed_picture)
        self.lbl_processed.config(image=self.photo_processed)

        orientation = self.calculateObjectOrientation_Global(self.loaded_picture, label_id)
        import math
        print(f"Obiectul cu eticheta {label_id} are orientarea: {math.degrees(orientation):.2f} grade")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()
