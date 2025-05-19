from PIL import Image, ImageTk, ImageFilter
import tkinter as tk

# Base class for backgrounds
class BaseBackground:
    def __init__(self, root, image_path):
        self._root = root
        self._image_path = image_path
        self._photo = None
        self._label = None

    def set_background(self):
        """To be overridden by subclasses"""
        raise NotImplementedError("Method must be overridden in subclass")

    def get_label(self):
        return self._label


# Subclass: Blurred background implementation
class BlurredBackground(BaseBackground):
    def set_background(self):  # Overriding
        # Load and resize image
        image = Image.open(self._image_path)
        screen_width = self._root.winfo_screenwidth()
        screen_height = self._root.winfo_screenheight()
        image = image.resize((screen_width, screen_height))

        # Apply blur
        blurred = image.filter(ImageFilter.GaussianBlur(radius=5))

        # Convert to Tkinter-compatible image
        self._photo = ImageTk.PhotoImage(blurred)

        # Create label and place it
        self._label = tk.Label(self._root, image=self._photo)
        self._label.image = self._photo  # keep reference
        self._label.place(x=0, y=0, relwidth=1, relheight=1)

