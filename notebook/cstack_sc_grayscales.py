# For Windows, please add the follow prior to importing pyvips
# import os
# vipshome = 'c:\\vips-dev-8.7\\bin'
# os.environ['PATH'] = vipshome + ';' + os.environ['PATH']

import pyvips  #must use conda to install for acquiring binaries
import os
import glob
from natsort import natsorted
from time import time

# assume all images have the same dimensions
# input = paths to single channel grayscale images
# output = multi-channel grayscale images in ome.tiff format
def ims2ometiff(ims,outputfilepath):
    imobjs = []
    for idx,im in enumerate(ims):
        impth = os.path.join(input_dir, im)
        imobj = pyvips.Image.new_from_file(impth)
        # imobj = pyvips.Image.openslideload(impth,level=0)
        if imobj.hasalpha(): imobj = imobj[:-1]
        imobjs.append(imobj)
        print('image {} has dimensions [{},{}]'.format(idx,imobj.height,imobj.width))
    print('z stack height :',len(imobjs))
    comp = pyvips.Image.arrayjoin(imobjs, across=1)
    image_height = imobj.height
    image_width = imobj.width
    image_bands = len(imobjs)
    comp = comp.copy()

    # set minimal OME metadata
    # before we can modify an image (set metadata in this case), we must take a
    # private copy
    comp.set_type(pyvips.GValue.gint_type, "page-height", image_height)
    comp.set_type(pyvips.GValue.gstr_type, "image-description",
                  f"""<?xml version="1.0" encoding="UTF-8"?>
    <OME xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.openmicroscopy.org/Schemas/OME/2016-06 http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd">
        <Image ID="Image:0">
            <!-- Minimum required fields about image dimensions -->
            <Pixels DimensionOrder="XYCZT"
                    ID="Pixels:0"
                    SizeC="{image_bands}"
                    SizeT="1"
                    SizeX="{image_width}"
                    SizeY="{image_height}"
                    SizeZ="1"
                    Type="uint8">
            </Pixels>
        </Image>
    </OME>""")


    #jpeg,jp2k,lzw,
    print('saving image...')
    # jp2k breaks the format somehow
    start=time()
    comp.tiffsave(outputfilepath, compression="jp2k", tile=True,
                  tile_width=512, tile_height=512,
                  pyramid=True, subifd=True)
    print('elapsed time: {}'.format(round(time()-start)))
    print('ome-tiff saved here: ',outputfilepath)

if __name__=='__main__':
    # Define input image paths
    input_dir = '/Volumes/Digital pathology image lib/JHU/Laura Wood/IF for SenPan001/sec125/align_wsi'
    ims = glob.glob(os.path.join(input_dir,'*.tif'))
    ims = natsorted(ims)
    # ims = [_ for _ in ims if 'round02' in _]
    print(len(ims))
    # Define output image path
    output_dir = os.path.join(input_dir, 'zstack')
    if not os.path.exists(output_dir): os.mkdir(output_dir)
    # Execute the function
    ims2ometiff(ims,os.path.join(output_dir,'jp2k.ome.tiff'))
