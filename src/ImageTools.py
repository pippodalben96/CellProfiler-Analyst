'''
ImageTools.py
Authors: afraser

A collection of tools to modify images used in CPA.
'''

import numpy
import operator
import wx
from Properties import Properties

p = Properties.getInstance()


def ShowImage(imKey, chMap, parent=None):
    from ImageViewer import ImageViewer
    from ImageCollection import ImageCollection
    IC = ImageCollection.getInstance()
    imgs = IC.FetchImage(imKey)
    frame = ImageViewer(imgs=imgs, chMap=chMap, parent=parent, title=str(imKey) )
    frame.Show(True)
    return frame
    

def Crop(imgdata, (w,h), (x,y)):
    '''
    Crops an image to the width (w,h) around the point (x,y).
    Area outside of the image is filled with the color specified.
    '''
    imWidth = imgdata.shape[1]
    imHeight = imgdata.shape[0]
    crop = numpy.zeros((h,w), dtype='float32')
    for px in xrange(w):
        for py in xrange(h):
            xx = px+x-w/2
            yy = py+y-h/2
            if 0<=xx<imWidth and 0<=yy<imHeight:
                crop[py,px] = imgdata[yy,xx]
            else:
                crop[py,px] = 0
    return crop


#def GetRectangleMask(w,h):
#    mask = numpy.zeros((h,w,3),dtype='float')
#    mask[0:h,0,:]   = 1.0 # left
#    mask[0,0:w,:]   = 1.0 # top
#    mask[0:h,-1,:]  = 1.0 # right
#    mask[-1,0:w,:]  = 1.0 # bottom
#    return mask 
    
    

def MergeToBitmap(imgs, chMap, brightness=1.0, scale=1.0, masks=[]):
    '''
    imgs  - list of numpy arrays containing pixel data for each channel of an image
    chMap - list of colors to map each corresponding channel onto.  eg: ['red', 'green', 'blue']
    brightness - value around 1.0 to multiply color values by
    contrast - value around 1.0 to scale contrast by
    scale - value around 1.0 to scale the image by
    '''
    
    imData = MergeChannels(imgs, chMap, masks=masks)
    h,w = imgs[0].shape
    
    # Convert from float [0-1] to 8bit
    imData *= 255.0
    imData[imData>255] = 255

    # Write wx.Image
    img = wx.EmptyImage(w,h)
    img.SetData(imData.astype('uint8').flatten())
    
    # Apply brightness, contrast & scale
    # TODO: Add contrast adjustment
    if brightness != 1.0:
        img = img.AdjustChannels(brightness, brightness, brightness)
    if scale != 1.0:
        if w*scale>10 and h*scale>10:
            img.Rescale(w*scale, h*scale)
        else:
            img.Rescale(10,10)
    
    return img.ConvertToBitmap()


def MergeChannels(imgs, chMap, masks=[]):
    '''
    Merges the given image data into the channels listed in chMap.
    Masks are passed in pairs (mask, blendingfunc).
    '''
    nChannels = len(p.image_channel_paths)
    h,w = imgs[0].shape
    imData = numpy.zeros((h,w,3),dtype='float')
    
    colormap = {'red'      : [1,0,0], 
                'green'    : [0,1,0], 
                'blue'     : [0,0,1], 
                'cyan'     : [0,1,1], 
                'yellow'   : [1,1,0], 
                'magenta'  : [1,0,1], 
                'gray'     : [1,1,1], 
                'none'     : [0,0,0] }
    
    for i, im in enumerate(imgs):
        c = colormap[chMap[i].lower()]
        for chan in range(3):
            imData[:,:,chan] += im * c[chan]
    
    for mask, func in masks:
        imData = func(imData, mask)
        imData[imData>1.0] = 1.0
        imData[imData<0.0] = 0.0
        
    return imData






