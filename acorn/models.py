
# This is an app model.
# Sets default values, ranges, increment steps, lists of values, etc.
# for widgets of each panel.

import os


class Model:
    
    def __init__(self):
        self.model = dict()
        
    def __call__(self):
        return self.model

    def add_value(self, widget, key, value):
        if isinstance(value, dict):
            self.model[widget] = {**self.model[widget],
                                  **value}
        else:
            self.model[widget][key] = value
        
    def add_values(self, widget, keys, values):
        for key, value in zip(keys, values):
            self.add_value(widget, key, value)
        
    def add_value_to_widgets(self, widgets, key, value):
        for widget in widgets:
            self.add_value(widget, key, value)
            

class FileManagerModel(Model):
    
    def __init__(self):
        super().__init__()
        self.model['recursive'] = {
                    'type': 'checkbutton',
                    'text_label': 'Recursive',
                    'default': False}
        self.model['save_images'] = {
                    'type': 'checkbutton',
                    'text_label': 'Save images',
                    'default': False}

   
class ImageCorrectionDefaultModel(Model):
    
    def __init__(self):
        super().__init__()
        self.model['channel'] = {
                    'type': 'combobox',
                    'text_label': 'Channel',
                    'default': 'BW',
                    'values': ['BW', 'Red', 'Green', 'Blue']}
        self.model['bright'] = {
                    'type': 'spinbox',
                    'text_label': 'Brightness',
                    'default': 1.0,
                    'from_': 0.1,
                    'to': 20,
                    'increment': 0.1}
        self.model['contr'] = {
                    'type': 'spinbox',
                    'text_label': 'Contrast',
                    'default': 1.0,
                    'from_':-20,
                    'to': 20,
                    'increment':0.1}
        self.model['blur_radius'] = {
                    'type': 'spinbox',
                    'text_label': 'Blur Radius',
                    'default': 0,
                    'from_': 0,
                    'to': 25,
                    'increment': 1}
        self.model['inverse'] = {
                    'type': 'checkbutton',
                    'text_label': 'Inverse Image',
                    'default': False}


class ImageCorrectionWoundAssayModel(ImageCorrectionDefaultModel):

    def __init__(self):
        super().__init__()
        self.model['contr']['default'] = 1.2
        self.model['blur_radius']['default'] = 1


class ImageCorrectionCellCounterModel(ImageCorrectionDefaultModel):

    def __init__(self):
        super().__init__()
        self.model['channel']['default'] = 'Green'

class ImageCorrectionCellConfluent(ImageCorrectionDefaultModel):

    def __init__(self):
        super().__init__()
        self.model['contr']['default'] = 1.2
        self.model['blur_radius']['default'] = 1
      
                                          
class WoundParametersModel(Model):

    def __init__(self):
        super().__init__()
        self.model['mode'] = {
                    'type': 'combobox',
                    'text_label': 'Mode',
                    'default': 'Borders',
                    'values': ['Borders', 'Contrast']}
        self.model['filt'] = {
                    'type': 'combobox',
                    'text_label': 'Binary filter',
                    'default': 'Mean',
                    'values': ['Mean', 'Otsu', 'Minimum']}
        self.model['offset'] = {
                    'type': 'spinbox',
                    'text_label': 'Offset, %',
                    'default': 0,
                    'from_': -50,
                    'to': 50,
                    'increment': 0.5}
        self.model['equal_exposure'] = {
                    'type': 'checkbutton',
                    'text_label': 'Equal. exposure',
                    'default': True}
        self.model['disk_radius'] = {
                    'type': 'spinbox',
                    'text_label': 'Disk Radius',
                    'default': 6,
                    'from_': 0,
                    'to': 25,
                    'increment': 1}
        self.model['min_wound'] = {
                    'type': 'spinbox',
                    'text_label': 'Min wound, %',
                    'default': 1.5,
                    'from_': 0,
                    'to': 80,
                    'increment': 0.5}
        self.model['min_objects'] = {
                    'type': 'spinbox',
                    'text_label': 'Min objects, %',
                    'default': 7,
                    'from_': 0,
                    'to': 80,
                    'increment': 0.5}


class CellCounterModel(Model):

    def __init__(self):
        super().__init__()
        self.model['binary_filter'] = {
                    'type': 'combobox',
                    'text_label': 'Binary filter',
                    'default': 'Minimum',
                    'values': ['Mean', 'Otsu', 'Minimum']}
        self.model['mask_filter'] = {
                    'type': 'combobox',
                    'text_label': 'Mask filter',
                    'default': 'Otsu',
                    'values': ['Mean', 'Otsu', 'Minimum']}
        self.model['offset_binary'] = {
                    'type': 'spinbox',
                    'text_label': 'Binary offset, %',
                    'default': 0,
                    'from_': -50,
                    'to': 50,
                    'increment': 1}
        self.model['offset_mask'] = {
                    'type': 'spinbox',
                    'text_label': 'Mask offset, %',
                    'default': 0,
                    'from_': -50,
                    'to': 50,
                    'increment': 1}
        self.model['min_dist'] = {
                    'type': 'spinbox',
                    'text_label': 'Min distance',
                    'default': 3,
                    'from_': 1,
                    'to': 50,
                    'increment': 1}
        self.model['disk_radius'] = {
                    'type': 'spinbox',
                    'text_label': 'Disk radius',
                    'default': 3,
                    'from_': 1,
                    'to': 25,
                    'increment': 1}
        self.model['size_thresh'] = {
                    'type': 'spinbox',
                    'text_label': 'Size threshold',
                    'default': 25,
                    'from_': 0,
                    'to': 1000,
                    'increment': 1}


class CellConfluentModel(WoundParametersModel):

    def __init__(self):
        super().__init__()
        self.model['filt']['default'] = 'Mean'
        self.model['disk_radius']['default'] = 3 
        self.model['min_wound'] = {
                    'type': 'spinbox',
                    'text_label': 'Free space, %',
                    'default': 0.1,
                    'from_': 0,
                    'to': 80,
                    'increment': 0.01}
        self.model['min_objects'] = {
                    'type': 'spinbox',
                    'text_label': 'Min objects, %',
                    'default': 0.05,
                    'from_': 0,
                    'to': 80,
                    'increment': 0.01}


class BorderPropertiesModel(Model):

    def __init__(self):
        super().__init__()
        self.model['border_size'] = {
                    'type': 'spinbox',
                    'text_label': 'Border size, pxl',
                    'default': 1,
                    'from_': 1,
                    'to': 100,
                    'increment': 1}      


class AppModel(Model):
    
    def __init__(self):
        super().__init__()
        path_to_samples = os.path.join(os.getcwd(), 'Sample Images')
        if os.path.exists(path_to_samples):
            self.model['default_folder'] = path_to_samples
        else:
            self.model['default_folder'] = os.getcwd()
        self.model['img_ext'] = ['.jpg', '.jpeg']
