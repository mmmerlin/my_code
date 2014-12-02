from __builtin__ import str, range, len # why does it put these in when that is unnecessary?!
import time


from ROOT import TCanvas, TF1, TH1F, TGraph, TLegend, TGraphErrors, TPaveText
from array import array
import numpy as np
from numpy.core.defchararray import zfill

# my stuff
from root_functions import GetFirstBinBelowX, DoubleGausFit, LanGausFit, LandauFit, ListToHist, ListVsList, CANVAS_HEIGHT, CANVAS_WIDTH
from TrackFitting import *
from ImageStat import Stat
import TrackViewer as TV
import TrackFitting


##########################################################################################
OUTPUT_PATH = "/mnt/hgfs/VMShared/output/edge_straightness/"


cosmic_pickle_file = '/mnt/hgfs/VMShared/output/datasets/edge_large_grow'
# cosmic_pickle_file = '/mnt/hgfs/VMShared/output/datasets/edge_tracks_200thr_gr2_px2_gain_corrected'


GLOBAL_OUT = []

if __name__ == '__main__':
    start_time = time.time()
    import cPickle as pickle
    print "Running PSF Calculator\n"

    t0 = time.time()
    all_tracks = pickle.load(open(cosmic_pickle_file, 'rb'))
    dt = time.time() - t0
    print "%s tracks unpickled in %.2f seconds" %(len(all_tracks),dt) 
    
    top_tracks = []
    bottom_tracks = []
    left_tracks = []
    right_tracks = []
    edge_tracks = []
    midline_tracks = []
    
    nstats = 0
    rawstats = len(all_tracks)
    
    discs = []
    all_tracks_temp = []

    ###################################################
####     Applying cuts, optionally re-saving dataset
    n_post_cut = 0
    for stat in all_tracks:
        if stat.length_true_um < 200: continue
        if stat.discriminator > 1500: continue
        
        n_post_cut += 1
        all_tracks_temp.append(stat)
        
        if stat.left_track == True:
            left_tracks.append(stat)            
        if stat.right_track == True:
            right_tracks.append(stat)            
        if stat.top_track == True:
            top_tracks.append(stat)            
        if stat.bottom_track == True:
            bottom_tracks.append(stat)            
        if stat.midline_track == True:
            midline_tracks.append(stat)      

    all_tracks = all_tracks_temp #remove cut tracks from the all_track dataset
       
    n_left = len(left_tracks)
    n_right = len(right_tracks)    
    n_top = len(top_tracks)    
    n_bottom = len(bottom_tracks)    
    n_midline = len(midline_tracks)      
    
    print "Total post cuts = %s" %n_post_cut
    print "left",   n_left
    print "right",  n_right
    print "top",    n_top
    print "bottom", n_bottom
    print "middle", n_midline
        
        
    ListToHist([stat.discriminator for stat in all_tracks], OUTPUT_PATH + 'discs.png', histmin = 0, histmax = 5000, nbins = 50)#, log_z, nbins, histmin, histmax)
    ListToHist([stat.LineOfBestFit.R2 for stat in all_tracks],OUTPUT_PATH + 'r2.png', histmin = 0, histmax = 1.1, nbins = 50)
    ListToHist([stat.npix for stat in all_tracks], OUTPUT_PATH + 'npix.png', histmin = 0, histmax = 1000, nbins = 100)
  
 
    c1 = TCanvas( 'canvas', 'canvas', 1600,800) #create canvas
    gr_left = TGraph() 
    max_distance = 50
    dev_max = 5 #in pixels
        
    deviations = np.zeros(max_distance, dtype = 'f8')
    point_counter = np.zeros(max_distance, dtype = 'f8')
    
    first_col_flux_list = []
        
