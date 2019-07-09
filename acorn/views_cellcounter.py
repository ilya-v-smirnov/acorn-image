
import tkinter as tk
from tkinter import ttk
from .views import FramePanel, AssayView
from .models import CellCounterModel, ImageCorrectionCellCounterModel


class CellCounterParameters(FramePanel):
    """
    Creates a panel containing parameters for cell counting.
    """
    
    def __init__(self, parent,
                 **kwargs):
        super().__init__(parent, frame_model = CellCounterModel,
                         text='Cell Counting Parameters', **kwargs)
        self.frame_model.add_value_to_widgets(
                    ['binary_filter', 'mask_filter',
                     'offset_binary', 'offset_mask',
                     'min_dist', 'disk_radius',
                     'size_thresh'],
                     'width', 12)
        self.initiate_widgets()
        sticky_pad = {'sticky': tk.W+tk.E, 'padx': 5, 'pady': 2}                        
        self.widgets['binary_filter'].grid(row=0, column=0, **sticky_pad)
        self.widgets['offset_binary'].grid(row=0, column=1, **sticky_pad)
        self.widgets['mask_filter'].grid(row=0, column=2, **sticky_pad)
        self.widgets['offset_mask'].grid(row=0, column=3, **sticky_pad)
        self.widgets['min_dist'].grid(row=1, column=0, **sticky_pad)
        self.widgets['disk_radius'].grid(row=1, column=1, **sticky_pad)
        self.widgets['size_thresh'].grid(row=1, column=2, **sticky_pad)


class CellCounterView(AssayView):
    
    def __init__(self, parent, **kwargs):
        self.title = 'Cell Counter'
        self.additional_panel = CellCounterParameters
        self.img_titles = ['Corrected Image', 'Debris', 'Cells']
        self.img_filename_suffix = 'counter'
        self.image_correction_model = ImageCorrectionCellCounterModel
        super().__init__(parent, **kwargs)