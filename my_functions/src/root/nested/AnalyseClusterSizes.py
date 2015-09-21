import os
               
from my_functions import *
import lsst.afw.display.ds9 as ds9
import lsst.afw.display.utils as displayUtils
import lsst.afw.detection   as afwDetect
from root_functions import ListToHist


DISPLAY = False



if __name__ == '__main__':
 
    xmin = 33
    ymin = 10
    xmax = 240
    ymax = 240
#     day = 'day3'
#     runs = ['run2','run3','run4','run5','run6','run7','run8']
#     runs = ['run5']
    
#     day = 'day4'
#     runs = ['run1']

    day = 'day1'
    runs = ['run2']
    
    
    for run in runs:
        data_path = '/mnt/hgfs/VMShared/Data/oxford/june_2015/'
        exp_type = 'timepix'
        
        data_path += day + '/'
        data_path += exp_type + '/'
        data_path += run + '/' 
        
        out_path = '/mnt/hgfs/VMShared/output/oxford/2015_june/temp/clusters/'
        out_path += day + run + '_'
        
        if DISPLAY:
            try:
                ds9.initDS9(False)
            except ds9.Ds9Error:
                print 'DS9 launch bug error thrown away (probably)'
    
    
    ###################################################################
    #         mask_list = GeneratePixelMaskListFromFileset(data_path, 0.1, file_limit=99999)  
    #         pixel_mask = MakeMaskArray(mask_list)  
    #         print 'masking %s pixels'%len(mask_list[0])
        
    ###         ViewIntensityArrayInDs9(-1*(pixel_mask-1), savefile=OUTPUT_PATH + str(val) + '_pixel_mask.jpeg')  
        
        thresholdValue = 1
        npixMin = 1
        grow = 0
        isotropic = False
        
        cluster_sizes = []
        pixels_per_frame_list = []
        footprint_pixels_per_frame_list = []
        ions_per_frame = []
        
        display_num = 120
        for filenum, filename in enumerate(os.listdir(data_path)):
            if filenum %100 == 0: print 'Processing file # %s'%filenum
            
#             image, npix = TimepixToExposure_binary(data_path + filename, xmin, xmax, ymin, ymax)
#             image, npix = TimepixToExposure_binary(data_path + filename, xmin, xmax, ymin, ymax, mask_pixels=pixel_mask)
            image, npix = TimepixToExposure_binary(data_path + filename, xmin, xmax, ymin, ymax)
            pixels_per_frame_list.append(npix)
            
            if DISPLAY == True and filenum == display_num: ds9.mtv(image)
            
            threshold = afwDetect.Threshold(thresholdValue)
            footPrintSet = afwDetect.FootprintSet(image, threshold, npixMin)
            footPrintSet = afwDetect.FootprintSet(footPrintSet, grow, isotropic)
            footPrints = footPrintSet.getFootprints()
            
            footprint_pixels = 0
            
            ions_per_frame.append(len(footPrints))
            for footprint in footPrints:
                if DISPLAY and filenum == display_num: displayUtils.drawBBox(footprint.getBBox(), borderWidth=0.5) # border to fully encompass the bbox and no more
                npix = afwDetect.Footprint.getNpix(footprint)
                cluster_sizes.append(npix)
                footprint_pixels += npix
            
            footprint_pixels_per_frame_list.append(footprint_pixels)
#             if filenum == display_num: exit()
            if DISPLAY and filenum == display_num:
                arg = 'saveimage jpeg ' + str(out_path + str(filenum) + '_example_frame.jpeg') + ' 100'
                ds9.ds9Cmd(arg)
        
        
        NORMALISE = True
        
        histmax = 70
        name = 'cluster_size'
        h1 = ListToHist(cluster_sizes, out_path + 'cluster_size.png', log_y = False, nbins = histmax-1, histmin = 1, histmax = histmax, name = name, normalise=NORMALISE)
        
#         histmax = 1.2* max(pixels_per_frame_list)
        histmax = 2501
        name = 'pixels_per_frame'
        h2 = ListToHist(pixels_per_frame_list, out_path + 'pixels_per_frame.png', log_y = False, nbins = 50, histmin = 1, histmax = histmax, name = name, normalise=NORMALISE)
        
        
        histmax = 151
        name = 'ions_per_frame'
        h3 = ListToHist(ions_per_frame, out_path + 'ions_per_frame.png', log_y = False, nbins = 50, histmin = 1, histmax = histmax, name = name, normalise=NORMALISE)
        
    print '\n***End code***'      
        
        
    
    
    