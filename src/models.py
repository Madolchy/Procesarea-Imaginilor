class RGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        
    def get_intensity(self):
        return int(0.299 * self.r + 0.587 * self.g + 0.114 * self.b)

    def apply(self, func):
        return RGB(func(self.r), func(self.g), func(self.b))

    def alpha_blending(self, rgb_target, alpha):
        inverse_alpha = 1 - alpha
        return RGB(
            int(self.r * inverse_alpha + rgb_target.r * alpha),
            int(self.g * inverse_alpha + rgb_target.g * alpha),
            int(self.b * inverse_alpha + rgb_target.b * alpha)
        )
        
    def __truediv__(self, other):
        return RGB(
            int(self.r / other),
            int(self.g / other),
            int(self.b / other)
        )
        
    def __iter__(self):
        yield self.r
        yield self.g
        yield self.b
    