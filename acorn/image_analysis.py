
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance
from PIL.ImageOps import invert
from PIL.ImageFilter import GaussianBlur
from skimage.filters import threshold_otsu, threshold_mean, threshold_minimum 
from skimage.morphology import watershed, binary_opening, binary_closing
from skimage.morphology import disk, remove_small_objects
from scipy import ndimage as ndi
from skimage.filters import sobel, roberts
from skimage.feature import corner_peaks
from skimage.exposure import equalize_adapthist
from .accessory_functions import *
from math import floor


class CorrectedImage:
    """
    Loads image and performs its basic correction using
    PIL tools.
    """
    
    def __init__(self, img_path):
        self.img_path = img_path
        self.PILimg = None
        self.channel = None
        self.bright = None
        self.contr = None
        self.blur_radius = None
        self.equal_exposure = None
        self.inverse = None
        self.img_corrected = None
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

    def get_img_original(self):
        return self.img_original.copy()
    
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
            ax1.imshow(self.img_original, cmap='gray')
        ax1.set_title('Original image')
        ax1.axis('off')
        ax2.imshow(self.img_corrected, cmap='gray')
        ax2.set_title('Corrected image')
        ax2.axis('off')
        plt.show()
        
    def called_with(self):
        """
        Return arguments of the __call__ function.
        """
        d = {'channel': self.channel,
             'bright': self.bright,
             'contr': self.contr,
             'blur_radius': self.blur_radius,
             'equal_exposure': self.equal_exposure,
             'inverse': self.inverse}
        return d
    
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
        self.pre_binary = None
        self.img_binary = None
        self.y_slice = None
        self.thresh = None
        
    def __call__(self, filt,
                 mode='Borders',
                 offset=0, y_slice=None,
                 **kwargs):
        super().__call__(**kwargs)
        self.filt = filt
        self.mode = mode
        self.offset = offset
        if y_slice is None:
            self.y_slice = int(self.height / 2)
        if self.mode == 'Borders':
            self.pre_binary = sobel(self.img_corrected)
        elif self.mode == 'Contrast' or self.mode == 'Contrast-positive':
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
        elif self.mode == 'Contrast-positive':
            self.img_binary = self.pre_binary > self.thresh
        return self.img_binary
    
    def _get_filter(self):
        d = {'Mean': threshold_mean,
             'Otsu': threshold_otsu,
             'Minimum': threshold_minimum}
        return d.get(self.filt)
    
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
        im_slice = self._slice_img()
        x = np.arange(len(im_slice))
        fig = plt.figure(figsize=plt.figaspect(self.height/self.width))
        plt.plot(x, im_slice, color='red')
        plt.axhline(y=self.thresh, linestyle=':', color='blue')
        plt.margins(x=0, y=0)
        plt.axis('off')
        arr = fig2array(fig)
        plt.close()
        return arr
        
    def show_slice(self):
        im_slice = self.get_image_slice(self.y_slice)
        plt.imshow(im_slice)
        plt.show()
        
    def called_with(self):
        d = {'filt': self.filt,
             'mode': self.mode,
             'offset': self.offset}
        return {**super().called_with(), **d}
        
        
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
        self.pixels = 0
        self.disk_radius = 1
        self.min_wound = 1
        self.min_objects = 1
        
    def __call__(self,   
                 disk_radius,
                 min_objects, min_wound,
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
        area = np.sum(self.img_binary) * 100 / self.pixels
        width = np.sum(self.img_binary) / self.height
        return (area, width)

    def get_report_stat(self):
        area, width = self.get_stat()
        return {'wound_area': round(area, 2),
                'wound_width': round(width, 2)}
    
    def get_images(self):
        sliced_img = self.get_sliced_img(True, 11)
        im_slice = self.get_image_slice()
        return [sliced_img, im_slice, self.img_wound]
        
    def called_with(self):
        d = {'disk_radius': self.disk_radius,
             'min_objects': self.min_objects,
             'min_wound': self.min_wound}
        return {**super().called_with(), **d}
        
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
        
    def get_save_img(self):
        return self.img_wound


class CellCounter:
    
    def __init__(self, img_path):
        self.binary_filter = 'Minimum'
        self.mask_filter = 'Otsu'
        self.offset_binary = 0
        self.offset_mask = 0
        self.min_dist = 0
        self.disk_radius = 0
        self.size_thresh = 0
        self.binary_im = BinaryImage(img_path)
        self.size_thresh = 0
        self.img_binary = None
        self.img_binary_mask = None
        self.img_labeled = None
        self.img_cells = None
        self.img_debris = None
        self.N_objects = 0
        self.N_cells = 0
        self.N_debris = 0

    def __call__(self, binary_filter=None, mask_filter=None,
                 offset_binary=None, offset_mask=None,
                 min_dist=None, disk_radius=None,
                 size_thresh=None,
                 **kwargs):
        self.binary_filter = binary_filter or self.binary_filter
        self.mask_filter = mask_filter or self.mask_filter
        self.offset_binary = offset_binary or self.offset_binary
        self.offset_mask = offset_mask or self.offset_mask
        self.min_dist = min_dist or self.min_dist
        self.disk_radius = disk_radius or self.disk_radius
        self.size_thresh = size_thresh or self.size_thresh
        self.img_binary = self.binary_im(filt=binary_filter,
                mode='Contrast-positive',
                offset=self.offset_binary, **kwargs)
        self.img_binary_mask = self.binary_im(filt=mask_filter,
                mode='Contrast-positive',
                offset=self.offset_mask, **kwargs)      
        distance = ndi.distance_transform_edt(self.img_binary)
        foot_print = disk(self.disk_radius)
        peaks = corner_peaks(distance, indices=False,
                             min_distance=int(self.min_dist),
                             footprint=foot_print)
        markers = ndi.label(peaks)[0]
        self.img_labeled = watershed(-distance, markers,
                                 mask=self.img_binary_mask,
                                 watershed_line=True)
        num, inv, self.size = np.unique(self.img_labeled,
                                        return_inverse=True,
                                        return_counts=True)
        inv.shape = self.img_binary.shape
        self.img_cells = self.img_labeled.copy()
        self.img_cells[(self.size < self.size_thresh)[inv]] = 0
        self.img_debris = (self.size < self.size_thresh)[inv]
        self.N_objects = max(num)
        self.N_cells = np.sum(self.size[1:] >= self.size_thresh)
        self.N_debris = self.N_objects - self.N_cells

    def get_stat(self):
        return (self.N_objects, self.N_debris, self.N_cells)

    def get_additional_stat(self):
        cell_size = self.size[1:][self.size[1:] >= self.size_thresh]
        mean_cell_size = np.mean(cell_size)
        sd_cell_size = np.std(cell_size)
        confl = np.sum(self.img_cells > 0)/np.prod(self.img_cells.shape)
        return (mean_cell_size, sd_cell_size, confl*100)
    
    def get_report_stat(self):
        stat = self.get_stat() + self.get_additional_stat()
        headers = ['N_objects', 'N_cells', 'N_debris',
                   'mean_cell_size', 'sd_cell_size', 'confl']
        d = {}
        for head, st in zip(headers, stat):
            d[head] = st if st == int(st) else round(st, 2)
        return d

    def get_outlined_cells(self, border_size=1,
                           border_color=(255, 0, 0)):
        img_outlined = self.binary_im.get_img_original()
        if len(img_outlined.shape) == 2:
            img_outlined = np.dstack((img_outlined,) * 3)
        img_borders = roberts(self.img_cells) > 0
        if border_size > 1:
            img_borders = ndi.maximum_filter(img_borders, border_size)
        img_outlined.setflags(write=True)
        img_outlined[img_borders] = (255, 0, 0)
        return img_outlined

    def called_with(self):
        binary_call = self.binary_im.called_with()
        del binary_call['filt']
        del binary_call['offset']
        d = {'binary_filter': self.binary_filter,
             'mask_filter': self.mask_filter,
             'offset_binary': self.offset_binary,
             'offset_mask': self.offset_mask,
             'min_dist': self.min_dist,
             'disk_radius': self.disk_radius,
             'size_thresh': self.size_thresh}
        return {**binary_call, **d}

    def get_PILimg(self):
        return self.binary_im.PILimg

    def get_images(self):
        img_debris_bw = self.img_debris.astype(np.uint8) * 255
        color_map = generate_cmap(self.N_objects + 1)
        img_cells_color = color_map(self.img_cells) * 255
        img_cells_color = img_cells_color.astype(np.uint8)
        return [self.binary_im.img_corrected,
                img_debris_bw,
                #img_cells_color
                self.get_outlined_cells()]

    def get_image_path(self):
        return self.binary_im.img_path

    def view_images(self):
        images = [self.binary_im.img_original] + self.get_images()
        titles = ['Original image', 'Corrected image',
                  'Debris', 'Cells']
        #color_maps = ['']
        fig, axes = plt.subplots(ncols=2, nrows=2,
                    sharex=True, sharey=True)
        axes = axes.ravel()
        for ax, img, title in zip(axes, images, titles):
            if len(img.shape) == 2:
                ax.imshow(img, 'gray')
            else:
                ax.imshow(img)
            ax.set_title(title)
            ax.axis('off')
        plt.tight_layout()
        plt.show()
    
    def get_save_img(self):
        return self.get_outlined_cells()

# поправить cхему выбора порогов в BinaryImage