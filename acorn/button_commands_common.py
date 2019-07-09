
from .accessory_functions import backend_switcher, dict_identical
from .views import TableView
from .accessory_functions import save_csv

class CommonButtonCommands:
    """
    Adds basic functionality to the buttons of ButtonPanel.
    """
    
    def __init__(self):
        self.image = None
        self.result = []
        self.draw_gui = True
            
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

    
    def _apply_all(self):
        if self._select_image(self.get_first_image()):
            
            image_files = self.get_images()
            n_files = len(image_files)
            if n_files > 1:
                self.draw_gui = False
                for i in range(n_files-1):
                    self._apply()
                    self._add_to_report()
                    self.next_file()
                self.draw_gui = True
            self._apply()
            self._add_to_report()
    
    def _clear_report(self):
        self.result.clear()
        self.set_default_images()
    
    @backend_switcher
    def _view_images(self):
        if not self.image is None:
            self.image.view_images()
    
    def _view_report(self):
        if len(self.result) > 0:
            TableView(self, self.result)

    def _save_report(self, report,
                     fieldnames=None,
                     title=None, fileName='report',
                     dirName=None, fileExt='.csv',
                     fileTypes=None):
        if len(self.result) > 0:
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