 
import tkinter as tk
from .models import AppModel
from .views_woundassay import WoundAssayView
from .image_analysis import WoundImage
from matplotlib import use
from .accessory_functions import dict_identical, backend_switcher
use("Agg")
 

class ButtonCommands:
    """
    Adds functionality to the buttons of ButtonPanel.
    """
    
    def __init__(self):
        self.image = None
        self.result = []
        self.draw_gui = True
        
    def _select_image(self, img_path):
        if img_path:
            self.image = WoundImage(img_path)
            return True
        else:
            return False
        
    def _view_file(self):
        if self._select_image(self.get_image_path()):
            self.set_image(self.image.get_PILimg())
        
    def _apply(self):
        if self._select_image(self.get_image_path()):
            self._view_file()
            input = self.get_input()
            self.image(**input)
            stat = self.image.get_stat()
            if self.draw_gui:
                images = self.image.get_images()
                stat_text = "Wound Area: " + str(round(stat[0], 1)) + '%'
                self.set_image_row(images,
                            subtitles=['', '', stat_text])
                self.set_widgets({'channel': self.image.channel})
    
    def _next(self):
        self.next_file()
        self._apply()
        
    def _image_saver(self):
        save = self.get_save_images_status()
        if save:
            basename = self.get_file_name(with_ext=False)
            self.save_image(self.image.get_wound_img(), basename)
        
    def _add_to_report(self):
        if self.image:
            filename = {'file': self.image.get_image_path()}
            arguments = self.image.called_with()
            area, width = self.image.get_stat()
            row = {**filename,
                   **arguments,
                   'wound_area': round(area, 2),
                   'wound_width': round(width, 2)}
            if len(self.result) == 0:
                self.result.append(row)
                self._image_saver()
            if not dict_identical(row, self.result[-1]):
                self.result.append(row)
                self._image_saver()
    
    def _apply_all(self):
        if self._select_image(self.get_first_image()):
            
            image_files = self.get_images()
            n_files = len(image_files)
            if n_files > 1:
                self.draw_gui = False
                for i in range(n_files-1):
                    self._apply()
                    self._add_to_report()
                    self.next_file()
                self.draw_gui = True
            self._apply()
            self._add_to_report()
    
    def _clear_report(self):
        self.result.clear()
        self.set_default_images()
    
    @backend_switcher
    def _view_images(self):
        if not self.image is None:
            self.image.view_images()
        
    def _save_report(self):
        if len(self.result) > 0:
            super()._save_report(report=self.result,
                        dirName=self.get_path_wd())
    
    def _view_report(self):
        if len(self.result) > 0:
            super()._view_report(self.result)
            

class WoundAssay(ButtonCommands, WoundAssayView):
    """
    Merges App view and button's functions.
    """

    def __init__(self, parent,
                 default_folder,
                 img_ext,
                 *args, **kwargs):
        WoundAssayView.__init__(self, parent,
                                default_folder, img_ext,
                                *args, **kwargs)
        ButtonCommands.__init__(self)


class AcornImage(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Acorn Image')
        self.resizable(width=False, height=False)
        self.app_model = AppModel()
        self.woundassay = WoundAssay(self, **self.app_model())
        self.woundassay.pack()

        