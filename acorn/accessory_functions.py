
import numpy as np
import matplotlib.pyplot as plt #import imsave, switch_backend
from matplotlib.colors import LinearSegmentedColormap
from math import ceil
import csv
import os


def fig2array(fig):
    """
    Converts matplotlib plot into numpy array.
    """
    fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    arr = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    arr.shape = (h, w, 3)
    return arr  


def get_threshold(img, threshold_fun, offset_perc=0, **kwargs):
    """
    Gets threshold for image using threshold function.
    Offset should be provided as percentage value.
    """
    data_type = str(img.dtype)
    if data_type == 'bool' or data_type.startswith('float'):
        offset = offset_perc / 100
    elif data_type.startswith('uint'):
        fact = int(data_type.replace('uint', ''))
        offset = int(round(offset_perc * 2**fact / 100))
    else:
        raise ValueError('Incorrect data type of img: {}'.format(data_type))
    if len(kwargs) > 0:
        return threshold_fun(img, **kwargs) + offset
    return threshold_fun(img) + offset
    

def save_image(img, path, color_map='gray'):
    """
    Saves numpy images using matplotlib interface.
    """
    if len(img.shape) == 2:
        plt.imsave(path, img, cmap=color_map)
    else:
        plt.imsave(path, img)


def generate_cmap(N):
    """
    Generates N random colors for color map of matplotlib.
    """
    colors = [(0, 0, 0)]
    new_colors = [tuple(np.random.randint(1, 255, size=3)/255) for _ in range(N)]
    colors.extend(new_colors)
    cm = LinearSegmentedColormap.from_list("random_colors", colors, N=N)
    return cm


def is_even(N):
    return N % 2 == 0
  
  
def limit_text(text, limit, begin):
    if len(text) >= limit:
        x = len(text) - limit + begin + 3
        text = text[:begin] + '...' + text[x:]
    return text
 
 
def dict_identical(d1, d2):
    if len(d1) != len(d2):
        return False
    comp = [d2[key] == value for key, value in d1.items()]
    return all(comp)
  
  
def backend_switcher(fun):
    def switcher(*args, **kwargs):
        plt.switch_backend('TkAgg')
        fun(*args, **kwargs)
        plt.switch_backend('Agg')
    return switcher
   
   
def save_csv(table, fieldnames, filename):
    with open(filename, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, delimiter=";",
                                    fieldnames=fieldnames)
            writer.writeheader()
            for row in table:
                writer.writerow(row)
       
       
def read_csv(path, sep=';'):
    table = []
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=sep)
        for row in reader:
            table.append(row)
    return table


def file_namer(folder, basename='file', suffix=None, num=0, ext=''):
    num_str = str(num)
    add = 3 - len(num_str)
    if add > 0:
        num_str = '0' * add + num_str
    if suffix is None:
        name = basename + '_' + num_str
    else:
        name = basename + '_' + suffix + '_' + num_str
    proposed = os.path.join(folder, '.'.join([name, ext]))
    if os.path.exists(proposed):
        num += 1
        return file_namer(folder, basename, suffix, num, ext)
    else:
        return proposed


# def get_image_slice(img, y_slice, threshold, res):
#         y = int(y_slice*img.shape[1]/100)
#         im_slice = img[y,]
#         x = np.arange(len(im_slice))
#         fig = plt.figure(figsize=plt.figaspect(res[0]/res[1]))
#         plt.plot(x, im_slice, color='red')
#         plt.axhline(y=threshold, linestyle=':', color='blue')
#         plt.margins(x=0, y=0)
#         plt.axis('off')
#         arr = fig2array(fig)
#         plt.close()
#         return arr