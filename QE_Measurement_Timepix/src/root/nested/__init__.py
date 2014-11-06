import os
from os.path import expanduser, join
from os import listdir
import numpy as np
import string        
               
from ROOT import TCanvas, TF1, TH1F, TGraph
from root_functions import GetFirstBinBelowX, DoubleGausFit, LanGausFit, LandauFit
from my_functions import GetXYTarray_SingleFile
from math import floor


OUTPUT_PATH = "/home/mmmerlin/output/"
FILE_TYPE = ".pdf"



def S_curve_single_pixel():
      
    home_dir  = expanduser('~')
    path = home_dir + '/Desktop/VMShared/Data/QE/635nm/Pixel1/'
    
    
    #########################
    c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    dirs = listdir(path)
    
    voltages = []
    frequencies = []
    
#### pixel 1
    pixel_x = 86
    pixel_y = 110

#### pixel 2
#    pixel_x = 125
#    pixel_y = 110

#### pixel 3
#    pixel_x = 125
#    pixel_y = 132

    boxsize = 8/2 # Must be even, goes in both directions from pixel
    glitch_threshold = 10
    N_glitches = 0
    
    for dir in dirs:
#        if dir <> '5.0mV': print "skipping", str(dir); continue
        
        thisdir = join(path, dir)
        files = listdir(thisdir)
        print "Dir = %s"%dir
        
        N_goodframes = 0
        N_pix_hits = 0
        
        voltages.append(float(dir[0:3])) # what is up with using 2, weird bug?
        print "Analysing voltage %s" %dir
        
        for file in files:
            xs, ys, ts = GetXYTarray_SingleFile(join(thisdir,file), pixel_x-boxsize, pixel_x + boxsize, pixel_y - boxsize, pixel_y + boxsize)
            assert len(xs) == len(ys) == len(ts)
            if len(xs) >= glitch_threshold: print "skipped glitch frame"; N_glitches +=1; continue
            N_goodframes += 1
            N_pix_hits += len(ts)
            
        freq = float(N_pix_hits) / float(N_goodframes)
        frequencies.append(freq)
        
        # next dir (i.e. voltage)
    
    
    Scurve_graph = TGraph(len(dirs),np.asarray(voltages),np.asarray(frequencies))

        
    Scurve_graph.Draw("AP")
    Scurve_graph.SetTitle("")
    Scurve_graph.SetMarkerStyle(2)
    Scurve_graph.SetMarkerSize(1.2)
    Scurve_graph.GetXaxis().SetTitle('Voltage (V)')
    Scurve_graph.GetYaxis().SetTitle('Avg # pixels on per frame')
    
    c1.SaveAs(OUTPUT_PATH + "QE_S_curve_pixel_1" + FILE_TYPE)

    print "# glitches in %s = %s"%(path, N_glitches)
    
    return



def Average_ToT_Dir(path, center_x, center_y, boxsize_over_2):
    from ROOT import TCanvas, TH2F
    c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    
    glitch_threshold = floor(0.75 * (boxsize_over_2 *2)**2) #75% box fill
    N_glitches = 0
    mask_above = 100
    
    N_goodframes = 0
    N_pix_hits = 0
    
    nx, ny = 256,256
    image_hist = TH2F('', '',nx,0,255,ny, 0, 255)
    
    files = os.listdir(path)
    
    for file in files:
        if str(file).count('.txt')<1: continue
        xs, ys, ts = GetXYTarray_SingleFile(path + file, center_x - boxsize_over_2, center_x + boxsize_over_2, center_y - boxsize_over_2, center_y + boxsize_over_2)
        assert len(xs) == len(ys) == len(ts)
        if len(xs) >= glitch_threshold: print "skipped glitch frame"; N_glitches +=1; continue
        
        N_goodframes += 1
        N_pix_hits += len(ts)
        for i in range(len(xs)):
            value = float(ts[i])/50
            if value > mask_above: value = 0
            image_hist.Fill(float(xs[i]),float(ys[i]),value)
            

    image_hist.GetXaxis().SetTitle('x')
    image_hist.GetYaxis().SetTitle('y')
    image_hist.GetZaxis().SetTitle('ToT (us)')
    image_hist.GetXaxis().SetRangeUser(center_x - boxsize_over_2, center_x + boxsize_over_2)
    image_hist.GetYaxis().SetRangeUser(center_y - boxsize_over_2, center_y + boxsize_over_2)
    image_hist.Draw("lego2 0 z") #box, lego, colz, lego2 0
    image_hist.SetStats(False)
    c1.SaveAs(path + "total_ToT.pdf")

    image_hist.Scale(1/float(N_goodframes))
    c1.SaveAs(path + 'averaged_ToT.pdf')
    del c1

    print "# glitches removed from averaging in %s = %s"%(path, N_glitches)
    return image_hist









