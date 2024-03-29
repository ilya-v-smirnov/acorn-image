
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image
from . import widgets as w
from .models import FileManagerModel, ImageCorrectionDefaultModel
import os
from .file_manager import ImageFileMixin
from .accessory_functions import save_csv, limit_text


class FramePanel(tk.LabelFrame):
    """
    Provides additional functionality to LabelFrames.
    """
    
    def __init__(self, parent, frame_model, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.frame_model = frame_model()
        self.widgets = {}
    
    def initiate_widgets(self):
        scheme = self.frame_model()
        for widget, pars in scheme.items():
            self.widgets[widget] = w.LabeledWidget(self, **pars)
    
    def get_input(self):
        keys = self.widgets.keys()
        d = dict()
        for k in keys:
            d[k] = self.widgets[k].get()
        return d
        
    def set_widgets(self, widget_values):
        for key, value in widget_values.items():
            if not self.widgets.get(key) is None:
                self.widgets[key].set(value)


class FilePathLabel(ttk.Label):
    """
    Makes folder path length no longer then limit.
    Configure method allows to change text in the widget.
    """
    
    def __init__(self, parent, path,
                 limit, begin, **kwargs):
        self.path = path
        self.limit = limit
        self.begin = begin
        self.text = self._make_limited()
        super().__init__(parent, text=self.text)
    
    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, path):
        if path is None:
            self.__path = os.getcwd()
        elif os.path.exists(path):
            self.__path = path
        else:
            raise ValueError('Wrong path')
        self.__path = self.path.replace('/', '\\')
    
    def _make_limited(self):
        return limit_text(self.__path, self.limit, self.begin)
    
    def configure(self, path):
        self.path = path
        self.text = self._make_limited()
        super().configure(text=self.text)
    
    
class FileManager(ImageFileMixin, FramePanel):
    """
    File Manager is able to choose image containing directory and
    working directory to save images and report.
    """

    sticky_pad = {'sticky': tk.W+tk.E, 'padx': 5, 'pady': 1}

    def __init__(self, parent,
                 path=None, img_ext=None):
        self.path = path
        FramePanel.__init__(self, parent,
                            text='File Manager',
                            frame_model=FileManagerModel)
        ImageFileMixin.__init__(self, path=path,
                                img_ext=img_ext)
        self.path_wd = self.path                        
        self.frame_model.add_value(widget='recursive',
                                key='command',
                                value=self._recursive)
        self.initiate_widgets()
        ttk.Label(self, text='Path to images:'
                                ).grid(row=0, column=0,
                                **self.sticky_pad)        
        self.path_to_images = FilePathLabel(self,
                                path=self.path,
                                limit=50, begin=20)
        self.path_to_images.grid(row=1, column=0, columnspan=2,
                                **self.sticky_pad)
        self.widgets['file'] = w.LabeledWidget(self,
                                type='combobox', text_label='File:',
                                default=self.current_image,
                                values=self.images,
                                width=50)
        self.widgets['file'].grid(row=2, column=0,
                                columnspan=2,
                                **self.sticky_pad)
        self.path_to_wd = FilePathLabel(self,
                                path=self.path_wd,
                                limit=50, begin=20)
        self.path_to_wd.grid(row=4, column=0,
                             columnspan=2,
                             **self.sticky_pad)
        but_browse1 = ttk.Button(self, text="Browse",
                                 command=self._browse_button1)        
        ttk.Label(self,
                 text='Path to working directory:'
                 ).grid(row=3, column=0,
                 **self.sticky_pad)
        self.recursive = False
        self.widgets['recursive'].grid(row=3, column=1,
                                **self.sticky_pad)
        self.widgets['save_images'].grid(row=5, column=0,
                                sticky=tk.W, padx=5)          
        but_browse1.grid(row=1, column=2, **self.sticky_pad)
        but_browse2 = ttk.Button(self, text="Browse",
                                 command=self._browse_button2)
        but_browse2.grid(row=4, column=2, **self.sticky_pad)
        
    def _browse_button1(self):
        chosen_path = filedialog.askdirectory(parent=self,
                                initialdir=self.path)
        if chosen_path != '':
            self.path = chosen_path
            self.path_to_images.configure(path=self.path)
            self.images.clear()
            self._find_images()
            self.widgets['file'].set(self.first_img)
            self.widgets['file'].configure(values=self.images)
            self.select_first_image()
            self.configure_buttons()
 
    def select_first_image(self):
        pass
        
    def _browse_button2(self):
        chosen_path = filedialog.askdirectory(parent=self,
                                initialdir=self.path_wd)
        if chosen_path != '':
            self.path_wd = chosen_path
            self.path_to_wd.configure(path=self.path_wd)
        
    def _recursive(self):
        self.recursive = self.widgets['recursive'].get()
        self.images.clear()
        self._find_images()
        self.image_index = 0
        self.set_current_image()
        self.widgets['file'].set(self.first_img)
        self.widgets['file'].configure(values=self.images)
        self.configure_buttons()
        self.select_first_image()

    def get_image_path(self):
        fileName = self.widgets['file'].get()
        if fileName == 'None':
            return None
        return os.path.join(self.path, fileName)
        
    def next_file(self):
        self._next_file()
        self.widgets['file'].set(self.current_image)

    def previous_file(self):
        self._previous_file()
        self.widgets['file'].set(self.current_image)
                    
    def get_file_name(self, with_ext=True):
        file_name = self.widgets['file'].get()
        if with_ext:
            return file_name
        return os.path.splitext(file_name)[0]

    def set_file_name(self):
        filename = os.path.basename(self.images[self.image_index])
        self.widgets['file'].set(filename)
        
    def get_save_images_status(self):
        return self.widgets['save_images'].get()

    def configure_buttons(self):
        pass

    def get_path_wd(self):
        return self.path_wd

    def set_first_image(self):
        self.image_index = 0
        self.set_current_image()
        self.set_file_name()
               
       
