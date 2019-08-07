
from .accessory_functions import backend_switcher, dict_identical
from .views import TableView
from .accessory_functions import save_csv
from tkinter import filedialog
import tkinter.messagebox as tkmessagebox
from .views_additional_properties import AdditionalPropertis

class CommonButtonCommands:
    """
    Adds basic functionality to the buttons of ButtonPanel.
    """

    def __init__(self):
        self.image = None
        self.result = []
        self.draw_progress = False

    def _select_image(self, img_path, FUN):
        if img_path:
            self.image = FUN(img_path)
            file_name = self.get_input().get('file')
            index = self.file_manager.images.index(file_name)
            self.file_manager.image_index = index
            self.set_image(self.image.get_PILimg())
            return True
        else:
            return False

    def _apply(self):
        try:
            self._sub_apply()
        except Exception as e:
            if hasattr(self, 'wait_window'):
                self.destroy_wait_window()
            if hasattr(self, 'progress_window'):
                self.destroy_progressbar()
            tkmessagebox.showerror('Error!', str(e), parent=self)
            self.grab_set()
        finally:
            n_files = len(self.file_manager.images)
            im_index = self.file_manager.image_index
            if n_files > 1:
                if im_index > 0:
                    self.activate_previous()
                else:
                    self.deactivate_previous()
                if im_index + 1 == n_files:
                    self.deactivate_next()
                else:
                    self.activate_next()
            self.activate_view_images()
            self.activate_add_to_report()

    def _next(self):
        self.next_file()
        self._apply()

    def _previous(self):
        self.previous_file()
        self._apply()
        
    def _image_saver(self):
        save = self.get_save_images_status()
        if save:
            basename = self.get_file_name(with_ext=False)
            self.image.save_final_image(folder=self.get_path_wd(),
                                prefix='',
                                basename=basename,
                                suffix=self.img_filename_suffix,
                                ext='jpg')

        
    def _add_to_report(self):
        if self.image:
            filename = {'file': self.image.get_image_path()}
            arguments = self.image.called_with()
            report_stat = self.image.get_report_stat()
            row = {**filename,
                   **arguments,
                   **report_stat}
            if len(self.result) == 0:
                self.result.append(row)
                self._image_saver()
            if not dict_identical(row, self.result[-1]):
                self.result.append(row)
                self._image_saver()
            self.activate_report_buttons()
            self.deactivate_add_to_report()
    
    def _apply_all(self):
        self.file_manager.set_first_image()
        self.n_files = len(self.file_manager.images)
        if self.n_files > 1:
            self.draw_progress = True
            self.progress_widget()
            for _ in range(self.n_files):
                self._apply()
                self._add_to_report()
                self.update_progressbar()
                self.next_file()
            self.destroy_progressbar()
            self.draw_porgress = False
   
    def _clear_report(self):
        self.result.clear()
        self.set_default_images()
        self.deactivate_report_buttons()
        self.deactivate_view_images()
    
    @backend_switcher
    def _view_images(self):
        if not self.image is None:
            self.image.view_images()
    
    def _view_report(self):
        if len(self.result) > 0:
            TableView(self, self.result)

    def _save_report(self,
                     fieldnames=None,
                     title=None, fileName='report',
                     dirName=None, fileExt='.csv'):
        if len(self.result) > 0:
            fileTypes = [('csv files', '.csv'), ('all files', '.*')]
            options = {'parent': self,
                       'defaultextension': fileExt,
                       'filetypes': fileTypes,
                       'initialdir': dirName,
                       'initialfile': fileName,
                       'title': title}
            csv_name = filedialog.asksaveasfilename(**options)
            if fieldnames is None:
                fieldnames = self.result[0].keys()
            if csv_name != '':
                save_csv(self.result, fieldnames, csv_name)

    def _add_prop(self):
        inp = self.get_input()
        props = ['border_size', 'border_color']
        props_dict = dict()
        for pr in props:
            props_dict[pr] = inp.get(pr)
        print(props_dict)
        self.add_prop = AdditionalPropertis(self, **props_dict)