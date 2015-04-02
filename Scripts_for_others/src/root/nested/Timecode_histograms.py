translate_to_us = True

# for cropping the perimeter pixels as these often don't equalise
xmin = 1
xmax = 254
ymin = 1
ymax = 254

input_path =  '/mnt/hgfs/VMShared/Data/new_sensors/suny_01042015/50nm_threshold/415/'
output_path = '/mnt/hgfs/VMShared/temp/SUNY/'

def GetTimecodes_AllFilesInDir(path, winow_xmin = 0, winow_xmax = 999, winow_ymin = 0, winow_ymax = 999, offset_us = 0, translate_to_us = False):
    import string, os
    
    timecodes = []
    files = []
    
    for filename in os.listdir(path):
        files.append(path + filename)

    nfiles = 0
    for filename in files:
        datafile = open(filename)
        nfiles += 1
        lines = datafile.readlines()
        
        if len(lines) > 20000: continue #skip files which glitched (most pixels hit - parameter may need tuning)
        for line in lines:
            x,y,timecode = string.split(str(line),'\t')
            x = int(x)
            y = int(y)
            timecode = int(timecode)
            if timecode == 11810: continue  #discard overflows
            if timecode == 1: continue      #discard noise hits
            if x>=winow_xmin and x<=winow_xmax and y>=winow_ymin and y<=winow_ymax:
                if translate_to_us == True:
                    actual_offset_us = 250 - offset_us
                    time_s = (11810. - timecode) * 20e-9
                    time_us = (time_s *1e6)- actual_offset_us
                    timecodes.append(time_us)
                else:
                    timecodes.append(timecode)

    print "Loaded data from %s files"%nfiles
    return timecodes



def MakeToFSpectrum(translate_to_us = True):
    import pylab as pl
    
    timecodes = GetTimecodes_AllFilesInDir(input_path, xmin, xmax, ymin, ymax, 110, translate_to_us)
    print 'Total number of timecodes read in = %s' %len(timecodes)
     
    if translate_to_us:
        tmin = 5
        tmax = 25
        bins = (((tmax-tmin))*50) - 1 #1 timecode per bin
    else:
#         tmin = 0         # full range
#         tmax = 11810     # full range
        tmin = 3900
        tmax = 4400
        bins = (tmax-tmin) +1 
     
    fig = pl.figure()
    
    pl.hist(timecodes, bins = bins, range = [tmin,tmax]) #make the histogram of the timecodes
    
#     pl.ylim([0,2000]) #for clipping the y-axis
    pl.xlim([tmin,tmax]) #for clipping the x-axis
   
    
    if translate_to_us:
        pl.xlabel('ToF (us)', horizontalalignment = 'right' )
    else:
        pl.xlabel('Timecodes', horizontalalignment = 'right' )
    
    pl.title('Timepix ToF Spectrum')
    fig.savefig(output_path + 'Full_ToF.png')
    
     
################## can redefine the x-axis and re-save here to zoom in on certain peaks:
#     pl.xlim([7100,7170])
#     fig.savefig(out_stem + path + 'ToF_ROI.png')
#     pl.xlim([6900,7170])
#     fig.savefig(out_stem + path + 'ToF_ROI_More.png')
##################
    
    pl.show() #to show as an active object - allows zooming etc. Can be removed if you just want to look at the files
    
    
if __name__ == '__main__':
    print "Running Timecode Histograms..."
    
    MakeToFSpectrum(translate_to_us)
    
    print '\n***End code***'







