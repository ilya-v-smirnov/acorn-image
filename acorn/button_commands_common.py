
from .accessory_functions import backend_switcher, dict_identical
from .views import TableView
from .accessory_functions import save_csv
from tkinter import filedialog

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
            return True
        else:
            return False

    def _apply(self):
        pass

    def _view_file(self):
        if self._select_image(self.get_image_path()):
            self.set_image(self.image.get_PILimg())
          
    def _next(self):
        self.next_file()
        self._apply()
        
    def _image_saver(self):
        save = self.get_save_images_status()
        if save:
            basename = self.get_file_name(with_ext=False)
            self.save_image(self.image.get_save_img(),
                            name=basename,
                            suffix=self.img_filename_suffix)
        
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
        self.set_file_name(self.get_first_image())
        self.n_files = len(self.get_images())
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
        self.deactivate_add_to_report()
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