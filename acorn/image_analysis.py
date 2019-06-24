
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance
from PIL.ImageOps import invert
from PIL.ImageFilter import GaussianBlur
from skimage.filters import threshold_otsu, threshold_mean, threshold_minimum 
from skimage.morphology import watershed, binary_opening, binary_closing
from skimage.morphology import disk, remove_small_objects
from scipy import ndimage as ndi
from skimage.filters import sobel
from skimage.feature import corner_peaks
from skimage.exposure import equalize_adapthist
from matplotlib.colors import LinearSegmentedColormap
from .accessory_functions import *

class CorrectedImage:
    """
    Loads image and performs its basic correction using
    PIL tools.
    """
    
    def __init__(self, img_path):
        self.img_path = img_path
        try:
            self.PILimg = Image.open(self.img_path)
            self.img_original = np.asarray(self.PILimg)
        except:
            raise TypeError("Can't open file {}\n".format(img_path))
        self.height = self.img_original.shape[0]
        self.width = self.img_original.shape[1]
            
    def __call__(self, channel='BW', bright=1.0, contr=1.0,
                 blur_radius=0, equal_exposure=False,
                 inverse=False, **kwargs):        
        self.channel = channel
        self.bright = bright
        self.contr = contr
        self.blur_radius = blur_radius
        self.equal_exposure = equal_exposure
        self.inverse = inverse
        self.img_corrected = np.asarray(
            self._correct_img(self._get_channel()))
        if self.equal_exposure:
            img_eqaul = equalize_adapthist(self.img_corrected)*255
            self.img_corrected = img_eqaul.astype('uint8')
    
    def get_PILimg(self):
        return self.PILimg
    
    def _get_channel(self):
        """
        Extracts specified channels from PIL Image.
        If image is BW sets channel as 'BW' despite it
        initial value.
        If image is RGB but channel set as 'BW',
        it swiches channel to 'Red'.
        """
        shape = self.PILimg.getbands()
        if len(shape) == 1:
            if self.channel != 'BW':
                self.channel = 'BW'
            return self.PILimg
        else:
            if self.channel == 'BW':
                self.channel = 'Red'
            splited_img = self.PILimg.split()[0:3]
            ch = {key: value for key, value in zip(("Red", "Green", "Blue"), splited_img)}
            return ch[self.channel]
    
    def _correct_img(self, img):
        """
        Corrects brightness and contrast of the image and
        performs its Gaussian blur.
        """
        if self.inverse:
            img = invert(img)
        if self.bright == 1.0 and self.contr == 1.0 and self.blur_radius == 0:
            return img
        br = ImageEnhance.Brightness(img)
        img = br.enhance(self.bright)
        ctr = ImageEnhance.Contrast(img)
        img = ctr.enhance(self.contr)
        img = img.filter(GaussianBlur(self.blur_radius))
        return img
        
    def show_correction(self):
        fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(8, 4),
                                       sharex=True, sharey=True)
        if len(self.img_original.shape) == 3:
            ax1.imshow(self.img_original)
        else:
            ax1.imshow(self.img_original, cmap=plt.cm.gray)
        ax1.set_title('Original image')
        ax1.axis('off')
        ax2.imshow(self.img_corrected, cmap=plt.cm.gray)
        ax2.set_title('Corrected image')
        ax2.axis('off')
        plt.show()
        
    def called_with(self):
        """
        Return arguments of the __call__ function.
        """
        dict = {'channel': self.channel,
                'bright': self.bright,
                'contr': self.contr,
                'blur_radius': self.blur_radius,
                'equal_exposure': self.equal_exposure,
                'inverse': self.inverse}
        return dict
    
    def get_image_path(self):
        return self.img_path
        

