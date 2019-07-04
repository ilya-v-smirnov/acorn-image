
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image
from . import widgets as w
from .models import FileManagerModel, ImageCorrectionModel
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
        dict = {}
        for k in keys:
            dict[k] = self.widgets[k].get()
        return dict
        
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
        self._set()
        self.text = self._make_limited()
        super().__init__(parent, text=self.text)
        
    def _set(self):
        if self.path is None:
            self._path = os.getcwd()
        elif os.path.exists(self.path):
            self._path = self.path
        else:
            raise ValueError('Wrong path')
    
    def _make_limited(self):
        return limit_text(self._path, self.limit, self.begin)
    
    def configure(self, path):
        self.path = path
        self._set()
        self.text = self._make_limited()
        super().configure(text=self.text)
    
    
class FileManager(ImageFileMixin, FramePanel):
    """
    File Manager is able to choose image containing directory and
    working directory to save images and report.
    """
    
    def __init__(self, parent,
                 path=None, img_ext=None):
        self.path = path
        FramePanel.__init__(self, parent,
                            text='File Manager',
                            frame_model=FileManagerModel)
        ImageFileMixin.__init__(self, path=path,
                                img_ext=img_ext)
        self.path_wd = self.path if os.path.exists(self.path) else None                        
        self.frame_model.add_value(widget='recursive',
                             key='command',
                             value=self._recursive)
        self.initiate_widgets()
        sticky_pad = {'sticky': tk.W+tk.E, 'padx': 5, 'pady': 1}
        ttk.Label(self,
                  text='Path to images:'
                  ).grid(row=0, column=0,
                  **sticky_pad)        
        self.path_to_images = FilePathLabel(self,
                                path=self.path,
                                limit=50, begin=20)
        self.path_to_images.grid(row=1, column=0, columnspan=2,
                                **sticky_pad)
        self.widgets['file'] = w.LabeledWidget(self,
                                type='combobox', text_label='File:',
                                default=self.first_img,
                                values=self.images,
                                width=50)
        self.widgets['file'].grid(row=2, column=0,
                                columnspan=2,
                                **sticky_pad)
        self.path_to_wd = FilePathLabel(self,
                                path=self.path_wd,
                                limit=50, begin=20)
        self.path_to_wd.grid(row=4, column=0,
                             columnspan=2,
                             **sticky_pad)
        but_browse1 = ttk.Button(self, text="Browse",
                                 command=self._browse_button1)        
        ttk.Label(self,
                 text='Path to working directory:'
                 ).grid(row=3, column=0,
                 **sticky_pad)
        self.recursive = False
        self.widgets['recursive'].grid(row=3, column=1,
                                **sticky_pad)
        self.widgets['save_images'].grid(row=5, column=0,
                                sticky=tk.W, padx=5)          
        but_browse1.grid(row=1, column=2, **sticky_pad)
        but_browse2 = ttk.Button(self, text="Browse",
                                 command=self._browse_button2)
        but_browse2.grid(row=4, column=2, **sticky_pad)
        
    def _browse_button1(self):
        chosen_path = filedialog.askdirectory()
        if chosen_path != '':
            self.path = chosen_path
            self.path_to_images.configure(path=self.path)
            self.images.clear()
            self._find_images()
            self.widgets['file'].set(self.first_img)
            self.widgets['file'].configure(values=self.images)
        
    def _browse_button2(self):
        chosen_path = filedialog.askdirectory()
        if chosen_path != '':
            self.path_wd = chosen_path
            self.path_to_wd.configure(path=self.path_wd)
        
    def _recursive(self):
        self.recursive = self.widgets['recursive'].get()
        self.images.clear()
        self._find_images()
        self.widgets['file'].set(self.first_img)
        self.widgets['file'].configure(values=self.images)
        
    def get_image_path(self):
        fileName = self.widgets['file'].get()
        if fileName == 'None':
            return None
        return os.path.join(self.path, fileName)
        
    def next_file(self):
        file_name = self.widgets['file'].get()
        index = self.images.index(file_name)
        if index + 1 < len(self.images):
            self.widgets['file'].set(self.images[index+1])
            
    def get_file_name(self, with_ext=True):
        file_name = self.widgets['file'].get()
        if with_ext:
            return file_name
        return os.path.splitext(file_name)[0]
        
    def get_save_images_status(self):
        return self.widgets['save_images'].get()
                   
       
