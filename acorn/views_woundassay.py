
import tkinter as tk
from tkinter import ttk
from . import views as v
from .models import WoundParametersModel

class WoundParameters(v.FramePanel):
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
        

class WoundAssayView(v.ButtonPanel, tk.Frame):
    """
    Arranges app layout and adds buttons.
    """
    
    def __init__(self, parent,
                 default_folder,
                 img_ext,
                 *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        v.ButtonPanel.__init__(self, self)
        sticky_pad = {'sticky':tk.W+tk.E, 'padx':5, 'pady':2}
        ttk.Label(self, text="Wound assay",
                  font=("TkDefaultFont", 16)
                  ).grid(row=0, columnspan=2)
        left_panel = tk.Label(self)
        self.file_manager = v.FileManager(left_panel,
                                          default_folder,
                                          img_ext)
        self.image_correction = v.ImageCorrection(left_panel)
        self.wound_pars = WoundParameters(left_panel)
        self.input_panels = [self.file_manager,
                             self.image_correction,
                             self.wound_pars]
        for i, panel in enumerate(self.input_panels):
            panel.grid(row=i, column=0, **sticky_pad)
        left_panel.grid(row=1, column=0, rowspan=3)
        self.img_view = v.ImageView(self,
                                img=None, res=(360, 240),
                                padx=30, pady=10)
        self.img_view.grid(row=1, column=1,
                           columnspan=2, rowspan=2,
                           sticky=tk.W+tk.E+tk.N)
        self.image_row = v.ImageRow(self,
                        images = [None, None, None],
                        titles = ['Corrected Image',
                                  'Image Slice',
                                  'Outlined Wound'],
                        subtitles = ['', '', ''],
                        res = (300, 200))
        self.image_row.grid(row=4, column=0,
                            columnspan=2,
                            **sticky_pad)
        self.grid_button_frame(row=3, column=1)
        
    def set_image(self, image):
        self.img_view.configure(image)
        
    def set_image_row(self, images, subtitles):
        self.image_row.configure_images(images)
        self.image_row.configure_subtitles(subtitles)
        
    def get_input(self):
        app_input = {}
        for panel in self.input_panels:
            app_input = {**app_input, **panel.get_input()}
        return app_input
        
    def get_image_path(self):
        return self.file_manager.get_image_path()
        
    def get_path_wd(self):
        return self.file_manager.get_path_wd()
        
    def next_file(self):
        self.file_manager.next_file()
        
    def get_first_image(self):
        return self.file_manager.get_first_image()
        
    def set_widgets(self, widget_values):
        self.image_correction.set_widgets(widget_values)
        self.wound_pars.set_widgets(widget_values)
        
    def get_images(self):
        return self.file_manager.get_images()
        
    def get_file_name(self, *args, **kwargs):
        return self.file_manager.get_file_name(*args, **kwargs)
        
    def get_save_images_status(self):
        return self.file_manager.get_save_images_status()
        
    def save_image(self, img, name, ext='jpg'):
        self.file_manager.save_image(img=img,
                    folder=self.file_manager.get_path_wd(),
                    name=name, suffix = 'wound',
                    ext=ext)
                    
    def set_default_images(self):
        self.img_view.set_default_image()
        self.image_row.set_default_images()

