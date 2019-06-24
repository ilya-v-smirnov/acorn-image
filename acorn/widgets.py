
import tkinter as tk
from tkinter import ttk
from decimal import Decimal, InvalidOperation
from PIL import Image, ImageTk
from numpy import asarray
import matplotlib.pyplot as plt
from .accessory_functions import fig2array, backend_switcher


class ValidatedMixin:
    """
    Adds a validation functionality to an input widget
    """
    
    def __init__(self, *args, error_var=None, **kwargs):
        self.error = error_var or tk.StringVar()
        super().__init__(*args, **kwargs)
        vcmd = self.register(self._validate)
        invcmd = self.register(self._invalid)
        self.config(validate='all',
                    validatecommand=(vcmd, '%P', '%s', '%S', '%V', '%i', '%d'),
                    invalidcommand=(invcmd, '%P', '%s', '%S', '%V', '%i', '%d'))
                    
    def _toggle_error(self, on=False):
        self.config(foreground=('red' if on else 'black'))
        
    def _validate(self, proposed, current, char, event, index, action):
        self._toggle_error(False)
        self.error.set('')
        valid = True
        if event == 'focusout':
            valid = self._focusout_validate(event=event)
        elif event == 'key':
            valid = self._key_validate(proposed=proposed, current=current, char=char,
                                       event=event, index=index, action=action)
        return valid
        
    def _focusout_validate(self, **kwargs):
        return True
        
    def _key_validate(self, **kwargs):
        return True
        
    def _invalid(self, proposed, current, char, event, index, action):
        if event == 'focusout':
            self._focusout_invalid(event=event)
        elif event == 'key':
            self._key_invalid(self, proposed=proposed, current=current,
                              char=char, event=event, index=index, action=action)
                                    
    def _focusout_invalid(self, **kwargs):
        self._toggle_error(True)
        
    def _key_invalid(self, *args, **kwargs):
        pass
        
    def trigger_focusout_validation(self):
        valid = self._validate('', '', '', 'focusout', '', '')
        if not valid:
            self._focusout_invalid(event='focusout')
        return valid

        
class ValidatedSpinbox(ValidatedMixin, ttk.Spinbox):
    """
    Validates Spinbox input.
    """
    
    def __init__(self, *args, min_var=None, max_var=None, focus_update_var=None,
                 from_='-Infinity', to='Infinity', **kwargs):
        super().__init__(*args, from_=from_, to=to, **kwargs)
        self.resolution = Decimal(str(kwargs.get('increment', '1.0')))
        self.precision = (self.resolution
                          .normalize()
                          .as_tuple()
                          .exponent)

    def _key_validate(self, action, index, char, proposed, current, **kwargs):
        valid = True
        min_val = self.cget('from')
        max_val = self.cget('to')
        no_negative = min_val >= 0
        no_decimal = self.precision >= 0
        if action == "0":
            return True
        if any([
                (char not in '-1234567890.'),
                (char == '-' and (no_negative or index != '0')),
                (char == '.' and (no_decimal or '.' in current)),
                (char == '0' and (current == '0' or current == '-0'))
               ]):
            return False
        if proposed in '-.':
            return True
        proposed = Decimal(proposed)
        proposed_precision = proposed.as_tuple().exponent
        
        if any([
                (proposed > max_val),
                (proposed < min_val),
                (proposed_precision < self.precision)
               ]):
            return False
        return valid
                
    def _focusout_validate(self, event):
        valid = True
        value = self.get()
        if value == '':
            self.error.set('A value is required')
            valid = False
        else:
            try:
                Decimal(value)
            except ValueError:
                self.error.set('Invalid value: {}'.format(value))
                valid = False
        return valid


class ValidatedCombobox(ValidatedMixin, ttk.Combobox):
    """
    Validates Combobox input.
    """
    
    def __init__(self, *args, values, **kwargs):
        super().__init__(*args, values=values, **kwargs)
        
    def _key_validate(self, action, **kwargs):
        valid = True
        if action == '0' or action == '1':
            valid = False
        elif not proposed in values:
            valid = False
        return valid
    
    def _focusout_validate(self, event):
        valid = True
        value = self.get()
        if value == '':
            self.error.set('A value is required')
            valid = False
        return valid

        