class ImageCorrection(FramePanel):
    """
    Creates a panel for image correction.
    """
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, text="Image Correction",
                         frame_model=ImageCorrectionModel,
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
                 titles, subtitles, res, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.buttons = []
        self.subtitles = subtitles
        self.sub_labels = []
        sticky_pad = {'sticky': tk.E, 'padx': 5, 'pady': 5}
        for i, (img, title, subtitl) in enumerate(zip(images, titles, self.subtitles)):
            ttk.Label(self, text=title,
                     font=("TkDefaultFont", 12)).grid(row=0, column=i)
            self.buttons.append(w.ImageButton(self, img, res))
            self.buttons[i].grid(row=1, column=i, **sticky_pad)
            self.sub_labels.append(ttk.Label(self,
                                   text=subtitl, font=("TkDefaultFont", 12)))
            self.sub_labels[i].grid(row=2, column=i)

    def configure_subtitles(self, subtitles):
        for sub, lab in zip(subtitles, self.sub_labels):
            lab.configure(text=sub)
            
    def configure_images(self, images):
        for img, but in zip(images, self.buttons):
            PILimg = Image.fromarray(img, 'RGB')
            but.configure_image_button(PILimg)
            
    def set_default_images(self):
        for button in self.buttons:
            button.set_default_image()
            

class TableView(tk.Toplevel):
    """
    Creates a table widget to show results.
    """
    
    def __init__(self, parent, table, columns=None,
                 id_field=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title = 'Report'
        self.table = table
        self.columns = columns or list(self.table[0].keys())
        self.id_field = id_field
        self.tree = ttk.Treeview(self, columns=self.columns)
        self.tree.pack(side=tk.LEFT)
        self.tree['show'] = 'headings'
        self._make_columns()
        self._make_rows()
        self._fill_table()
        scroll = tk.Scrollbar(self, orient=tk.VERTICAL,
                              command=self.tree.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scroll.set)
    
    def _make_columns(self):
        for col in self.columns:
            self.tree.column(col, width=75, minwidth=75, stretch=True)
            self.tree.heading(col, text=col, anchor=tk.CENTER)
    
    def _make_rows(self):
        index = 0
        for row in self.table:
            iid = row.get(self.id_field)
            self.tree.insert(parent='', index=index, iid=iid)
            index += 1
            
    def _fill_table(self):
        for row in self.table:
            for col in self.columns:
                self.tree.set(item=row.get(self.id_field),
                              column=col, value=row.get(col))
      

class ButtonPanel:
    """
    Creats a panel containing buttons.
    """
    
    def __init__(self, parent, *args, **kwargs):    
        sticky_pad = {"sticky": tk.W+tk.E, "padx": 5, "pady": 2}
        self.button_frame = tk.Frame(parent, *args, **kwargs)
        self.view_file_but = ttk.Button(self.button_frame,
                                text="\n  View file  \n",
                                command=self._view_file)
        self.view_file_but.grid(row=0, column=0, rowspan=2,
                                **sticky_pad)        
        button_name = ("Apply", ">> Next >>",
                       "<< Apply ALL >>", "View Images",
                       "Add to Report", "View Report",
                       "Clear Report", "Save Report")
        button_functions = (self._apply, self._next,
                            self._apply_all, self._view_images,
                            self._add_to_report, self._view_report,
                            self._clear_report, self._save_report)
        self.buttons = []
        for button, fun in zip(button_name, button_functions):
            self.buttons.append(ttk.Button(self.button_frame,
                                           text=button,
                                           command=fun))
        for i, button in enumerate(self.buttons):
            row = i % 2
            col = i // 2 + 1
            button.grid(row=row, column=col,
                        **sticky_pad)
    
    def grid_button_frame(self, *args, **kwargs):
        self.button_frame.grid(*args, **kwargs)
    
    def _view_file(self):
        pass
    
    def _apply(self):
        pass
        
    def _next(self):
        pass
        
    def _apply_all(self):
        pass
        
    def _view_images(self):
        pass
        
    def _add_to_report(self):
        pass
        
    def _view_report(self, table):
        TableView(self, table, id_field='file')
        
    def _clear_report(self):
        pass
        
    def _clear_report(self):
        pass
        
    def _save_report(self, report,
                     fieldnames=None,
                     title=None, fileName='report',
                     dirName=None, fileExt='.csv',
                     fileTypes=None):
        if fileTypes is None:
            fileTypes = [('csv files', '.csv'), ('all files', '.*')]
        options = {'defaultextension': fileExt,
                   'filetypes': fileTypes,
                   'initialdir': dirName,
                   'initialfile': fileName,
                   'title': title}
        csv_name = filedialog.asksaveasfilename(**options)
        if fieldnames is None:
            fieldnames = report[0].keys()
        if csv_name != '':
            save_csv(report, fieldnames, csv_name)