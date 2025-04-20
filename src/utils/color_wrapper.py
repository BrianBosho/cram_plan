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
            "black": (0.0, 0.0, 0.0, 1.0),
            "brown": (0.65, 0.32, 0.17, 1.0),
            "wood": (0.72, 0.53, 0.04, 1.0),
            "silver": (0.75, 0.75, 0.75, 1.0),
            # Add more colors as needed
        }
        return mapping.get(color_str.lower(), (1.0, 1.0, 1.0, 1.0))
    
    def get_rgba(self):
        return self.rgba
