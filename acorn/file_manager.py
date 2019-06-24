
import os
import tkinter as tk
from tkinter import ttk
from .accessory_functions import limit_text, save_image, file_namer

class ImageFileMixin:
    """
    Adds functionality to file manager panel
    """
    
    def __init__(self, path, img_ext, *args,
                 recursive=False, **kwargs):
        self.path = path
        self.img_ext = img_ext
        self.recursive = recursive
        self.images = []
        self.first_img = None
        self._find_images()
    
    @staticmethod
    def _fext(filename):
        """Returns file extension"""
        return os.path.splitext(filename)[-1].lower()
    
    def _find_images(self):
        files = os.listdir(self.path)
        if self.recursive:
            for folder, subfolder, files in os.walk(self.path):
                for f in files:
                    if self._fext(f) in self.img_ext:
                        fp = os.path.join(folder, f)
                        fp = fp.replace(self.path + "\\", "")
                        self.images.append(fp)
        else:
            for f in files:
                if self._fext(f) in self.img_ext:
                    self.images.append(f)
        self.first_img = None
        if len(self.images) > 0:
            self.first_img = self.images[0]
  
    def get_images(self):
        return self.images
        
    def get_first_image(self):
        if len(self.images) > 0:
            return os.path.join(self.path, self.images[0])
        else:
            return None
        
    def get_path_wd(self):
        return self.path_wd

    @staticmethod
    def save_image(img, folder, name, suffix, ext='jpg'):
        abs_path = file_namer(folder, basename=name, suffix=suffix, ext=ext)
        save_image(img, abs_path)
            