class ImageCorrection(FramePanel):
    """
    Creates a panel for image correction.
    """
    
    def __init__(self, parent, frame_model=ImageCorrectionDefaultModel,
                 *args, **kwargs):
        super().__init__(parent, text="Image Correction",
                         frame_model=frame_model,
                         *args, **kwargs)
        self.frame_model.add_value_to_widgets(['channel', 'bright',
                                         'contr', 'blur_radius'], 
                                         'width', 12)
        self.initiate_widgets()
        sticky_pad = {'sticky': tk.W+tk.E, 'padx': 5, 'pady': 1}
        self.widgets['channel'].grid(row=0, column=0, **sticky_pad)
        self.widgets['bright'].grid(row=0, column=1, **sticky_pad)
        self.widgets['contr'].grid(row=0, column=2, **sticky_pad)
        self.widgets['blur_radius'].grid(row=0, column=3, **sticky_pad)
        self.widgets['inverse'].grid(row=1, column=0, **sticky_pad)
        

class ImageView(tk.Frame):
    """
    Creates a widget showing selected image.
    """
    
    def __init__(self, parent,
                 img=None, res=(300, 200),
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.img_button = w.ImageButton(self, img, res=res)
        self.img_button.grid(row=0, column=0, **kwargs)
        
    def configure(self, PILimg, *args, **kwargs):
        self.img_button.configure_image_button(PILimg,
                        *args, **kwargs)
                        
    def set_default_image(self):
        self.img_button.set_default_image()
        

class ImageRow(tk.Frame):
    """
    Creates three image-buttons showing image processing results.
    """
    
    def __init__(self, parent, images,
                 titles, subtitles, res,
                 scales,
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.buttons = []
        self.subtitles = subtitles
        self.sub_labels = []
        sticky_pad = {'sticky': tk.E, 'padx': 5, 'pady': 5}
        pars = zip(images, scales, titles, self.subtitles)
        for i, (img, scale, title, subtitl) in enumerate(pars):
            ttk.Label(self, text=title,
                     font=("TkDefaultFont", 12)).grid(row=0, column=i)
            if scale:
                self.buttons.append(w.ImageButtonWithScale(self, img, res))
            else:
                self.buttons.append(w.ImageButton(self, img, res))
            self.buttons[i].grid(row=1, column=i, **sticky_pad)
            self.sub_labels.append(ttk.Label(self,
                                   text=subtitl, font=("TkDefaultFont", 12)))
            self.sub_labels[i].grid(row=2, column=i)

    def configure_subtitles(self, subtitles):
        for sub, lab in zip(subtitles, self.sub_labels):
            lab.configure(text=sub)
            
    def configure_images(self, images, img_mode=None):
        if not img_mode:
            img_mode = ('RGB',) * 3
        for img, but, mod in zip(images, self.buttons, img_mode):
            PILimg = Image.fromarray(img, mod)
            but.configure_image_button(PILimg)
            
    def set_default_images(self):
        for button in self.buttons:
            button.set_default_image()


class TableView(tk.Toplevel):
    """
    Creates a table widget to show results.
    """
    
    def __init__(self, parent, table, columns=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.grab_set()
        self.title = 'Report'
        self.table = table
        self.columns = columns or list(self.table[0].keys())
        self.tree = ttk.Treeview(self, columns=self.columns)
        self.tree['show'] = 'headings'
        self._make_columns()
        self._make_rows()
        self._fill_table()
        scroll_y = tk.Scrollbar(self, orient=tk.VERTICAL,
                                command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        scroll_x = tk.Scrollbar(self, orient=tk.HORIZONTAL,
                                command=self.tree.xview)
        self.tree.configure(xscrollcommand=scroll_x.set)
        
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def _make_columns(self):
        for col in self.columns:
            self.tree.column(col, width=75, minwidth=75, stretch=True)
            self.tree.heading(col, text=col, anchor=tk.CENTER)
    
    def _make_rows(self):
        index = 0
        for row in self.table:
            self.tree.insert(parent='', index=index, iid=None)
            index += 1

    def _fill_table(self):
        for row, item in zip(self.table, self.tree.get_children()):
            for col in self.columns:
                self.tree.set(item=item, column=col, value=row.get(col))


class ButtonPanel:
    """
    Creats a panel containing buttons.
    """

    sticky_pad = {"sticky": tk.W+tk.E, "padx": 5, "pady": 2}

    def __init__(self, parent, *args, **kwargs):
        self.button_frame = tk.Frame(parent,  *args, **kwargs)
        self.buttons = list()
        apply_button = tk.Button(self.button_frame,     # 0
                                text="    APPLY    ",
                                relief='groove',
                                state='disabled',
                                command=self._apply)
        apply_button.grid(row=0, column=0, rowspan=2,
                          sticky=tk.W+tk.E+tk.N+tk.S,
                          padx=5, pady=2)
        self.buttons.append(apply_button)
        button_name = (">> Next >>", "<< Previous <<",      # 1, 2
                       "<< Apply ALL >>", "View Images",    # 3, 4
                       "Add to Report", "View Report",      # 5, 6
                       "Clear Report", "Save Report")       # 7, 8
        button_commands = (self._next, self._previous,
                           self._apply_all, self._view_images,
                           self._add_to_report, self._view_report,
                           self._clear_report, self._save_report)
        for but_name, but_cmd in zip(button_name, button_commands):
            self.buttons.append(tk.Button(self.button_frame,
                                text=but_name,
                                relief='groove',
                                state='disabled',
                                command=but_cmd))
        for i, but in enumerate(self.buttons[1:]):
            row = i % 2
            col = i // 2 + 1
            but.grid(row=row, column=col, **self.sticky_pad)
        prop_button = tk.Button(self.button_frame,
                                text='Additional Properties',
                                relief='groove',
                                command=self._add_prop)
        prop_button.grid(row=3, column=1, columnspan=3,
                                **self.sticky_pad)
    
    def grid_button_frame(self, *args, **kwargs):
        self.button_frame.grid(*args, **kwargs)

    def activate_apply_apply_all(self):
        self.buttons[0].configure(state='normal')
        self.buttons[3].configure(state='normal')

    def deactivate_apply_apply_all(self):
        self.buttons[0].configure(state='disabled')
        self.buttons[3].configure(state='disabled')

    def activate_next(self):
        self.buttons[1].configure(state='normal')

    def deactivate_next(self):
        self.buttons[1].configure(state='disabled')

    def activate_previous(self):
        self.buttons[2].configure(state='normal')

    def deactivate_previous(self):
        self.buttons[2].configure(state='disabled')

    def activate_view_images(self):
        self.buttons[4].configure(state='normal')

    def deactivate_view_images(self):
        self.buttons[4].configure(state='disabled')

    def activate_add_to_report(self):
        self.buttons[5].configure(state='normal')

    def deactivate_add_to_report(self):
        self.buttons[5].configure(state='disabled')

    def activate_report_buttons(self):
        ind = [6, 7, 8]
        for i in ind:
            self.buttons[i].configure(state='normal')

    def deactivate_report_buttons(self):
        ind = [6, 7, 8]
        for i in ind:
            self.buttons[i].configure(state='disabled')

    def _apply(self):
        pass

    def _next(self):
        pass

    def _previous(self):
        pass

    def _apply_all(self):
        pass
    
    def _view_images(self):
        pass

    def _add_to_report(self):
        pass

    def _view_report(self):
        pass

    def _clear_report(self):
        pass

    def _save_report(self):
        pass

    def _add_prop(self):
        pass


class AssayView(ButtonPanel, tk.Frame):
    """
    Arranges basic app layout and adds buttons. Defines
    common functionality of the buttons.

    All child classes should have the following attributes
    defined in the __init__() function:
    - self.title, str;
    - self.additional_panel, None or FramePanel;
    - self.img_titles, list of three str;
    - self.img_subtitles, list of three str;
    - self.img_scales, list of three bool;
    - self.img_filename_suffix, str;
    - self.image_correction_model, Model.
    If not defined these attribute will have default
    values.
    """
    
    def __init__(self, parent,
                 default_folder,
                 img_ext,
                 *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        ButtonPanel.__init__(self, self)
        self.default_folder = default_folder
        self.img_ext = img_ext
        attributes = ['title', 'additional_panel',
                      'img_titles', 'img_subtitles',
                      'img_scales',
                      'img_filename_suffix',
                      'image_correction_model']
        values = ['Title', # title
                  None, # additional_panel
                  ['', '', ''], # img_titles
                  ['', '', ''], # img_subtitels
                  [False, False, False], # img_scaels
                  '', # img_filename_suffix
                  ImageCorrectionDefaultModel] # image_correction_model
        for attr, val in zip(attributes, values):
            if not hasattr(self, attr):
                setattr(self, attr, val)
        self.file_manager = None
        self.input_panels = None
        self._draw_view()
        self.file_manager.bind('<MouseWheel>', self.wheel_change)
        
    def _draw_view(self,):
        sticky_pad = {'sticky':tk.W+tk.E, 'padx':5, 'pady':2}
        ttk.Label(self, text=self.title,
                  font=("TkDefaultFont", 16)
                  ).grid(row=0, columnspan=2)
        left_panel = tk.Label(self)
        self.file_manager = FileManager(left_panel,
                                        self.default_folder,
                                        self.img_ext)
        self.file_manager.configure_buttons = self.configure_buttons
        self.file_manager.select_first_image = self.show_image
        self.image_correction = ImageCorrection(left_panel,
                            frame_model=self.image_correction_model)
        self.input_panels = [self.file_manager,
                             self.image_correction]
        if self.additional_panel:
            self.add_panel = self.additional_panel(left_panel)
            self.input_panels.append(self.add_panel)
        for i, panel in enumerate(self.input_panels):
            panel.grid(row=i, column=0, **sticky_pad)
        left_panel.grid(row=1, column=0, rowspan=3)
        self.img_view = ImageView(self,
                                  img=None, res=(360, 240),
                                  padx=30, pady=10)
        self.img_view.grid(row=1, column=1,
                           columnspan=2, rowspan=2,
                           sticky=tk.W+tk.E+tk.N)
        self.image_row = ImageRow(self,
                        images = [None, None, None],
                        titles = self.img_titles,
                        subtitles = self.img_subtitles,
                        scales = self.img_scales,
                        res = (300, 200))
        self.image_row.grid(row=4, column=0,
                            columnspan=2,
                            **sticky_pad)
        self.grid_button_frame(row=3, column=1)
        self.configure_buttons()
        
    def configure_buttons(self):
        if self.get_image_path():
            self.activate_apply_apply_all()
        else:
            self.deactivate_apply_apply_all()

    def set_image(self, image):
        self.img_view.configure(image)
        
    def set_image_row(self, images, subtitles, img_mode=None):
        self.image_row.configure_images(images, img_mode)
        self.image_row.configure_subtitles(subtitles)
        
    def get_input(self):
        app_input = dict()
        for panel in self.input_panels:
            app_input = {**app_input, **panel.get_input()}
        return app_input
        
    def get_image_path(self):
        return self.file_manager.get_image_path()
        
    def get_path_wd(self):
        return self.file_manager.get_path_wd()

    def show_image(self):
        img_path = self.get_image_path()
        if img_path: # not None
            self._select_image(img_path)
        else: 
            self.img_view.set_default_image()

    def next_file(self):
        self.file_manager.next_file()

    def previous_file(self):
        self.file_manager.previous_file()
        
    def get_first_image(self):
        return self.file_manager.get_first_image()
        
    def set_widgets(self, widget_values):
        self.image_correction.set_widgets(widget_values)
        if not self.additional_panel:
            self.additional_panel.set_widgets(widget_values)
        
    def get_images(self):
        return self.file_manager.get_images()
        
    def get_file_name(self, *args, **kwargs):
        return self.file_manager.get_file_name(*args, **kwargs)

    def set_file_name(self, path):
        self.file_manager.set_file_name(path)
        
    def get_save_images_status(self):
        return self.file_manager.get_save_images_status()
                    
    def set_default_images(self):
        self.img_view.set_default_image()
        self.image_row.set_default_images()
        self.image_row.configure_subtitles(['', '', ''])

    def _get_geom_pop_window(self, width, height):
        rootx, rooty = self.winfo_rootx(), self.winfo_rooty()
        root_width, root_height = self.winfo_width(), self.winfo_height()
        pos_x = int(rootx + root_width/2 - width/2)
        pos_y = int(rooty + root_height/2 - height/2)
        return '%dx%d+%d+%d' % (width, height, pos_x, pos_y)

    def show_wait_window(self):
        self.wait_window = tk.Toplevel(self,
                            highlightcolor='red',
                            highlightbackground='red',
                            highlightthickness=1)
        self.wait_window.overrideredirect(True)
        lab = tk.Label(self.wait_window, text='Please, wait...',
                       fg='red')
        lab.pack(expand=1, anchor=tk.CENTER)
        geom = self._get_geom_pop_window(150, 75)
        self.wait_window.geometry(geom)
        self.wait_window.update_idletasks()
        self.wait_window.grab_set()

    def destroy_wait_window(self):
        self.wait_window.destroy()

    def progress_widget(self):
        self.progress_window = tk.Toplevel(self,
                                highlightcolor='red',
                                highlightbackground='red',
                                highlightthickness=1)
        self.progress_window.overrideredirect(True)
        geom = self._get_geom_pop_window(300, 100)
        self.progress_window.geometry(geom)
        lab = tk.Label(self.progress_window, text='Progress...',
                                fg='red')
        lab.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.fc = 0
        self.fc_perc = 0
        self.file_counter = tk.Label(self.progress_window,
                                text=str(self.fc)+' out of '+str(self.n_files),
                                fg='red')
        self.file_counter.grid(row=1, column=0, sticky=tk.N+tk.S)
        self.progressbar = ttk.Progressbar(self.progress_window, orient=tk.HORIZONTAL, 
                                           length=270, mode='determinate')
        self.progressbar.grid(row=2, column=0, sticky=tk.W+tk.E, padx=10, pady=5)
        self.progressbar['value'] = 0
        self.update()
        self.progress_window.focus_set()
        self.progress_window.grab_set()
        self.progress_window.update()
        
    def update_progressbar(self):
        self.fc += 1
        self.fc_perc = round(self.fc*100/self.n_files)
        self.file_counter.configure(text=str(self.fc)+' out of '+str(self.n_files))
        self.progressbar['value'] = self.fc_perc
        self.progress_window.update()

    def destroy_progressbar(self):
        self.progress_window.destroy()

    def wheel_change(self, event):
        change = -event.delta
        if change > 0:
            self.next_file()
        if change < 0:
            self.previous_file()
        self.show_image()
        self.update()
