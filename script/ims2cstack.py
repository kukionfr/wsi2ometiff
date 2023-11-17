import pyvips  #must use conda to install
import os
import glob
from natsort import natsorted
from time import time

def ims2ometiff(ims,output_dir,q,compression):
    imobjs = []
    for idx,im in enumerate(ims):
        impth = os.path.join(input_dir, im)
        imobj = pyvips.Image.new_from_file(impth)
        # imobj = pyvips.Image.openslideload(impth,level=0)
        if imobj.hasalpha(): imobj = imobj[:-1]
        imobjs.append(pyvips.Image.arrayjoin(imobj.bandsplit(), across=1))
    c = len(imobjs)
    print('N channels :',c)

    if imobj.interpretation == 'b-w':
        bitdepth = 8
    elif imobj.interpretation == 'grey16':
        bitdepth = 16

    outputfilepath = os.path.join(output_dir, 'C{}_Q{}_B{}_{}.ome.tiff'.format(c, q, bitdepth, compression))

    comp = pyvips.Image.arrayjoin(imobjs, across=1)
    image_height = imobj.height
    image_width = imobj.width
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
                    SizeC="{len(imobjs)}"
                    SizeT="1"
                    SizeX="{image_width}"
                    SizeY="{image_height}"
                    SizeZ="1"
                    Type="uint{bitdepth}">
            </Pixels>
        </Image>
    </OME>""")

    #jpeg,jp2k,lzw,
    print('bit depth: {}'.format(bitdepth))
    print('saving image in {} format ...'.format(compression))
    # jp2k breaks the format somehow
    start=time()

    # 75% compression by default
    comp.tiffsave(outputfilepath, compression=compression, tile=True,
                  tile_width=512, tile_height=512, Q=q,
                  pyramid=True, subifd=True, bigtiff=True)
    print('elapsed time: {}'.format(round(time()-start)))
    print('ome-tiff saved here: ',outputfilepath)

if __name__=='__main__':
    input_dir = '/Volumes/Digital pathology image lib/MxIF SFC/TMA_S1/align_wsi/ReadDsf1_OutDsf1_2'
    output_dir = os.path.join(input_dir, 'cstack')
    if not os.path.exists(output_dir): os.mkdir(output_dir)
    ims = glob.glob(os.path.join(input_dir,'*.jpg')) + glob.glob(os.path.join(input_dir,'*.png')) + glob.glob(os.path.join(input_dir,'*.tif')) + glob.glob(os.path.join(input_dir,'*.tiff'))
    ims = natsorted(ims)
    # ims = ims[0:2]
    c=len(ims)
    q=30
    compression='none' #jpeg only support 8bit, so try none for 16bit
    ims2ometiff(ims,output_dir,q,compression)
