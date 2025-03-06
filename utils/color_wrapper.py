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
            # Add more colors as needed
        }
        return mapping.get(color_str.lower(), (1.0, 1.0, 1.0, 1.0))
    
    def get_rgba(self):
        return self.rgba
