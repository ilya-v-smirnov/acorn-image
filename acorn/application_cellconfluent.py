
import tkinter as tk
from .models import AppModel
from .views_cellconfluent import CellConfluentAssayView
from .image_analysis import CellConfluent
from matplotlib import use
from .accessory_functions import dict_identical, backend_switcher
from .button_commands_common import CommonButtonCommands
use("Agg")
 

class CellConfluentButtonCommands(CommonButtonCommands):
    """
    Adds specific functionality to the buttons of Cell Confluent App.
    """

    def _select_image(self, img_path):
        result = False
        if img_path:
            result = super()._select_image(img_path, CellConfluent)
        return result
        
    def _apply(self):
        if self._select_image(self.get_image_path()):
            if not self.draw_progress:
                self.show_wait_window()
            self._view_file()
            input = self.get_input()
            self.image(**input, border_size=1)
            stat = self.image.get_stat()
            images = self.image.get_images()
            stat_text = "Cell Confluent: " + str(round(stat, 1)) + '%'
            self.set_image_row(images,
                        subtitles=['', '', stat_text],
                        img_mode=['P', 'RGB', 'RGB'])
            self.set_widgets({'channel': self.image.channel})
            self._after_apply()
            if not self.draw_progress:
                self.destroy_wait_window()
            self.set_slider(50)
            self.grab_set()

class CellConfluentAssay(CellConfluentButtonCommands, CellConfluentAssayView):
    """
    Merges App view and button's functions.
    """

    def __init__(self, parent,
                 default_folder,
                 img_ext,
                 *args, **kwargs):
        CellConfluentAssayView.__init__(self, parent,
                                        default_folder=default_folder,
                                        img_ext=img_ext,
                                        *args, **kwargs)
        CellConfluentButtonCommands.__init__(self)