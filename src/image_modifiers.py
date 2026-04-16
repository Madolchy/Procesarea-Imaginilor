import random

from models import RGB




def calculate_histogram(image, h, w):
    hist = [0] * 256 
    for y in range(h):
        for x in range(w):
            intensity = image[y][x].get_intensity()
            hist[intensity] += 1 
            
    return hist


def equalize_histogram(image, h, w):
    histogram = calculate_histogram(image, h, w)

    hc = [0] * 256
    hc[0] = histogram[0]
    for i in range(1, 256):
        hc[i] = hc[i - 1] + histogram[i]

    result = []
    for i in range(h):
        row = []
        for j in range(w):
            nivel = image[i][j].get_intensity()
            nivel_nou = int((hc[nivel] - hc[0]) * 255 / (w * h - hc[0]))
            row.append(RGB(nivel_nou, nivel_nou, nivel_nou))
        result.append(row)

    return result


def eroziune(image, h, w):
    src_bin = get_binary_matrix(image, h, w)

    result = []
    for i in range(h):
        row = []
        for j in range(w):
            val = 255
            for k in range(-1, 2):
                for m in range(-1, 2):
                    if 0 <= i + k < h and 0 <= j + m < w:
                        if src_bin[i + k][j + m] == 0:
                            val = 0
            row.append(RGB(val, val, val))
        result.append(row)

    return result


def dilatare(image, h, w):
    src_bin = get_binary_matrix(image, h, w)

    result = []
    for i in range(h):
        row = []
        for j in range(w):
            val = 0
            for k in range(-1, 2):
                for m in range(-1, 2):
                    if 0 <= i + k < h and 0 <= j + m < w:
                        if src_bin[i + k][j + m] == 255:
                            val = 255
                    else:
                        val = 255
            row.append(RGB(val, val, val))
        result.append(row)

    return result


def compute_first_order( image:list[RGB], h, w, threshold = 127):
    m00 = m10 = m01 = 0
    
    for y in range(h):
        for x in range(w):
            i = image[y][x].get_intensity()
            weight = 1 if i < threshold else 0

            m00 += weight
            m10 += x * weight
            m01 += y * weight
    
    return (m00, m10, m01)

def compute_centru_masa( image:list[RGB], h, w):
    m00, m10, m01 = compute_first_order(image, h, w)
    return (m10 / m00, m01 / m00)

def compute_second_order( image:list[RGB], h, w):
    m20 = m02 = m11 = 0
    for y in range(h):
        for x in range(w):
            i = image[y][x].get_intensity()
            m20 += x * x * i
            m02 += y * y * i
            m11 += x * y * i
    
    return (m20, m02, m11)

def display_first_order(image: list[RGB], h, w):
    xc, yc = compute_centru_masa(image, h, w)
    xc, yc = int(xc), int(yc)


    for y in range(int(yc - 2), yc + 3):
        for x in range(xc - 2, xc + 3):
            
            if 0 <= y < h and 0 <= x < w:
                image[y][x] = RGB(255, 0, 0)
    return image


def compute_covariance(image: list[RGB], h, w, threshold = 127):
    m00 = m10 = m01 = compute_first_order(image, h, w)
    xc, yc = m10 / m00, m01 / m00
    
    mu20 = mu02 = mu11 = 0
    for y in range(h):
        for x in range(w):
            intensity = image[y][x].get_intensity()
            if intensity > threshold:
                mu20 += (x - xc)**2
                mu02 += (y - yc)**2
                mu11 += (x - xc) * (y - yc)
            
    cov20, cov02, cov11 = mu20 / m00, mu02 / m00, mu11 / m00
    print(f"Matricea de Covarianta:\n[{cov20:.2f}, {cov11:.2f}]\n[{cov11:.2f}, {cov02:.2f}]")

def compute_projections(image: list[RGB], h, w):
    proj_h = [0] * h
    proj_v = [0] * w
      
    for y in range(h):
        for x in range(w):
            I = image[y][x].get_intensity()
            proj_h[y] += I
            proj_v[x] += I

    return (proj_h, proj_v)              

def get_binary_matrix(image: list[RGB], h, w, threshold=127):
    src_bin = []
    
    for y in range(h):
        row = []
        for x in range(w):
            pixel = image[y][x]
            intensity = pixel.get_intensity()
            if intensity < threshold:
                row.append(0)
            else:
                row.append(255)
        src_bin.append(row)
        
    return src_bin

def etichetare(image, height, width):
    src_bin = get_binary_matrix(image, height, width)

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

    label_colors = {0: RGB(255, 255, 255)} # fundal
    for l in range(1, label + 1):
        label_colors[l] = RGB(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

    labels = labels
    max_label = label

    result = []
    for i in range(height):
        row = []
        for j in range(width):
            row.append(label_colors[labels[i][j]])
        result.append(row)

    return result