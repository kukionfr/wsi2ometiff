import pyvips  #must use conda to install
import os
import glob
from natsort import natsorted
from time import time

def ims2ometiff(ims,outputfilepath):
    imobjs = []
    for idx,im in enumerate(ims):
        impth = os.path.join(input_dir, im)
        imobj = pyvips.Image.new_from_file(impth)
        # imobj = pyvips.Image.openslideload(impth,level=0)
        if imobj.hasalpha(): imobj = imobj[:-1]
        imobjs.append(pyvips.Image.arrayjoin(imobj.bandsplit(), across=1))
    print('z stack height :',len(imobjs))
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
                    SizeC="3"
                    SizeT="1"
                    SizeX="{image_width}"
                    SizeY="{image_height}"
                    SizeZ="{len(imobjs)}"
                    Type="uint8">
            </Pixels>
        </Image>
    </OME>""")

    #jpeg,jp2k,lzw,
    print('saving image...')
    # jp2k breaks the format somehow
    start=time()

    # 75% compression by default
    comp.tiffsave(outputfilepath, compression="jpeg", tile=True,
                  tile_width=512, tile_height=512, Q=30,
                  pyramid=True, subifd=True, bigtiff=True)
    print('elapsed time: {}'.format(round(time()-start)))
    print('ome-tiff saved here: ',outputfilepath)

if __name__=='__main__':
    input_dir = '/Volumes/Digital pathology image lib/SenNet JHU TDA Project/SN-LW-PA-P003-B1_SNP004/HESS/AlignIM/run5/Dalign__imdsf2__dsfout1_padsz500'
    output_dir = os.path.join(input_dir, 'zstack')
    if not os.path.exists(output_dir): os.mkdir(output_dir)
    ims = glob.glob(os.path.join(input_dir,'*.jpg')) + glob.glob(os.path.join(input_dir,'*.png')) + glob.glob(os.path.join(input_dir,'*.tif')) + glob.glob(os.path.join(input_dir,'*.tiff'))
    ims = natsorted(ims)
    # ims = ims[0:10] #can do 5; cant do 6
    print('processing {} images'.format(len(ims)))
    ims2ometiff(ims,os.path.join(output_dir,'Z54_Q30_jpeg.ome.tiff'))
