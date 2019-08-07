
import tkinter as tk
from .views import FramePanel
from .models import BorderPropertiesModel
from tkinter.colorchooser import askcolor

class BorderProperties(FramePanel):

    sticky_pad = {'sticky': tk.W+tk.E+tk.N+tk.S,
                  'padx': 5, 'pady': 5}

    def __init__(self, parent, frame_model=BorderPropertiesModel,
                border_color=None, border_size=None,
                *args, **kwargs):
        self.border_color = border_color
        super().__init__(parent, text='Border Properties',
                                frame_model=frame_model, *args, **kwargs)
        if not border_color:
            border_color = (255, 0, 0)
        if border_size:
            self.frame_model.add_value_to_widgets(['border_size'],
                                'default', int(border_size))
        self.frame_model.add_value_to_widgets(['border_size'], 'width', 12)
        self.initiate_widgets()
        self.widgets['border_size'].grid(row=0, column=0, **self.sticky_pad)
        choose_color_but = tk.Button(self, text='Choose Border\nColor',
                                command=self._choose_color)
        choose_color_but.grid(row=1, column=0, **self.sticky_pad)

    def _choose_color(self):
        RGB, _ = askcolor(color=self.border_color,
                                title='Choose Border Color',
                                parent=self)
        if RGB: # not None
            self.border_color = tuple([int(x) for x in RGB])


# class ImageSavingProperties(FramePanel):

#     sticky_pad = {'sticky': tk.W+tk.E+tk.N+tk.S,
#                   'padx': 5, 'pady': 5}

#     def __init__(self, parent, frame_model=ImageSavingPropertiesModel,
#                  save_int_images=None,
#                  *args, **kwargs):
#         super().__init__(parent, text='Image Saving',
#                                 frame_model=frame_model,
#                                 *args, **kwargs)
#         if save_int_images:
#             self.frame_model.add_value_to_widgets(['save_int_images'],
#                                 'default', save_int_images)
#         self.initiate_widgets()
#         self.widgets['save_int_images'].grid(row=0, column=0,
#                                 **self.sticky_pad)


class AdditionalPropertis(tk.Toplevel):
    
    sticky_pad = {'sticky': tk.W+tk.E+tk.N+tk.S,
                  'padx': 5, 'pady': 2}

    def __init__(self, parent,
                border_size=None, border_color=None,
                *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        super().title('Additional Properties')
        super().resizable(width=False, height=False)
        super().grab_set()
        self.parent = parent
        title_lab = tk.Label(self, text='Additional Properties',
                                font=("TkDefaultFont", 14))
        title_lab.grid(row=0, column=0, columnspan=3, **self.sticky_pad)
        self.bord_prop = BorderProperties(self, border_size=border_size,
                                border_color=border_color)
        self.bord_prop.grid(row=1, column=0, **self.sticky_pad)
        # self.img_save_prop = ImageSavingProperties(self,
        #                         save_int_images=save_int_images)
        # self.img_save_prop.grid(row=1, column=1, **self.sticky_pad)
        button_frame = tk.Frame(self)
        button_frame.grid(row=2, column=2, **self.sticky_pad)
        ok_button = tk.Button(button_frame, text='   OK   ', command=self._ok_cmd)
        ok_button.grid(row=0, column=0, **self.sticky_pad)
        cancel_button = tk.Button(button_frame, text='Cancel', command=self._cancel_cmd)
        cancel_button.grid(row=0, column=1, **self.sticky_pad)
    
    def _ok_cmd(self):
        self.parent.input_panels.append(self)
        self._cancel_cmd()

    def _cancel_cmd(self):
        self.destroy()
        self.parent.grab_set()

    def get_input(self):
        panels = [self.bord_prop, self.img_save_prop]
        inp = dict()
        for p in panels:
            inp = {**inp, **p.get_input()}
        return inp