class BinaryImage(CorrectedImage):
    """
    Creats a binary image.
    Takes threshold function through filter argument.
    Two modes are available:
    'Borders' - should be used for non-stained images.
    'Contrast' - should be used for stained images.
    """
    
    def __init__(self, img_path):
        super().__init__(img_path)
        
    def __call__(self, filter,
                 mode='Borders',
                 offset=0, y_slice=None,
                 **kwargs):
        super().__call__(**kwargs)
        self.filter = filter
        self.mode = mode
        self.offset = offset
        if y_slice is None:
            self.y_slice = int(self.height / 2)
        if self.mode == 'Borders':
            self.pre_binary = sobel(self.img_corrected)
        elif self.mode == 'Contrast':
            self.pre_binary = self.img_corrected
        else:
            raise ValueError("There is no mode '{}'!".format(self.mode))
        self.thresh = get_threshold(self.pre_binary,
                                    self._get_filter(),
                                    offset)
        if self.mode == 'Borders':
            self.img_binary = self.pre_binary > self.thresh
        elif self.mode == 'Contrast':
            self.img_binary = self.pre_binary < self.thresh
        return self.img_binary
    
    def _get_filter(self):
        dict = {'Mean': threshold_mean,
                'Otsu': threshold_otsu,
                'Minimum': threshold_minimum}
        return dict.get(self.filter)
    
    def show_binary(self):
        fig = plt.figure()
        plt.imshow(self.img_binary, cmap='gray')
        plt.axis('off')
        plt.show()
    
    def get_sliced_img(self, show_slice=False,
                       line_width=5):
        if self.y_slice is None or not show_slice:
            return self.img_corrected
        half_width = floor(line_width/2)
        start = self.y_slice - half_width
        if start < 0:
            start = 0
        end = self.y_slice + half_width + 1
        if end > self.height:
            end = half_width
        if is_even(line_width):
            line_width += 1
        img_colored = np.dstack((self.img_corrected,) * 3)
        line = np.array((255, 0, 0) * (end-start) * self.width)
        line.shape = (end-start, self.width, 3)
        img_colored[start:end,:,] = line
        return img_colored

    def _slice_img(self):
        return self.pre_binary[self.y_slice,]
        
    def get_image_slice(self):
        slice = self._slice_img()
        x = np.arange(len(slice))
        fig = plt.figure(figsize=plt.figaspect(self.height/self.width))
        plt.plot(x, slice, color='red')
        plt.axhline(y=self.thresh, linestyle=':', color='blue')
        plt.margins(x=0, y=0)
        plt.axis('off')
        arr = fig2array(fig)
        plt.close()
        return arr
        
    def show_slice(self):
        slice = self.get_image_slice(self.y_slice)
        plt.imshow(slice)
        plt.show()
        
    def called_with(self):
        dict = {'filter': self.filter,
                'mode': self.mode,
                'offset': self.offset}
        return {**super().called_with(), **dict}
        
        
class WoundImage(BinaryImage):
    """
    Estimates area and mean width of the wound.
    min_objects define the minimal size of objects
    recognized inside the wound.
    min_wound define the minimal size of wound. Serves to
    eliminate falsely recognized wound objects.
    """

    def __init__(self, img_path):
        super().__init__(img_path)
        
    def __call__(self,   
                 disk_radius=1,
                 min_objects=1, min_wound=1,
                 border_size=3, border_color=(255, 0, 0),
                 **kwargs):
        super().__call__(**kwargs)
        self.disk_radius = disk_radius
        self.min_objects = min_objects
        self.min_wound = min_wound
        self.disk_radius = int(self.disk_radius)
        self.selem = disk(self.disk_radius)
        self.img_binary = self._less_details()
        self.pixels = np.prod(self.img_corrected.shape)
        black_granule_size = round(self.pixels*self.min_wound/100)
        white_granule_size = round(self.pixels*self.min_objects/100)
        # Removes objects inside the wound
        self.img_binary = self._remove_grains(self.img_binary,
                            white_granule_size)
        # Removes objects outside of the wound
        self.img_binary = self._remove_grains(np.logical_not(self.img_binary),
                            black_granule_size)
        # Makes wound borders
        border = ndi.maximum_filter(sobel(self.img_binary), border_size)
        if self.channel == 'BW':
            self.img_wound = np.dstack((self.img_original,) * 3)
        else:
            self.img_wound = self.img_original.copy()
        self.img_wound[border.nonzero()] = border_color
        
    def _less_details(self):
        img = self.img_binary
        img = binary_closing(img, self.selem)
        img = binary_opening(img, self.selem)
        return img
        
    def _slice_img(self):
        y = super()._slice_img()
        mean_kernel = np.full(self.disk_radius, 1/self.disk_radius)
        return np.convolve(y, mean_kernel, mode='valid')
    
    @staticmethod
    def _remove_grains(img, size):
        return remove_small_objects(img, min_size=size)
    
    def show_wound(self):
        fig = plt.figure()
        plt.imshow(self.img_wound, cmap='gray')
        plt.axis('off')
        plt.show()
        
    def get_stat(self):
        area = np.sum(self.img_binary)*100/self.pixels
        width = np.sum(self.img_binary) / self.height
        return [area, width]
    
    def get_images(self):
        sliced_img = self.get_sliced_img(True, 11)
        slice = self.get_image_slice()
        return [sliced_img, slice, self.img_wound]
        
    def called_with(self):
        dict = {'disk_radius': self.disk_radius,
                'min_objects': self.min_objects,
                'min_wound': self.min_wound}
        return {**super().called_with(), **dict}
        
    def view_images(self):
        fig, axes = plt.subplots(nrows=2, ncols=2,
                                 sharex=True, sharey=True)
        axes = axes.ravel()
        steps = [self.img_original, self.img_corrected,
                 self.img_binary, self.img_wound]
        titles = ['Original Image', 'Corrected Image',
                  'Binary Image', 'Wound Image']
        for ax, st, titl in zip(axes, steps, titles):
            if len(st.shape) == 2:
                ax.imshow(st, cmap='gray')
            else:
                ax.imshow(st)
            ax.set_title(titl)
            ax.axis('off')
        plt.tight_layout()
        plt.show()
        
    def get_wound_img(self):
        return self.img_wound
    