class LabeledWidget(tk.Frame):
    """
    Creates labeled combobox and spinbox widgets.
    """
    
    def __init__(self, parent, type,
                 default, text_label='',
                 side='top',
                 inner_padx=5, inner_pady=2,
                 **kwargs):
        super().__init__(parent)
        self.type = type
        self.side = side
        self.padx, self.pady = inner_padx, inner_pady
        if self.type == 'checkbutton':
            self.var = tk.BooleanVar()
            self.check_lab = tk.StringVar()
            self.check_lab.set(text_label)
            self.widget = ttk.Checkbutton(self,
                            variable=self.var,
                            textvariable=self.check_lab,
                            **kwargs)
            self.widget.pack()
        else:
            label = ttk.Label(self, text=text_label)
            label.grid(row=self._label_row(),
                       column=self._label_col(),
                       **self._get_sticky_pad())
            if self.type == 'combobox':
                self.var = tk.StringVar()
                self.widget = ValidatedCombobox(self,
                        textvariable=self.var, **kwargs)
            elif self.type == 'spinbox':
                self.var = tk.DoubleVar()
                self.widget = ValidatedSpinbox(self,
                        textvariable=self.var, **kwargs)
            else:
                raise ValueError('Wrong type parameter')
            self.widget.grid(row=self._widget_row(),
                         column=self._widget_col(),
                         **self._get_sticky_pad())
        self.var.set(value=default)
    
    def _label_row(self):
        return int(self.side == 'bottom')
    
    def _label_col(self):
        return int(self.side == 'right')
            
    def _widget_row(self):
        return int(self.side == 'top')
            
    def _widget_col(self):
        return int(self.side == 'left')
        
    def _get_sticky_pad(self):
        sticky_pad = {}
        sticky_pad['sticky'] = tk.W + tk.E + tk.S + tk.N
        if self.side == 'bottom' or self.side == 'top':
            sticky_pad['pady'] = self.pady
        else:
            sticky_pad['padx'] = self.padx
        return sticky_pad
            
    def configure(self, *args, **kwargs):
        self.widget.configure(*args, **kwargs)
    
    def set(self, value):
        self.var.set(value)
    
    def get(self, *args, **kwargs):
        value = self.var.get(*args, **kwargs)
        if self.type == 'spinbox':
            return float(value)
        return value


class ImageButton(ttk.Button):
    def __init__(self, parent, PILimg=None, res=(300, 200),
                 *args, **kwargs):
        self.res = res
        self.img = PILimg or self._default_image()
        self.icon = self._make_icon()
        super().__init__(parent, image=self.icon,
                         command=self.open_in_window,
                         *args, **kwargs)
        
    def _default_image(self):
        ratio = self.res[1]/self.res[0]
        fig = plt.figure(figsize=plt.figaspect(ratio))
        plt.text(0, 0, 'No Image', fontsize=56,
                 horizontalalignment='center',
                 verticalalignment='center')
        plt.xlim(-1, 1)
        plt.ylim(-1, 1)
        plt.axis('off')
        arr = fig2array(fig)
        plt.close(fig)
        return Image.fromarray(arr)
        
    def _make_icon(self):
        img = self.img.resize(self.res, Image.ANTIALIAS)
        tk_img = ImageTk.PhotoImage(img)
        return tk_img

    @backend_switcher
    def open_in_window(self):
        image = asarray(self.img)
        fig = plt.figure()
        if len(image.shape) == 2:
            plt.imshow(image, cmap='gray')
        else:
            plt.imshow(image)
        plt.axis('off')
        plt.show()
    
    def configure_image_button(self, img):
        self.img = img
        self.icon = self._make_icon()
        self.configure(image = self.icon)
        
    def set_default_image(self):
        self.configure_image_button(self._default_image())
        