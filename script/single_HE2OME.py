import pyvips  #must use conda to install
import os
import glob
from natsort import natsorted
from time import time

def im2ometiff(impth,outputfilepath):
    imobj = pyvips.Image.new_from_file(impth)
    if imobj.hasalpha(): imobj = imobj[:-1]
    image_height = imobj.height
    image_width = imobj.width
    comp = pyvips.Image.arrayjoin(imobj.bandsplit(), across=1)
    comp = comp.copy()
    # set minimal OME metadata
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
    input_dir = '/Volumes/Digital pathology image lib/SenNet JHU TDA Project/SN-LW-PA-P003-B1_SNP004/HESS/AlignIM/run5/Dalign__imdsf2__dsfout1_padsz500/z-0001_2023-07-24 13.35.07.jpg'
    output_dir = os.path.join(os.path.dirname(input_dir),'processed_images')
    if not os.path.exists(output_dir): os.mkdir(output_dir)
    im2ometiff(input_dir,os.path.join(output_dir,'he_jp2k.ome.tiff'))
