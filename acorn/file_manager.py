
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
        self.images = list()
        self._find_images()
        self.image_index = 0
        self.current_image = self.set_current_image()
  
    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, path):
        if not path or not os.path.exists(path): # None or not exists
            self.__path = os.getcwd()
        else:
            self.__path = path

    @property
    def image_index(self):
        return self.__image_index

    @image_index.setter
    def image_index(self, index):
        if index < 0:
            self.__image_index = 0
        elif index + 1 > len(self.images) and not len(self.images) == 0:
            self.__image_index = len(self.images) - 1
        else:
            self.__image_index = index

    def set_current_image(self):
        if len(self.images) == 0:
            return None
        return self.images[self.image_index]

    def _next_file(self):
        self.image_index += 1
        self.current_image = self.images[self.image_index]

    def _previous_file(self):
        self.image_index -= 1
        self.current_image = self.images[self.image_index]

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
        
    @staticmethod
    def save_image(img, folder, name, suffix, ext='jpg'):
        abs_path = file_namer(folder, basename=name, suffix=suffix, ext=ext)
        save_image(img, abs_path)
            
