# -*- coding: utf-8 -*-
import matplotlib.pyplot as plot
import matplotlib.pylab as plt
import numpy as np
import imageio
import helpers
from skimage.draw import line
from scipy.ndimage.filters import gaussian_filter


# Helper functions for plotting images in Python (wrapper over matplotlib)    

def thumbnails(images, axis=0):
    
    if type(images) is np.ndarray:    
        n_images = images.shape[axis]
        if axis == 0:
            img_size = images.shape[1:]
        else:
            img_size = images.shape[:axis]
        images_x = int(np.ceil(np.sqrt(n_images)))
        images_y = int(np.ceil(n_images / images_x))
        size = (images_y, images_x)        
        output = np.zeros((size[0] * img_size[0], size[1] * img_size[1]))
        
        for r in range(n_images):
            bx = int(r % images_x)
            by = int(np.floor(r / images_x))
            if axis == 0:
                output[by*img_size[0]:(by+1)*img_size[0], bx*img_size[1]:(bx+1)*img_size[1]] = images[r,:,:].squeeze()
            elif axis == 2:
                output[by*img_size[0]:(by+1)*img_size[0], bx*img_size[1]:(bx+1)*img_size[1]] = images[:,:,r].squeeze()
    
    return output
    

def imsc(image, titles=None, figwidth=10, cmap='gray', ncols=None):
    """
    Universal function for plotting various structures holding series of images. Not thoroughly tested, but should work with:
    - np.ndarray of size (h,w,3) or (h,w)
    - lists or tuples of np.ndarray of size (h,w,3) or (h,w)    
    - np.ndarray of size (h,w,channels) -> channels shown separately
    - np.ndarray of size (1, h, w, channels)
    - np.ndarray of size (N, h, w, 3) and (N, h, w, 1)
    
    :param image: input image structure (see details above)
    :param titles: a single string or a list of strings matching the number of images in the structure
    :param figwidth: width of the figure
    :param cmap: color map
    """
        
    if type(image) is list or type(image) is tuple:
        
        if titles is not None and type(titles) is str:
            titles = [titles for x in range(len(image))]
        
        if len(titles) != len(image):
            raise RuntimeError('Provided titles ({}) do not match the number of images ({})!'.format(len(titles), len(image)))
        
        subplot_x = ncols or int(np.ceil(np.sqrt(len(image))))
        subplot_y = int(np.ceil(len(image) / subplot_x))
        
        fig = plot.figure(tight_layout=True, figsize=(figwidth, figwidth * (subplot_y / subplot_x)))
        plot.ioff()
        
        for n, i in enumerate(image):
            ax = fig.add_subplot(subplot_y, subplot_x, n + 1)
            quickshow(i, titles[n] if titles is not None else None, axes=ax, cmap=cmap)
            
        return fig
            
    if type(image) in [np.ndarray, imageio.core.util.Image]:
        
        if image.ndim == 2 or (image.ndim == 3 and image.shape[-1] == 3):
            
            fig = plot.figure(tight_layout=True, figsize=(figwidth, figwidth))
            plot.ioff()
            quickshow(image, titles, axes=fig.gca(), cmap=cmap)
            
            return fig

        elif image.ndim == 3 and image.shape[-1] != 3:
            
            def fetch_example(image, n):
                return image[:,:,n]
            
            n_images = image.shape[-1]

            if n_images > 100:
                image = np.swapaxes(image, 0, -1)
                n_images = image.shape[-1]
                                        
        elif image.ndim == 4 and (image.shape[-1] == 3 or image.shape[-1] == 1):
            
            n_images = image.shape[0]
            
            def fetch_example(image, n):
                return image[n, :, :, :]
            
        elif image.ndim == 4 and image.shape[0] == 1:

            n_images = image.shape[-1]
            
            def fetch_example(image, n):
                return image[:, :, :, n]             

        else:
            raise ValueError('Unsupported array dimensions {}!'.format(image.shape))

        if n_images > 100:
            raise RuntimeError('The number of subplots exceeds reasonable limits ({})!'.format(n_channels))                            
            
        subplot_x = ncols or int(np.ceil(np.sqrt(n_images)))
        subplot_y = int(np.ceil(n_images / subplot_x))            
            
        if titles is not None and type(titles) is str:
            titles = [titles for x in range(n_images)]
        
        if len(titles) != n_images:
            raise RuntimeError('Provided titles ({}) do not match the number of images ({})!'.format(len(titles), n_channels))
            
        fig = plot.figure(tight_layout=True, figsize=(figwidth, figwidth * (subplot_y / subplot_x)))
        plot.ioff()
            
        for n in range(n_images):
            ax = fig.add_subplot(subplot_y, subplot_x, n + 1)
            quickshow(fetch_example(image, n), titles[n] if titles is not None else None, axes=ax, cmap=cmap)
        
        return fig
            
    else:
        raise ValueError('Unsupported array type {}!'.format(type(image)))
                
    return fig

def quickshow(x, label=None, *, axes=None, cmap='gray'):
    """
    Simple function for plotting images. Adds the title and hides axes' ticks. The '{}' substring in the title 
    will be replaced with '(height x width) -> [min intensity - max intensity]'.
    """
    
    label = label or '{}'
    
    x = x.squeeze()
    
    if '{}' in label:
        label = label.replace('{}', '({}x{}) -> [{:.2f} - {:.2f}]'.format(*x.shape[0:2], np.min(x), np.max(x)))
        
    if axes is None:
        plt.imshow(x, cmap=cmap)
        plt.title(label)
        plt.xticks([])
        plt.yticks([])
    else:
        axes.imshow(x, cmap=cmap)
        axes.set_title(label)
        axes.set_xticks([])
        axes.set_yticks([])        