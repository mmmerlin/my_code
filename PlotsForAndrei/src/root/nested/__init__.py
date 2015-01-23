import os
from mpl_toolkits.mplot3d import Axes3D

import pylab as pl
import numpy as np
from numpy import dtype

from my_functions import *
import lsst.afw.display.ds9 as ds9

from root_functions import *
from ROOT import TCanvas, TH1F



# input_path = '/mnt/hgfs/VMShared/Data/timepix_fe55/Timepix/timepix 400hz 330 thr 250us window 1/'

input_path = '/mnt/hgfs/VMShared/Data/NSLS/threshold_scan/'
thresholds = [0,5,50,100,160,215,225,235,245,255,265,275,285,295,305,315,325]


if __name__ == '__main__':
    print "Making plots for Andrei..."

#     in_file = open('/mnt/hgfs/VMShared/output/NSLS/post-all.txt','r')

    data = np.loadtxt('/mnt/hgfs/VMShared/output/NSLS/post_all.txt')
    print data[0]

    ts = data[:,0]
    ys = data[:,1]
    
    t = []
    y= []
    for i in range(len(ts)):
        t.append(ts[i] * 0.02 )
        y.append(ys[i])


    from root_functions import ListVsList
    c1 = TCanvas( 'canvas2', 'canvas2', 500, 200, 700, 500 ) #create canvas
    
    graph = ListVsList(t , y, '', xmin = 0, ymin =0.0, ymax = 0.35, marker_color = 1, xtitle = '#Deltat (#mus)', ytitle = 'g_{2}', xmax = 250*0.02) # xmax = 250*0.02
    graph.Draw('AL')
    c1.SetLogx()
    c1.SaveAs('/mnt/hgfs/VMShared/output/NSLS/6.pdf')
    exit()





    av_codes_list = []
    
    hists = []
    
#     hists.append(TH1F('', '',10,0,10)) #0
#     hists.append(TH1F('', '',10,0,10))#5
#     hists.append(TH1F('', '',10,0,10))#50
#     hists.append(TH1F('', '',20,0,20))#100
#     hists.append(TH1F('', '',20,0,150))#160
#     hists.append(TH1F('', '',20,0,150))#215
#     hists.append(TH1F('', '',20,0,150))#225
#     hists.append(TH1F('', '',20,0,150))#235
#     hists.append(TH1F('', '',20,0,150))#245
#     hists.append(TH1F('', '',20,0,150))#255
#     hists.append(TH1F('', '',20,0,150))#265
#     hists.append(TH1F('', '',20,0,500))#275
#     hists.append(TH1F('', '',20,0,500))#285
# #     hists.append(TH1F('', '',20,1000,2000))#295
# #     hists.append(TH1F('', '',20,2500,4000))#305
# #     hists.append(TH1F('', '',20,4500,6000))#315
# #     hists.append(TH1F('', '',20,6000,7500))#325
#     hists.append(TH1F('', '',20,0,2000))#295
#     hists.append(TH1F('', '',20,0,4000))#305
#     hists.append(TH1F('', '',20,0,6000))#315
#     hists.append(TH1F('', '',20,0,7500))#325
    
    for i in range(17):
        hists.append(TH1F('', '',100,0,7500))#325
        
    

    for i,thr in enumerate(thresholds):
        ncodes = 0.
        sum = 0.

        files = os.listdir(input_path + str(thr))
        for file in files:
            ncodes = len(GetRawTimecodes_SingleFile(input_path + str(thr) + '/' + file))
            hists[i].Fill(ncodes)
            sum += ncodes
        
        av_codes_list.append(sum / float(len(files)))
    
    print thresholds
    print av_codes_list
#     exit()
    
    
    
    ListVsList(thresholds, av_codes_list, '/mnt/hgfs/VMShared/temp/NSLS_hits_vs_thr.pdf', setlogy = False, ytitle = 'Av. # hits/frame', xtitle = 'Threshold value')
    ListVsList(thresholds, av_codes_list, '/mnt/hgfs/VMShared/temp/NSLS_hits_vs_thr_logy.pdf', setlogy = True, ytitle = 'Av. # hits/frame', xtitle = 'Threshold value')


    for i,thr in enumerate(thresholds):
        c2 = TCanvas( 'canvas2', 'canvas2', 500, 200, 700, 500 ) #create canvas
        hists[i].Draw()
        hists[i].SetTitle('Thr ' + str(thr))
        hists[i].GetXaxis().SetTitle('# Hit pixels')
        hists[i].GetYaxis().SetTitle('Frequency')
        c2.SaveAs('/mnt/hgfs/VMShared/temp/thr_' + str(thr)+'.png')
        
        
    c3 = TCanvas( 'canvas3', 'canvas3', 500, 200, 700, 500 ) #create canvas
    hist_dummy = TH1F('', '',100,10,7500)
#     for i in range(100):
#         hist_dummy.Fill(0)
#         hist_dummy.Fill(7000)
     
     
#     hist_dummy.Draw('A')
    hist_dummy.GetXaxis().SetTitle('# Hit pixels')
    hist_dummy.GetYaxis().SetTitle('Frequency')

    hist_dummy.SetMaximum(100)
    hist_dummy.Draw("")
    
    for i in range(17):
        hists[i].SetLineColor(i)
        hists[i].Draw("same")
        
    c3.SetLogx()
    c3.SaveAs('/mnt/hgfs/VMShared/temp/master_hist.pdf')


#             exit()
        
#             image = TimepixToExposure(input_path + str(thr) + '/' + file, 1, 254, 1, 254)
#             ds9.mtv(image)
#             exit()



    exit()
    
    
    files = os.listdir(input_path)
        
    for file in files[2:]:
        image = TimepixToExposure(input_path + file, 1, 254, 1, 254)
        ds9.mtv(image)
        exit()

     
     

    print '\n***End code***'







