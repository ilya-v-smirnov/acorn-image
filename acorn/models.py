
# This is an app model.
# Sets default values, ranges, increment steps, lists of values, ets.
# for widgets of each panel.

import os

class Model:
    
    def __init__(self):
        self.model = {}
        
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
        self.model['recursive'] = {'type': 'checkbutton',
                                   'text_label': 'Recursive',
                                   'default': False}
        self.model['save_images'] = {'type': 'checkbutton',
                                     'text_label': 'Save wound images',
                                     'default': False}

   
class ImageCorrectionModel(Model):
    
    def __init__(self):
        super().__init__()
        self.model['channel'] = {'type': 'combobox',
                                 'text_label': 'Channel',
                                 'default': 'BW',
                                 'values': ['BW', 'Red', 'Green', 'Blue']}
        self.model['bright'] = {'type': 'spinbox',
                                'text_label': 'Brightness',
                                'default': 1.0,
                                'from_': 0.1,
                                'to': 20,
                                'increment': 0.1}
        self.model['contr'] = {'type': 'spinbox',
                               'text_label': 'Contrast',
                               'default': 1.2,
                               'from_':-20,
                               'to': 20,
                               'increment':0.1}
        self.model['blur_radius'] = {'type': 'spinbox',
                                     'text_label': 'Blur Radius',
                                     'default': 1,
                                     'from_': 0,
                                     'to': 25,
                                     'increment': 1}
        self.model['inverse'] = {'type': 'checkbutton',
                                 'text_label': 'Inverse Image',
                                 'default': False}
                                          
class WoundParametersModel(Model):

    def __init__(self):
        super().__init__()
        self.model['mode'] = {'type': 'combobox',
                              'text_label': 'Mode',
                              'default': 'Borders',
                              'values': ['Borders', 'Contrast', 'Minimum']}
        self.model['filter'] = {'type': 'combobox',
                                'text_label': 'Mode',
                                'default': 'Mean',
                                'values': ['Mean', 'Otsu']}
        self.model['offset'] = {'type': 'spinbox',
                                'text_label': 'Offset, %',
                                'default': 0,
                                'from_': -50,
                                'to': 50,
                                'increment': 0.5}
        self.model['equal_exposure'] = {'type': 'checkbutton',
                                        'text_label': 'Equal. exposure',
                                        'default': True}
        self.model['disk_radius'] = {'type': 'spinbox',
                                     'text_label': 'Disk Radius',
                                     'default': 6,
                                     'from_': 0,
                                     'to': 25,
                                     'increment': 1}
        self.model['min_wound'] = {'type': 'spinbox',
                                   'text_label': 'Min wound, %',
                                   'default': 7,
                                   'from_': 1,
                                   'to': 80,
                                   'increment': 1}
        self.model['min_objects'] = {'type': 'spinbox',
                                     'text_label': 'Min wound, %',
                                     'default': 7,
                                     'from_': 1,
                                     'to': 80,
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
                                        