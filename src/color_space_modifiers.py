from models import RGB
import math

def grayscale_pixel(rgb: RGB, **kwargs):
    gray = int((rgb.r + rgb.b + rgb.g) / 3)
    return RGB(gray, gray, gray)

def cmyk_pixel(rgb: RGB):
    cmy = rgb.apply(lambda p: 1 - (p / 255))
    cmy_normal = cmy.apply(lambda p: int(p * 255))
    return cmy_normal


def yuv_pixel(rgb: RGB):
    y_val = rgb.get_intensity() 
    u_val = 0.492 * (rgb.b - y_val)
    v_val = 0.877 * (rgb.r - y_val)

    tr = max(0, min(255, int(y_val)))
    tg = max(0, min(255, int(u_val + 128)))
    tb = max(0, min(255, int(v_val + 128)))
    
    return RGB(tr, tg, tb)

def ycbcr_pixel(rgb: RGB):
    y_val  =  0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b
    cb_val = -0.168736 * rgb.r - 0.331264 * rgb.g + 0.5 * rgb.b + 128
    cr_val =  0.5 * rgb.r - 0.418688 * rgb.g - 0.081312 * rgb.b + 128

    ycbcr = RGB(y_val, cb_val, cr_val)
    clamped_ycbcr = ycbcr.apply(lambda p: max(0, min(255, round(p))))
    
    return clamped_ycbcr

def binarize_pixel(rgb: RGB, threshold=127):
    intensity = rgb.get_intensity()
    bin_val = 255 if intensity > threshold else 0
    return RGB(bin_val, bin_val, bin_val)

def inverse(rgb: RGB):
        return rgb.apply(lambda p: 255 - p)