if __name__ == '__main__':
    print "Running QE analysis\n "
    
    home_dir  = expanduser('~')
#    path = home_dir + '/Desktop/VMShared/Data/QE/Disc Method/465nm/V_sweep/'
    path     = home_dir + '/Desktop/VMShared/Data/QE/Disc Method/465nm/V_sweep/'
    tot_path = home_dir + '/Desktop/VMShared/Data/QE/Disc Method/465nm/ToT before/'
    
    
    
    
    #########################
    c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    
    voltages = []
    frequencies = []
    
#### 627nm & 465nm
    pixel_x = 150
    pixel_y = 92


    boxsize = 30/2 # Must be even, goes in both directions from pixel
    glitch_threshold = 250
    N_glitches = 0
    
    dirs = listdir(path)
    tot_dirs = listdir(tot_path)
    for tot_dir in tot_dirs:
        dummy = Average_ToT_Dir(tot_path + tot_dir + '/', pixel_x, pixel_y, boxsize)
        del dummy
    exit()
    
    
    for dir in dirs:
#        if dir <> '8.7': print "skipping", str(dir); continue
        
        thisdir = join(path, dir)
        files = listdir(thisdir)
        print "Dir = %s"%dir
        
        N_goodframes = 0
        N_pix_hits = 0
        
        voltage = float(dir[0:3])
        voltages.append(voltage) # what is up with using 2, weird bug?
        print "Analysing voltage %s" %dir
        
        weighting_hist = Average_ToT_Dir(path + dir + '/', pixel_x, pixel_y, boxsize)
        
        
        templist = []
        for file in files:
            xs, ys, ts = GetXYTarray_SingleFile(join(thisdir,file), pixel_x-boxsize, pixel_x + boxsize, pixel_y - boxsize, pixel_y + boxsize)
            assert len(xs) == len(ys) == len(ts)
            if len(xs) >= glitch_threshold: print "skipped glitch frame"; N_glitches +=1; continue
            N_goodframes += 1
            N_pix_hits += len(ts)
            
#            templist.append(len(ts))
            
        freq = float(N_pix_hits) / float(N_goodframes)
        frequencies.append(freq)
        
        print "x,y = %s"%(weighting_hist.GetBinContent(pixel_x,pixel_y))
        
        del weighting_hist
        
        # next dir (i.e. voltage)
    
#    from root_functions import ListToHist
#    ListToHist(templist, path + "ts_hist.pdf", nbins = 300, histmin = 0, histmax = 300)
#    exit()
    
    Scurve_graph = TGraph(len(dirs),np.asarray(voltages),np.asarray(frequencies))

        
    Scurve_graph.Draw("AP")
    Scurve_graph.SetTitle("")
    Scurve_graph.SetMarkerStyle(2)
    Scurve_graph.SetMarkerSize(1.2)
    Scurve_graph.GetXaxis().SetTitle('Voltage (V)')
    Scurve_graph.GetYaxis().SetTitle('Avg # pixels on per frame')
    
    c1.SaveAs(OUTPUT_PATH + "QE_465nm_disc" + FILE_TYPE)

    print "# glitches in %s = %s"%(path, N_glitches)
    
    
   
    
    
    
    
    
    
    
    
    
    
    print '\n***End code***'      