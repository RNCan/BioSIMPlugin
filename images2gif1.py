""" MODULE images2gif
Provides a function (writeGif) to write animated gif from a series
of PIL images or numpy arrays.
This code is provided as is, and is free to use for all.
Almar Klein (June 2009)
- based on gifmaker (in the scripts folder of the source distribution of PIL)
- based on gif file structure as provided by wikipedia
"""

try:
    import PIL
    from PIL import Image, ImageChops
    from PIL.GifImagePlugin import getheader, getdata
except ImportError:
    PIL = None

try:
    import numpy as np
except ImportError:
    np = None    

# getheader gives a 87a header and a color palette (two elements in a list).
# getdata()[0] gives the Image Descriptor up to (including) "LZW min code size".
# getdatas()[1:] is the image data itself in chuncks of 256 bytes (well
# technically the first byte says how many bytes follow, after which that
# amount (max 255) follows).


def intToBin(i):
    """ Integer to two bytes """
    # devide in two parts (bytes)
    i1 = i % 256
    i2 = int( i/256)
    # make string (little endian)
    return chr(i1) + chr(i2)


def getheaderAnim(im):
    """ Animation header. To replace the getheader()[0] """
    bb = "GIF89a"
    bb += intToBin(im.size[0])
    bb += intToBin(im.size[1])
    bb += "\x87\x00\x00"
    return bb


def getAppExt(loops=0):
    """ Application extention. Part that secifies amount of loops. 
    if loops is 0, if goes on infinitely.
    """
    bb = "\x21\xFF\x0B"  # application extension
    bb += "NETSCAPE2.0"
    bb += "\x03\x01"
    if loops == 0:
        loops = 2**16-1
    bb += intToBin(loops)
    bb += '\x00'  # end
    return bb


def getGraphicsControlExt(duration=0.1, dispose=2,transparent_flag=0,transparency_index=0):
    """ Graphics Control Extension. A sort of header at the start of
    each image. Specifies transparancy and duration. """
    bb = '\x21\xF9\x04'
    bb += chr(((dispose & 3) << 2)|(transparent_flag & 1))   # no transparancy
    bb += intToBin( int(duration*100) ) # in 100th of seconds
    bb += chr(transparency_index)   # no transparant color
    bb += '\x00'  # end
    return bb


def _writeGifToFile(fp, images, durations, loops,disposes):
    """ Given a set of images writes the bytes to the specified stream.
    """
    
    # init
    frames = 0
    previous = None
    
    for im in images:
        
        if not previous:
            # first image
            
            # gather data
            palette =getheader(im)[1] #
            if not palette:	
               palette = im.palette.tobytes()
            data = getdata(im)
            imdes, data = data[0], data[1:]            
            header = getheaderAnim(im)
            appext = getAppExt(loops)
            graphext = getGraphicsControlExt(durations[0])
            
            # write global header
            fp.write(header)
            fp.write(palette)
            fp.write(appext)
            
            # write image
            fp.write(graphext)
            fp.write(imdes)
            for d in data:
                fp.write(d)
            
        else:
            # gather info (compress difference)              
            data = getdata(im) 
            imdes, data = data[0], data[1:]       
            graphext = getGraphicsControlExt(durations[frames])
            
            # write image
            fp.write(graphext)
            fp.write(imdes)
            for d in data:
                fp.write(d)

#             # delta frame - does not seem to work
#             delta = ImageChops.subtract_modulo(im, previous)            
#             bbox = delta.getbbox()
#             
#             if bbox:
#                 
#                 # gather info (compress difference)              
#                 data = getdata(im.crop(bbox), offset = bbox[:2]) 
#                 imdes, data = data[0], data[1:]       
#                 graphext = getGraphicsControlExt(durations[frames])
#                 
#                 # write image
#                 fp.write(graphext)
#                 fp.write(imdes)
#                 for d in data:
#                     fp.write(d)
#                 
#             else:
#                 # FIXME: what should we do in this case?
#                 pass
        
        # prepare for next round
        previous = im.copy()        
        frames = frames + 1

    fp.write(";")  # end gif
    return frames


def writeGif(filename, images, duration=0.1, loops=0, dither=1,dispose=None):
    """ writeGif(filename, images, duration=0.1, loops=0, dither=1)
    Write an animated gif from the specified images. 
    images should be a list of numpy arrays of PIL images.
    Numpy images of type float should have pixels between 0 and 1.
    Numpy images of other types are expected to have values between 0 and 255.
    """
    
    if PIL is None:
        raise RuntimeError("Need PIL to write animated gif files.")
    
    images2 = []

	# convert to PIL
    for im in images:
        im=im.convert('RGB',dither=dither,colors=255)
        if PIL and isinstance(im, PIL.Image.Image):
          im2=im.convert('P',dither=dither,colors=255)
          images2.append(im2)
        elif np and isinstance(im, np.ndarray):
            if im.dtype == np.uint8:
                pass
            elif im.dtype in [np.float32, np.float64]:
                im = im.copy()
                im[im<0] = 0
                im[im>1] = 1
                im *= 255
                im = im.astype(np.uint8)
            else:
                im = im.astype(np.uint8)
            # convert
            if len(im.shape)==3 and im.shape[2]==3:
              im = Image.fromarray(im,'RGB').convert('P',dither=dither,colors=255)
            elif len(im.shape)==2:
               im = Image.fromarray(im,'L').convert('P',dither=dither,colors=255)
            else:
                raise ValueError("Array has invalid shape to be an image.")
            images2.append(im)
           
        else:
            raise ValueError("Unknown image type.")
  
    # check duration
    if hasattr(duration, '__len__'):
        if len(duration) == len(images2):
            durations = [d for d in duration]
        else:
            raise ValueError("len(duration) doesn't match amount of images.")
    else:
        durations = [duration for im in images2]
        
    if dispose is None:
        dispose = 2
    if hasattr(dispose, '__len__'):
        if len(dispose) != len(images2):
            raise ValueError("len(xy) doesn't match amount of images.")
    else:
        dispose = [dispose for im in images2]
		
		
    #images2=convertImagesToPIL(images2,dither)
    # open file
    fp = open(filename, 'wb')
    
    # write
    try:
        n = _writeGifToFile(fp, images2, durations, loops,dispose)
        print n, 'frames written'
    finally:
        fp.close()