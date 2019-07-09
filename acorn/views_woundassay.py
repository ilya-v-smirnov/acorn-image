
import tkinter as tk
from tkinter import ttk
from .views import FramePanel, AssayView
from .models import WoundParametersModel, ImageCorrectionWoundAssayModel


class WoundParameters(FramePanel):
    """
    Creates a panel containing parameters for wound size estimation.
    """
    
    def __init__(self, parent,
                 **kwargs):
        super().__init__(parent, frame_model = WoundParametersModel,
                         text='Wound Parameters', **kwargs)
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
        

class WoundAssayView(AssayView):
    
    def __init__(self, parent, **kwargs):
        self.title = 'Wound Assay'
        self.additional_panel = WoundParameters
        self.img_titles = ['Corrected Image', 'Image slice', 'Outlined wound']
        self.img_filename_suffix = 'wound'
        self.image_correction_model = ImageCorrectionWoundAssayModel
        super().__init__(parent, **kwargs)
