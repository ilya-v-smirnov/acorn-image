
# import numpy as np
# import matplotlib.pyplot as plt
from PIL import Image
# from accessory_functions import get_image_slice

import tkinter as tk
from widgets import ImageButton, SlicePlotButton

print('Hello')

photo = Image.open('D:\\Google Drive\\Sample Images\\Wounds\\01.JPG')


class App(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        im_but = ImageButton(self, PILimg=photo, res=(300, 200))
        im_but.grid(row=0, column=0)
        star = SlicePlotButton(self, photo, y_slice=50, threshold=50, res=(300, 200))
        star.grid(row=0, column=0)

root = tk.Tk()
app = App(root)
app.pack()
root.mainloop()


# img = np.asarray(photo)

# plot = get_image_slice(img, 50, 100, (300, 200))

# fig = plt.figure()
# plt.imshow(plot)
# plt.show()