#     for i,stat in enumerate(left_tracks + right_tracks + top_tracks + bottom_tracks):
    for i,stat in enumerate(right_tracks):
        legend_text = []
        legend_text.append('R^{2} = ' + str(round(stat.LineOfBestFit.R2,5)))
        legend_text.append('Chisq = ' + str(stat.LineOfBestFit.chisq_red))
        legend_text.append('Disc = ' + str(round(stat.discriminator,0)))
        legend_text.append(TrackFitting.GetEdgeType(stat))

        edge_type = GetEdgeType(stat)
        if edge_type == 'left':
            data = stat.data
            fit_line = stat.LineOfBestFit
        elif edge_type == 'right':
            #flip up-down - because of numpy's axis weirdness
            data = np.flipud(stat.data)
            fit_line = TrackFitting.FitStraightLine(data)
        elif edge_type == 'top':
            #rotate 90 degrees counter clockwise
            data = np.rot90(stat.data,1)
            fit_line = TrackFitting.FitStraightLine(data)
        elif edge_type == 'bottom':
            #rotate 90 degrees counter clockwise 3 times
            data = np.rot90(stat.data,3) #[1:,]
            fit_line = TrackFitting.FitStraightLine(data)
        else:
            print "This should never happen"
            exit()

#         TV.TrackToFile_ROOT_2D_3D(stat.data, OUTPUT_PATH + 'tracks/left/raw' + str(i) + '.png', legend_text=legend_text, fitline=stat.LineOfBestFit )
#         TV.TrackToFile_ROOT_2D_3D(data, OUTPUT_PATH + 'tracks/' + str(i) + '.png', legend_text=legend_text, fitline=fit_line )
        
        cols, rows = data.shape
        
        CoMs = np.zeros(cols, dtype = 'f8')
        predicted_CoMs = np.zeros(cols, dtype = 'f8')
        flip_track = False
        
        # skip tracks that have been grown out to the edge but don't really touch the edge
        edge_row_flux = (data[0,:].sum(dtype = 'f8'))
#         edge_row_flux = max(data[0,:])
#         print edge_row_flux
        first_col_flux_list.append(edge_row_flux)
        if edge_row_flux < 100: continue # value of 100 was picked with historgramming, i.e. not an arbitrary cut
        
        #flip the deviation if necessary
        if fit_line.a < 0:
            flip_track = 1.
        else:
            flip_track = -1.
            
        
        for col_num in range(cols):
            #calculate Center of Mass of column
            col = data[col_num,:] #get column
            for pix_num in range(len(col)): #loop over pixels in column
                CoMs[col_num] += col[pix_num] * (pix_num + 0.5) #CoM summing, account for center of pixel location
            CoMs[col_num] /= col.sum() # calc CoM

            #calc deviation as function of edge distance using track fit
            predicted_CoMs[col_num] = fit_line.a*(col_num + 0.5) + fit_line.b 
            deviation = predicted_CoMs[col_num] - CoMs[col_num]
            deviation *= flip_track
            
            if abs(deviation) < dev_max: #cut outliers
                if col_num < max_distance: #discard if out of ROI
                    deviations[col_num] += deviation    # sum
                    point_counter[col_num] += 1         # increment number of points at this distance
            
            #TODO: need to:
            #            a) weight by angle
            #            b) flip for positive/negative slopes? - think about this




        #end file loop
    
    for i in range(max_distance):
        gr_left.SetPoint(i, i + 0.5, deviations[i]/point_counter[i])

    print point_counter
    
    gr_left.GetXaxis().SetTitle('Distance from sensor edge (pixels)')
    gr_left.GetYaxis().SetTitle('Charge centroid distance from track (pixels)')
    gr_left.SetMarkerStyle(2)
    gr_left.SetMarkerSize(1)
    
    gr_left.GetXaxis().SetRangeUser(0.,max_distance)
    gr_left.GetYaxis().SetRangeUser(-4,4)

    zero_line = TF1("line","0", 0,max_distance)
    zero_line.SetLineStyle(7)
    zero_line.SetLineWidth(1)

    gr_left.Draw('AP')
    zero_line.Draw("same")
    
    c1.SaveAs(OUTPUT_PATH + 'tracks/left/deviation.png')
    
    
    
    ListToHist(first_col_flux_list, OUTPUT_PATH + 'first_col.pdf', nbins = 20, histmin = -20, histmax = 1500)

############## END CODE ##############
    
    all_time = time.time() - start_time
    for line in GLOBAL_OUT:
        print line
#     print "All analysis done in %.2f seconds" %all_time 
    exit()
    
############# DONE ################
    
