class RGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        
    def get_intensity(self):
        return int(0.299 * self.r + 0.587 * self.g + 0.114 * self.b)