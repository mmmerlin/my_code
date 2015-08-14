import pylab as pl
from my_functions import *
import os

GLOBAL_OUT = []

xmin = 10
xmax = 245
ymin = 10
ymax = 245

out_path = '/mnt/hgfs/VMShared/output/oxford/2015_june/temp/'


#= laser exp ==============================================================================
timepix_path = '/mnt/hgfs/VMShared/Data/oxford/June_2015/Day4/timepix/'
offset     = 5282 #bigger moves left
finetune_1 = 0

# voltages = dict(run3=49,run4=100,run5=9,run6=20,run7=29,run8=40,run9=60,run10=69,run11=89,run12=80,run13=80)
voltages = dict(run3=49,run4=100)

NORMALISE = True


def MakeToFSpectrum():
    
    xpoints = []
    yseries = []
    
    for key in voltages:
        print key, voltages.get(key)
        path = os.path.join(timepix_path, key, '')
    
        timepix_timecodes_raw = GetTimecodes_AllFilesInDir(path, xmin, xmax, ymin, ymax, 0, checkerboard_phase = None)
    
        for i,code in enumerate(timepix_timecodes_raw):
            timepix_timecodes_raw[i] = (11810. - code) - offset
            timepix_timecodes_raw[i] *= 20
            
        timepix_nbins = 100
        
        fig = pl.figure(figsize=(14,10))
       
        values, bins, patches = pl.hist(timepix_timecodes_raw, bins = timepix_nbins, range = [0,2000])
    
        pl.clf()
        bins = bins[:-1] 
        
        if NORMALISE == True:
            pl.plot(bins-finetune_1, values/max(values), 'k-.o', label="Timepix Raw")
        else:
            pl.plot(bins-finetune_1, values,             'k-.o', label="Timepix Raw")
        
        print "Peak height raw = %s"%max(values)
        
        
    pl.legend()
    pl.xlim([100,1100])
    pl.ylim([0,1.1])
    pl.xlabel('Time (ns)', horizontalalignment = 'right' )

    pl.tight_layout()
    fig.savefig(out_path + 'T_res_voltage.png')
    pl.show()
    
    print "finished"
 

# def ShowRawToF():
#     raw_codes = GetTimecodes_AllFilesInDir(timepix_path, xmin, xmax, ymin, ymax, 0, checkerboard_phase = None)
#     offset = 5280#3700
#     tmin = 0
#     tmax = 11810
# 
#     for i,code in enumerate(raw_codes):
#         raw_codes[i] = (11810. - code) - offset
#         raw_codes[i] *= 20
#         
#     fig = pl.figure(figsize=(14,10))
#     n_codes, bins, patches = pl.hist(raw_codes, bins = 100, range = [0,2000])
# #     n_codes, bins, patches = pl.hist(raw_codes, bins = tmax-tmin, range = [tmin,tmax])
# 
# #     pl.clf()
# #     n_codes = n_codes[:-1] 
# #     pl.plot(bins, n_codes, 'k-.o', label="Timecodes")
#     
#     pl.tight_layout()
#     pl.show()
        
    
if __name__ == '__main__':
    print "Oxford June 2015..."

#     ShowRawToF()
#     exit()
    
    MakeToFSpectrum()
    print "Finished ToF Spectrum"
    exit()
    















