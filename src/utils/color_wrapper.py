class ColorWrapper:
    """
    A simple wrapper that converts a color string into an object with a get_rgba() method,
    which is required by PyCRAM.
    """
    def __init__(self, color_str):
        self.rgba = self.color_string_to_rgba(color_str)
    
    def color_string_to_rgba(self, color_str):
        mapping = {
            "red": (1.0, 0.0, 0.0, 1.0),
            "green": (0.0, 1.0, 0.0, 1.0),
            "blue": (0.0, 0.0, 1.0, 1.0),
            "yellow": (1.0, 1.0, 0.0, 1.0),
            "white": (1.0, 1.0, 1.0, 1.0),
            "black": (0.1, 0.1, 0.1, 1.0),
            "brown": (0.65, 0.32, 0.17, 1.0),
            "wood": (0.82, 0.70, 0.55, 1.0),   # warm oak
            "silver": (0.75, 0.75, 0.75, 1.0),
            "stone": (0.35, 0.35, 0.40, 1.0),  # dark countertop 
            "metal": (0.85, 0.85, 0.85, 1.0),  # stainless steel
            "accent": (0.50, 0.60, 0.50, 1.0), # sage green
            "accent2": (0.60, 0.50, 0.30, 1.0),# warm amber
            "gray": (0.70, 0.70, 0.70, 1.0),   # medium gray
            "wall": (0.90, 0.90, 0.90, 1.0),   # light grey
            # after (medium grey)
            "wall2":   (0.60, 0.60, 0.60, 1.0), 
            "ocean_blue": (0.00, 0.50, 0.70, 1.0), 
            "floor": (0.95, 0.95, 0.95, 1.0),  # very light grey
            
            # Add more colors as needed
        }
        return mapping.get(color_str.lower(), (1.0, 1.0, 1.0, 1.0))
    
    def get_rgba(self):
        return self.rgba
