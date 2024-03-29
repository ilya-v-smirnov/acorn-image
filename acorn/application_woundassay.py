 
import tkinter as tk
from .models import AppModel
from .views_woundassay import WoundAssayView
from .image_analysis import WoundImage
from matplotlib import use
from .accessory_functions import dict_identical, backend_switcher
from .button_commands_common import CommonButtonCommands
use("Agg")
 

class WoundAssayButtonCommands(CommonButtonCommands):
    """
    Adds specific functionality to the buttons of Wound Assay app.
    """

    def _select_image(self, img_path):
        result = False
        if img_path:
            result = super()._select_image(img_path, WoundImage)
        return result
        
    def _sub_apply(self):
        if self._select_image(self.get_image_path()):
            if not self.draw_progress:
                self.show_wait_window()
            input = self.get_input()
            self.image(**input)
            stat = self.image.get_stat()
            images = self.image.get_images()
            stat_text = "Wound Area: " + str(round(stat[0], 1)) + '%'
            self.set_image_row(images,
                        subtitles=['', '', stat_text],
                        img_mode=['P', 'RGB', 'RGB'])
            self.set_widgets({'channel': self.image.channel})
            if not self.draw_progress:
                self.destroy_wait_window()
            self.set_slider(50)
            self.grab_set()

class WoundAssay(WoundAssayButtonCommands, WoundAssayView):
    """
    Merges App view and button's functions.
    """

    def __init__(self, parent,
                 default_folder,
                 img_ext,
                 *args, **kwargs):
        WoundAssayView.__init__(self, parent,
                                default_folder=default_folder,
                                img_ext=img_ext,
                                *args, **kwargs)
        WoundAssayButtonCommands.__init__(self)