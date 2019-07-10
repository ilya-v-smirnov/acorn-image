 
import tkinter as tk
from .models import AppModel
from .views_cellcounter import CellCounterView
from .image_analysis import CellCounter
from matplotlib import use
from .accessory_functions import dict_identical, backend_switcher
from .button_commands_common import CommonButtonCommands
use("Agg")
 

class CellCounterButtonCommands(CommonButtonCommands):
    """
    Adds specific functionality to the buttons of Wound Assay app.
    """

    def _select_image(self, img_path):
        result = False
        if img_path:
            result = super()._select_image(img_path, CellCounter)
        return result
            
    def _apply(self):
        if self._select_image(self.get_image_path()):
            self._view_file()
            app_input = self.get_input()
            self.image(**app_input)
            stat = self.image.get_stat()
            if self.draw_gui:
                images = self.image.get_images()
                n_obj = 'Number of objects:' + str(stat[0])
                n_deb = 'Number of debris:' + str(stat[1])
                n_cells = 'Number of cells:' + str(stat[2])
                self.set_image_row(images,
                            subtitles=[n_obj, n_deb, n_cells],
                            img_mode=['P', 'P', 'RGB'])
                self.set_widgets({'channel': self.image.binary_im.channel})
            

class CellCounterApp(CellCounterButtonCommands, CellCounterView):
    """
    Merges App view and button's functions.
    """

    def __init__(self, parent,
                 default_folder,
                 img_ext,
                 *args, **kwargs):
        CellCounterView.__init__(self, parent,
                                default_folder=default_folder,
                                img_ext=img_ext,
                                *args, **kwargs)
        CellCounterButtonCommands.__init__(self)