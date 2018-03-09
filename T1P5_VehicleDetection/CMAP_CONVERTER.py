import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import glob
from PIL import Image

def pil_conv(img_name):
    cm_hot = mpl.cm.get_cmap('hot')
    img_src = Image.open(img_name).convert('L')
    img_src.thumbnail((1280,720))
    im = np.array(img_src)
    im = cm_hot(im)
    im = np.uint8(im*255*5)
    im = Image.fromarray(im)
    return im

mod_list = glob.glob('./HeatMapsMOD/*')

for image in mod_list:
    current_mod = pil_conv(image)
    current_mod.save(image)

