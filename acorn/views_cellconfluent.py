
import tkinter as tk
from tkinter import ttk
from .views import FramePanel, AssayView
from .models import CellConfluentModel, ImageCorrectionCellConfluent
from PIL import Image


class CellConfluentParameters(FramePanel):
    """
    Creates a panel containing parameters for wound size estimation.
    """
    
    def __init__(self, parent,
                 **kwargs):
        super().__init__(parent, frame_model = CellConfluentModel,
                         text='Cell Confluent Parameters', **kwargs)
        self.frame_model.add_value_to_widgets(['mode', 'filt',
                                         'offset', 'disk_radius',
                                         'min_wound', 'min_objects'],
                                         'width', 12)
        self.initiate_widgets()
        sticky_pad = {'sticky': tk.W+tk.E, 'padx': 5, 'pady': 2}                        
        self.widgets['mode'].grid(row=0, column=0, **sticky_pad)
        self.widgets['filt'].grid(row=0, column=1, **sticky_pad)
        self.widgets['offset'].grid(row=0, column=2, **sticky_pad)
        self.widgets['equal_exposure'].grid(row=0, column=3,
                                sticky=tk.W+tk.S, padx=5, pady=2) 
        self.widgets['disk_radius'].grid(row=1, column=0, **sticky_pad)
        self.widgets['min_wound'].grid(row=1, column=1, **sticky_pad)
        self.widgets['min_objects'].grid(row=1, column=2, **sticky_pad)
        

class CellConfluentAssayView(AssayView):
    
    def __init__(self, parent, **kwargs):
        self.title = 'Cell Confluent'
        self.additional_panel = CellConfluentParameters
        self.img_titles = ['Corrected Image', 'Image Slice', 'Outlined Cells']
        self.img_scales = [True, False, False]
        self.img_filename_suffix = 'confluent'
        self.image_correction_model = ImageCorrectionCellConfluent
        super().__init__(parent, **kwargs)
        self.image_row.buttons[0].slider_respond = self.slider_respond
    
    def slider_respond(self, position):
        if self.image:
            plot = self.image.get_image_slice(int(position))
            self.configure_plot(Image.fromarray(plot))
            self.update_idletasks()

    def configure_plot(self, img):
        self.image_row.buttons[1].configure_image_button(img)

    def set_slider(self, position):
        self.image_row.buttons[0].set_slider(position)
        